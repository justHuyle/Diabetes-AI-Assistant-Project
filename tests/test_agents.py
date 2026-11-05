import pytest
from backend.app.agents.prediction_agent import PredictionAgent
from backend.app.agents.knowledge_agent import KnowledgeAgent
from backend.app.agents.recommendation_agent import RecommendationAgent
from backend.app.agents.safety_agent import SafetyAgent, SafetyReviewResult
from backend.app.agents.base import AgentResponse


# ==============================================================================
# 1. KIỂM THỬ PREDICTION AGENT (DEEP LEARNING ONNX)
# ==============================================================================

def test_prediction_agent_valid_cases():
    """Kiểm tra dự đoán chính xác cho ca nguy cơ thấp và ca nguy cơ cao."""
    agent = PredictionAgent()

    # Ca nguy cơ thấp (người trẻ, chỉ số bình thường)
    low_risk_input = {
        "age": 28.0,
        "bmi": 21.5,
        "hbA1c_level": 5.1,
        "blood_glucose_level": 88.0,
        "gender": "Female",
        "smoking_history": "never",
        "hypertension": 0,
        "heart_disease": 0
    }
    resp_low = agent.run(low_risk_input)
    assert resp_low.agent == "PredictionAgent"
    assert resp_low.confidence < 0.87
    assert resp_low.content["predicted_label"] == 0
    assert "Nguy cơ thấp" in resp_low.content["risk_category"]
    assert "PASS" in resp_low.flags

    # Ca nguy cơ cao (cao tuổi, béo phì, HbA1c cao)
    high_risk_input = {
        "age": 64.0,
        "bmi": 49.27,
        "hbA1c_level": 8.2,
        "blood_glucose_level": 140.0,
        "gender": "Female",
        "smoking_history": "current",
        "hypertension": 1,
        "heart_disease": 1
    }
    resp_high = agent.run(high_risk_input)
    assert resp_high.confidence >= 0.87
    assert resp_high.content["predicted_label"] == 1
    assert "Nguy cơ cao" in resp_high.content["risk_category"]
    assert "HIGH_RISK_DETECTED" in resp_high.flags


def test_prediction_agent_missing_fields_error():
    """Kiểm tra báo lỗi chính xác khi thiếu trường bắt buộc (không được tự điền giả)."""
    agent = PredictionAgent()

    # Thiếu age và bmi
    incomplete_input = {
        "hbA1c_level": 6.0,
        "blood_glucose_level": 110.0,
        "gender": "Male"
    }
    resp = agent.run(incomplete_input)
    assert resp.confidence == 0.0
    assert "INVALID_INPUT" in resp.flags
    assert "error" in resp.content
    details = str(resp.content["details"])
    assert "age" in details
    assert "bmi" in details


def test_prediction_agent_out_of_range_error():
    """Kiểm tra báo lỗi khi dữ liệu ngoài khoảng sinh học hợp lệ."""
    agent = PredictionAgent()

    # Tuổi 150 (>120), BMI 5 (<10), giới tính 'UnknownGender'
    invalid_input = {
        "age": 150.0,
        "bmi": 5.0,
        "hbA1c_level": 5.5,
        "blood_glucose_level": 100.0,
        "gender": "AlienGender",
        "smoking_history": "never"
    }
    resp = agent.run(invalid_input)
    assert "INVALID_INPUT" in resp.flags
    details = str(resp.content["details"])
    assert "age" in details
    assert "bmi" in details
    assert "gender" in details


# ==============================================================================
# 2. KIỂM THỬ KNOWLEDGE AGENT (KB + RAG)
# ==============================================================================

def test_knowledge_agent_relevant_query():
    """Kiểm tra truy xuất câu hỏi đúng phạm vi trả về trích dẫn nguồn chuẩn."""
    agent = KnowledgeAgent()
    req = {"query": "Tiêu chuẩn chẩn đoán đái tháo đường theo chỉ số HbA1c là gì?", "top_k": 3}
    resp = agent.run(req)

    assert resp.agent == "KnowledgeAgent"
    assert resp.confidence > 0.40
    assert "PASS" in resp.flags
    assert len(resp.evidence) > 0
    # Phải có trích dẫn nguồn văn bản
    top_source = resp.content["primary_source"]
    assert "ada" in top_source.lower() or "diagnosis" in top_source.lower()
    assert "citations" in resp.content


