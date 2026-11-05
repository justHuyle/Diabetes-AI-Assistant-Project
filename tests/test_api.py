import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from backend.app.main import app, app_state, initialize_app_models
from backend.app.core.config import settings
from backend.app.core.loaders import ModelLoadError


@pytest.fixture(scope="module")
def client():
    """Fixture khởi tạo TestClient với Lifespan Context Manager."""
    with TestClient(app) as c:
        yield c


# ==============================================================================
# 1. KỊCH BẢN (A): HỎI ĐÁP TRI THỨC Y KHOA THUẦN TÚY
# ==============================================================================

def test_scenario_a_pure_knowledge_query(client):
    """Kịch bản (a): Người bệnh chỉ hỏi về kiến thức (tiêu chuẩn chẩn đoán, HbA1c), không nhập chỉ số."""
    payload = {
        "message": "Tiêu chuẩn chẩn đoán đái tháo đường theo chỉ số HbA1c và đường huyết lúc đói là bao nhiêu?",
        "metrics": {}
    }
    response = client.post("/api/consult", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["intent"] == "knowledge_query"
    assert data["status"] == "PASS"
    assert data["emergency_detected"] is False
    assert data["knowledge_response"] is not None
    assert len(data["knowledge_response"]["evidence"]) > 0
    # Phải có trích dẫn nguồn văn bản y khoa
    assert "ada" in data["knowledge_response"]["content"]["primary_source"].lower() or "diagnosis" in data["knowledge_response"]["content"]["primary_source"].lower()
    # Khi không có chỉ số thì không gọi đề xuất và dự đoán
    assert data["recommendation_response"] is None
    assert data["prediction_response"] is None
    # Ghi nhận vết
    assert "KnowledgeAgent" in data["trace"]["agents_called"]
    assert "SafetyAgent" in data["trace"]["agents_called"]


# ==============================================================================
# 2. KỊCH BẢN (B): NHẬP CHỈ SỐ SỨC KHỎE, DỰ ĐOÁN NGUY CƠ, ĐỀ XUẤT LỐI SỐNG
# ==============================================================================

def test_scenario_b_clinical_consultation(client):
    """Kịch bản (b): Bệnh nhân cung cấp chỉ số lâm sàng để nhận dự báo rủi ro và tư vấn lối sống."""
    payload = {
        "message": "Tôi 45 tuổi, vừa đi khám định kỳ, nhờ bác sĩ tư vấn kết quả này",
        "metrics": {
            "age": 45.0,
            "bmi": 26.5,
            "hbA1c_level": 6.1,
            "blood_glucose_level": 115.0,
            "gender": "Male",
            "smoking_history": "never",
            "hypertension": 0,
            "heart_disease": 0
        },
        "glucose_unit": "mg/dL",
        "time_of_day": "Trưa"
    }
    response = client.post("/api/consult", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["intent"] == "clinical_consultation"
    assert data["status"] == "PASS"
    # Phải có phản hồi dự đoán từ mô hình ONNX
    assert data["prediction_response"] is not None
    pred_c = data["prediction_response"]["content"]
    assert "risk_probability" in pred_c
    assert pred_c["decision_threshold"] == 0.87
    # Phải có phản hồi đề xuất lối sống từ Q-Table
    assert data["recommendation_response"] is not None
    rec_c = data["recommendation_response"]["content"]
    assert "lifestyle_plan" in rec_c
    assert rec_c["lifestyle_plan"]["nutrition"]["level"] in ["LOW", "MODERATE", "HIGH"]
    assert rec_c["lifestyle_plan"]["exercise"]["level"] in ["NONE", "MODERATE"]
    # Kiểm tra an toàn
    assert data["safety_review"]["status"] == "PASS"
    # Đủ cả 4 agent trong vết thực thi
    assert "PredictionAgent" in data["trace"]["agents_called"]
    assert "RecommendationAgent" in data["trace"]["agents_called"]
    assert "SafetyAgent" in data["trace"]["agents_called"]


# ==============================================================================
# 3. KỊCH BẢN (C): PHÁT HIỆN CHỈ SỐ NGUY HIỂM VÀ KÍCH HOẠT CẢNH BÁO KHẨN CẤP
# ==============================================================================

def test_scenario_c_emergency_hypoglycemia_short_circuit(client):
    """Kịch bản (c1): Đường huyết hạ nguy hiểm (<70 mg/dL), cảnh báo cấp cứu đi trước."""
    payload = {
        "message": "Tôi thấy run chân tay, đói cồn cào và vã mồ hôi lạnh",
        "metrics": {
            "blood_glucose_level": 55.0,
            "glucose_unit": "mg/dL"
        }
    }
    response = client.post("/api/consult", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["intent"] == "emergency"
    assert data["emergency_detected"] is True
    assert data["status"] == "VETO"
    assert "HẠ ĐƯỜNG HUYẾT NGUY HIỂM" in data["emergency_alert"]
    # Tóm tắt phải đưa cảnh báo khẩn cấp lên đầu tiên
    assert data["summary"].startswith("🚨 [CẢNH BÁO KHẨN CẤP]")
    # Vận động phải bị ép về NONE
    if data["recommendation_response"]:
        plan = data["recommendation_response"]["content"]["lifestyle_plan"]
        assert plan["exercise"]["level"] == "NONE"


def test_scenario_c_emergency_hyperglycemia_mmol(client):
    """Kịch bản (c2): Đường huyết tăng rất cao (>14.0 mmol/L tương đương >250 mg/dL), cảnh báo toan ceton."""
    payload = {
        "message": "Tôi cảm thấy khát nước liên tục, tiểu nhiều và mệt lả",
        "metrics": {
            "blood_glucose_level": 16.0,  # 16 mmol/L = 288.3 mg/dL > 250
            "glucose_unit": "mmol/L"
        }
    }
    response = client.post("/api/consult", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["intent"] == "emergency"
    assert data["emergency_detected"] is True
    assert data["status"] == "VETO"
    assert "TĂNG ĐƯỜNG HUYẾT RẤT CAO" in data["emergency_alert"]
    assert "toan ceton" in data["emergency_alert"].lower()


# ==============================================================================
# 4. CA NGOÀI PHẠM VI (KÊ ĐƠN THUỐC / LIỀU LƯỢNG INSULIN)
# ==============================================================================

def test_scenario_out_of_scope_prescription_request(client):
    """Ca ngoài phạm vi: Người bệnh yêu cầu kê đơn hoặc chỉnh liều thuốc -> từ chối lịch sự và hướng tới bác sĩ."""
    payload = {
        "message": "Bác sĩ kê đơn cho tôi liều Metformin và chỉnh liều tiêm insulin bao nhiêu đơn vị?",
        "metrics": {}
    }
    response = client.post("/api/consult", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["intent"] == "out_of_scope"
    assert data["status"] == "VETO"
    assert "RULE_06_NO_MEDICATION_IN_RL" in data["safety_review"]["triggered_rules"]
    assert "TUYỆT ĐỐI TỪ CHỐI KÊ ĐƠN" in data["summary"] or "LƯU Ý AN TOÀN Y TẾ" in data["summary"]
    assert "bác sĩ chuyên khoa" in data["summary"].lower()


# ==============================================================================
# 5. KIỂM TRA THỨ TỰ ƯU TIÊN XUNG ĐỘT (Safety > Knowledge > Recommendation > Prediction)
# ==============================================================================

def test_conflict_priority_safety_overrides_recommendation(client):
    """Kiểm tra độ ưu tiên: Khi có xung đột giữa RL và Quy tắc an toàn, SafetyAgent luôn phủ quyết/chỉnh sửa.
    
    1. Ca dinh dưỡng (RULE_04): Đường huyết 75.0 mg/dL (< 80), RL đề xuất LOW carb.
       SafetyAgent can thiệp nâng lên MODERATE carb vì cắt kiệt tinh bột khi đường huyết thấp là nguy hiểm.
    2. Ca vận động (RULE_02): Đường huyết 260.0 mg/dL (> 250), RL buổi chiều đề xuất MODERATE exercise.
       SafetyAgent can thiệp hạ về NONE vì nguy cơ toan ceton DKA.
    """
    # 1. Ca xung đột dinh dưỡng RULE_04
    payload_nutrition = {
        "message": "Tư vấn chế độ ăn cho tôi",
        "metrics": {
            "blood_glucose_level": 75.0,  # < 80 mg/dL
            "glucose_unit": "mg/dL"
        }
    }
    resp1 = client.post("/api/consult", json=payload_nutrition)
    assert resp1.status_code == 200
    data1 = resp1.json()

    assert "RULE_04_HYPO_REQUIRE_CARB" in data1["safety_review"]["triggered_rules"]
    assert data1["safety_review"]["status"] == "MODIFY"
    nutri_plan = data1["recommendation_response"]["content"]["lifestyle_plan"]["nutrition"]
    assert nutri_plan["level"] == "MODERATE"
    assert "agent an toàn hiệu chỉnh" in nutri_plan["label"].lower()

    # 2. Ca xung đột vận động RULE_02
    payload_exercise = {
        "message": "Tư vấn chế độ tập buổi chiều",
        "metrics": {
            "blood_glucose_level": 260.0,  # > 250 mg/dL
            "glucose_unit": "mg/dL",
            "time_of_day": "afternoon"
        }
    }
    resp2 = client.post("/api/consult", json=payload_exercise)
    assert resp2.status_code == 200
    data2 = resp2.json()

    assert any("RULE_02" in r for r in data2["safety_review"]["triggered_rules"])
    ex_plan = data2["recommendation_response"]["content"]["lifestyle_plan"]["exercise"]
    assert ex_plan["level"] == "NONE"
    assert "tạm nghỉ thể lực" in ex_plan["label"].lower()


# ==============================================================================
# 6. KIỂM TRA CÁC ENDPOINTS PHỤ & TRƯỜNG HỢP THIẾU MODEL
# ==============================================================================

def test_api_predict_valid_and_invalid(client):
    """Kiểm tra endpoint POST /api/predict hoạt động chuẩn và trả 422 khi thiếu dữ liệu."""
    valid_payload = {
        "age": 50.0,
        "bmi": 28.0,
        "hbA1c_level": 6.8,
        "blood_glucose_level": 135.0,
        "gender": "Male",
        "smoking_history": "former",
        "hypertension": 1,
        "heart_disease": 0
    }
    resp = client.post("/api/predict", json=valid_payload)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["status"] == "success"
    assert "risk_probability" in res_data["prediction"]

    # Thiếu trường age
    invalid_payload = {
        "bmi": 28.0,
        "hbA1c_level": 6.8,
        "blood_glucose_level": 135.0,
        "gender": "Male"
    }
    resp_inv = client.post("/api/predict", json=invalid_payload)
    assert resp_inv.status_code == 422


def test_api_rules(client):
    """Kiểm tra endpoint GET /api/rules trả về danh mục 6 luật an toàn."""
    resp = client.get("/api/rules")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["total_rules"] >= 6
    assert "rule_01_hypo_exercise_veto" in data["rules"]


def test_api_health_healthy(client):
    """Kiểm tra endpoint GET /api/health trả 200 khi các model sẵn sàng."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["models"]["risk_model"] == "ready"
    assert data["models"]["knowledge_base"] == "ready"
    assert data["models"]["rl_recommendation"] == "ready"
    assert data["models"]["safety_rules"] == "ready"


def test_api_trace(client):
    """Kiểm tra endpoint GET /api/trace/{id} lưu và trả vết thực thi chính xác."""
    # 1. Gọi consult tạo 1 phiên tư vấn
    resp = client.post("/api/consult", json={"message": "Tiêu chuẩn chẩn đoán ADA"})
    cid = resp.json()["consultation_id"]

    # 2. Truy vấn trace theo ID
    trace_resp = client.get(f"/api/trace/{cid}")
    assert trace_resp.status_code == 200
    t_data = trace_resp.json()
    assert t_data["status"] == "success"
    assert t_data["trace"]["consultation_id"] == cid
    assert len(t_data["trace"]["steps"]) > 0

    # 3. ID không tồn tại trả 404
    fake_resp = client.get("/api/trace/fake-id-123")
    assert fake_resp.status_code == 404


def test_missing_model_returns_503(monkeypatch, client):
    """Kiểm tra khi thiếu model thì hệ thống trả mã lỗi HTTP 503 kèm thông báo minh bạch."""
    # Giả lập thiếu file ONNX
    fake_path = Path("models/missing_risk_model.onnx")
    monkeypatch.setattr(settings, "ONNX_MODEL_PATH", fake_path)
    
    # Đánh dấu uninitialized để ép nạp lại và bắt lỗi
    app_state["coordinator"] = None
    app_state["model_status"]["risk_model"] = "uninitialized"

    resp = client.get("/api/health")
    assert resp.status_code == 503
    data = resp.json()
    assert "Một hoặc nhiều mô hình chưa sẵn sàng" in data["message"]

    resp_consult = client.post("/api/consult", json={"message": "Xin chào"})
    assert resp_consult.status_code == 503
    assert "Dịch vụ chưa sẵn sàng" in resp_consult.json()["error"]