def test_knowledge_agent_refuses_out_of_scope():
    """Kiểm tra KnowledgeAgent từ chối trả lời khi câu hỏi nằm ngoài phạm vi y khoa (không bịa)."""
    agent = KnowledgeAgent()
    out_of_scope_req = {"query": "Hướng dẫn cấu hình mạng Kubernetes cluster trên máy chủ Linux Ubuntu?", "top_k": 3}
    resp = agent.run(out_of_scope_req)

    assert "OUT_OF_SCOPE" in resp.flags
    assert "REFUSED_GROUNDING" in resp.flags
    assert "Không đủ căn cứ y khoa" in resp.content["message"]
    assert resp.confidence < agent.similarity_threshold


def test_knowledge_agent_empty_query():
    """Kiểm tra xử lý lỗi khi câu hỏi rỗng."""
    agent = KnowledgeAgent()
    resp = agent.run({"query": "   "})
    assert "EMPTY_QUERY" in resp.flags
    assert "error" in resp.content


# ==============================================================================
# 3. KIỂM THỬ RECOMMENDATION AGENT (RL LIFESTYLE)
# ==============================================================================

def test_recommendation_agent_valid_lifestyle():
    """Kiểm tra ánh xạ trạng thái và đề xuất lối sống theo chính sách Q-Table."""
    agent = RecommendationAgent()

    # Đường huyết 120 mg/dL (khoảng an toàn), buổi sáng (time_bin 0)
    req = {"blood_glucose_level": 120.0, "time_bin": 0}
    resp = agent.run(req)

    assert resp.agent == "RecommendationAgent"
    assert "PASS" in resp.flags
    assert "lifestyle_plan" in resp.content
    plan = resp.content["lifestyle_plan"]
    assert "nutrition" in plan
    assert "exercise" in plan
    assert "monitoring" in plan

    # Tuyệt đối không chứa thuốc hay insulin trong hành động
    action_text = str(resp.content).lower()
    for med in ["insulin", "metformin", "tiêm thuốc", "uống thuốc"]:
        assert med not in plan["nutrition"]["level"].lower()
        assert med not in plan["exercise"]["level"].lower()


def test_recommendation_agent_missing_glucose_returns_insufficient_data():
    """Kiểm tra khi không có nồng độ đường huyết thì không bịa, thông báo chưa đủ dữ liệu."""
    agent = RecommendationAgent()
    req = {"query": "Tôi nên tập thể dục thế nào?"}  # Không có blood_glucose_level
    resp = agent.run(req)

    assert "INSUFFICIENT_DATA" in resp.flags
    assert "Chưa đủ dữ liệu để đề xuất" in resp.content["message"]
    assert "blood_glucose_level" in resp.content["missing_fields"]


# ==============================================================================
# 4. KIỂM THỬ SAFETY AGENT (HỆ LUẬT VÀ PHỦ QUYẾT)
# ==============================================================================

def test_safety_rule_01_hypo_no_exercise():
    """RULE_01: Cấm vận động thể lực khi đường huyết dưới 100 mg/dL."""
    safety = SafetyAgent()
    dummy_rl_resp = AgentResponse(
        agent="RecommendationAgent",
        content={
            "lifestyle_plan": {
                "nutrition": {"level": "MODERATE"},
                "exercise": {"level": "MODERATE"},
                "monitoring": {"required": False}
            }
        },
        confidence=0.9
    )
    res = safety.review(
        responses={"recommendation_agent": dummy_rl_resp},
        metrics={"blood_glucose_level": 65.0}  # Đường huyết < 100
    )
    assert "RULE_01_HYPO_NO_EXERCISE" in res.triggered_rules
    assert dummy_rl_resp.content["lifestyle_plan"]["exercise"]["level"] == "NONE"


def test_safety_rule_02_hyper_no_exercise():
    """RULE_02: Cấm tập thể dục cường độ vừa/cao khi đường huyết > 250 mg/dL (nguy cơ toan ceton)."""
    safety = SafetyAgent()
    dummy_rl_resp = AgentResponse(
        agent="RecommendationAgent",
        content={
            "lifestyle_plan": {
                "nutrition": {"level": "LOW"},
                "exercise": {"level": "MODERATE"},
                "monitoring": {"required": True}
            }
        },
        confidence=0.9
    )
    res = safety.review(
        responses={"recommendation_agent": dummy_rl_resp},
        metrics={"blood_glucose_level": 260.0}  # Đường huyết > 250
    )
    assert "RULE_02_HYPER_NO_EXERCISE" in res.triggered_rules
    assert dummy_rl_resp.content["lifestyle_plan"]["exercise"]["level"] == "NONE"


def test_safety_rule_03_hyper_restrict_carb():
    """RULE_03: Khi đường huyết > 180 mg/dL, cấm đề xuất bữa ăn mức tinh bột cao (High Carb)."""
    safety = SafetyAgent()
    dummy_rl_resp = AgentResponse(
        agent="RecommendationAgent",
        content={
            "lifestyle_plan": {
                "nutrition": {"level": "HIGH"},
                "exercise": {"level": "NONE"},
                "monitoring": {"required": False}
            }
        },
        confidence=0.9
    )
    res = safety.review(
        responses={"recommendation_agent": dummy_rl_resp},
        metrics={"blood_glucose_level": 195.0}  # Đường huyết > 180
    )
    assert "RULE_03_HYPER_RESTRICT_CARB" in res.triggered_rules
    assert dummy_rl_resp.content["lifestyle_plan"]["nutrition"]["level"] == "LOW"


def test_safety_rule_04_hypo_require_carb():
    """RULE_04: Khi đường huyết dưới 80 mg/dL, cấm đề xuất bữa ăn cắt kiệt tinh bột (Low Carb)."""
    safety = SafetyAgent()
    dummy_rl_resp = AgentResponse(
        agent="RecommendationAgent",
        content={
            "lifestyle_plan": {
                "nutrition": {"level": "LOW"},
                "exercise": {"level": "NONE"},
                "monitoring": {"required": False}
            }
        },
        confidence=0.9
    )
    res = safety.review(
        responses={"recommendation_agent": dummy_rl_resp},
        metrics={"blood_glucose_level": 75.0}  # Đường huyết < 80
    )
    assert "RULE_04_HYPO_REQUIRE_CARB" in res.triggered_rules
    assert dummy_rl_resp.content["lifestyle_plan"]["nutrition"]["level"] == "MODERATE"


def test_safety_rule_05_mandatory_monitoring():
    """RULE_05: Bắt buộc kích hoạt nhắc đo đường huyết khi rơi vào vùng bất thường (<70 hoặc >250)."""
    safety = SafetyAgent()
    dummy_rl_resp = AgentResponse(
        agent="RecommendationAgent",
        content={
            "lifestyle_plan": {
                "nutrition": {"level": "MODERATE"},
                "exercise": {"level": "NONE"},
                "monitoring": {"required": False}
            }
        },
        confidence=0.9
    )
    res = safety.review(
        responses={"recommendation_agent": dummy_rl_resp},
        metrics={"blood_glucose_level": 60.0}  # < 70
    )
    assert "RULE_05_MANDATORY_MONITORING" in res.triggered_rules
    assert dummy_rl_resp.content["lifestyle_plan"]["monitoring"]["required"] is True


def test_safety_rule_06_veto_medication_request():
    """RULE_06: Phủ quyết tuyệt đối yêu cầu kê đơn thuốc hoặc chỉnh liều insulin."""
    safety = SafetyAgent()
    dummy_kb_resp = AgentResponse(
        agent="KnowledgeAgent",
        content={"answer": "Thông tin về thuốc điều trị."},
        confidence=0.8
    )
    res = safety.review(
        responses={"knowledge_agent": dummy_kb_resp},
        metrics={},
        query="Bác sĩ hãy kê đơn cho tôi liều Metformin và chỉnh liều tiêm insulin bao nhiêu?"
    )
    assert res.status == "VETO"
    assert "RULE_06_NO_MEDICATION_IN_RL" in res.triggered_rules
    assert "TUYỆT ĐỐI TỪ CHỐI KÊ ĐƠN" in dummy_kb_resp.content["answer"]


def test_safety_emergency_short_circuit():
    """Kiểm tra đường rút gọn cấp cứu: Hạ đường huyết < 70 hoặc tăng > 250 cảnh báo đi trước."""
    safety = SafetyAgent()

    # Cấp cứu hạ đường huyết
    res_hypo = safety.review(responses={}, metrics={"blood_glucose_level": 58.0})
    assert res_hypo.emergency_detected is True
    assert res_hypo.status == "VETO"
    assert "HẠ ĐƯỜNG HUYẾT NGUY HIỂM" in res_hypo.emergency_message

    # Cấp cứu tăng đường huyết rất cao
    res_hyper = safety.review(responses={}, metrics={"blood_glucose_level": 290.0})
    assert res_hyper.emergency_detected is True
    assert res_hyper.status == "VETO"
    assert "TĂNG ĐƯỜNG HUYẾT RẤT CAO" in res_hyper.emergency_message
