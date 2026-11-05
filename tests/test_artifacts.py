import pytest
import numpy as np
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.loaders import (
    load_risk_model,
    load_knowledge_base,
    load_rl_recommendation,
    load_safety_rules,
    load_all_artifacts,
    ModelLoadError,
    RiskModelArtifacts,
    KnowledgeBaseArtifacts,
    RLRecommendationArtifacts,
    SafetyRulesArtifacts,
)


def test_load_risk_model_and_inference():
    """Kiểm tra nạp mô hình ONNX, bộ chuẩn hóa scaler và chạy suy luận mẫu."""
    model_bundle = load_risk_model()
    assert isinstance(model_bundle, RiskModelArtifacts)
    assert model_bundle.threshold == 0.87
    
    # 1. Mẫu bệnh nhân âm tính (nguy cơ thấp)
    sample_negative = {
        "age": 25.0,
        "bmi": 21.0,
        "hbA1c_level": 5.0,
        "blood_glucose_level": 90.0,
        "gender": "Female",
        "smoking_history": "never",
        "hypertension": 0,
        "heart_disease": 0,
        "race:Asian": 1
    }
    prob_neg, label_neg = model_bundle.predict_proba(sample_negative)
    assert 0.0 <= prob_neg <= 1.0
    assert label_neg == 0
    assert prob_neg < model_bundle.threshold

    # 2. Mẫu bệnh nhân dương tính (nguy cơ rất cao)
    sample_positive = {
        "age": 64.0,
        "bmi": 49.27,
        "hbA1c_level": 8.2,
        "blood_glucose_level": 140.0,
        "gender": "Female",
        "smoking_history": "current",
        "hypertension": 1,
        "heart_disease": 1,
        "race:Asian": 1
    }
    prob_pos, label_pos = model_bundle.predict_proba(sample_positive)
    assert 0.0 <= prob_pos <= 1.0
    assert label_pos == 1
    assert prob_pos >= model_bundle.threshold


def test_load_knowledge_base_and_retrieval():
    """Kiểm tra nạp Vector Index, mô hình embedding và truy xuất có metadata nguồn."""
    kb_bundle = load_knowledge_base()
    assert isinstance(kb_bundle, KnowledgeBaseArtifacts)
    assert len(kb_bundle.metadata) == 24  # Config_B_Balanced có đúng 24 đoạn
    assert kb_bundle.config.get("selected_chunk_config") == "Config_B_Balanced"
    assert kb_bundle.config.get("embedding_dimension") == 384

    # Thực hiện truy xuất câu hỏi y khoa lâm sàng mẫu
    query = "Xử trí cấp cứu hạ đường huyết bằng quy tắc 15-15 như thế nào?"
    results = kb_bundle.retrieve(query, top_k=3)
    
    assert len(results) == 3
    for r in results:
        assert "rank" in r
        assert "similarity_score" in r
        assert "source_file" in r
        assert "doc_id" in r
        assert "section_or_page" in r
        assert "text" in r
        assert len(r["text"]) > 0

    # Đoạn top-1 phải trích từ tài liệu hạ đường huyết NIDDK
    top1 = results[0]
    assert "NIDDK" in top1["doc_id"] or "HYPOGLYCEMIA" in top1["source_file"].upper()
    assert top1["similarity_score"] > 0.40


def test_load_rl_recommendation_and_discretization():
    """Kiểm tra nạp Q-Table, policy và tính toàn vẹn với discretization.json."""
    rl_bundle = load_rl_recommendation()
    assert isinstance(rl_bundle, RLRecommendationArtifacts)
    
    # Kích thước phải khớp chính xác 24 trạng thái x 12 hành động
    assert rl_bundle.q_table.shape == (24, 12)
    assert rl_bundle.policy.shape == (24,)
    
    # Chính sách tối ưu phải bằng argmax của Q-table
    computed_policy = np.argmax(rl_bundle.q_table, axis=1)
    np.testing.assert_array_equal(rl_bundle.policy, computed_policy)

    # Kiểm tra hàm rời rạc hóa trạng thái (discretize_state)
    # Đường huyết 65 mg/dL (<70, bin 0), Buổi Sáng (bin 0) -> state_id = 0*4 + 0 = 0
    s0 = rl_bundle.discretize_state(65.0, 0)
    assert s0 == 0
    
    # Đường huyết 120 mg/dL (100-140, bin 2), Buổi Trưa (bin 1) -> state_id = 2*4 + 1 = 9
    s9 = rl_bundle.discretize_state(120.0, 1)
    assert s9 == 9

    # Kiểm tra hàm khuyến nghị lối sống
    rec = rl_bundle.recommend(glucose_mg_dl=120.0, time_bin=1)
    assert rec["state_id"] == 9
    assert 0 <= rec["action_id"] < 12
    assert "carb" in rec["details"]
    assert "exercise" in rec["details"]
    assert "remind" in rec["details"]


def test_load_safety_rules():
    """Kiểm tra nạp tập luật an toàn lâm sàng từ rules.yaml."""
    safety_bundle = load_safety_rules()
    assert isinstance(safety_bundle, SafetyRulesArtifacts)
    assert len(safety_bundle.rules) >= 6
    
    # Kiểm tra chốt chặn an toàn: Đường huyết hạ (< 70) nhưng vận động MODERATE -> Vi phạm RULE_01
    bad_hypo_action = {"carb": "LOW", "exercise": "MODERATE", "remind": False}
    is_safe, violations = safety_bundle.check_safety(glucose_mg_dl=60.0, action=bad_hypo_action)
    assert not is_safe
    assert any("RULE_01_HYPO_NO_EXERCISE" in v for v in violations)
    assert any("RULE_05_MANDATORY_MONITORING" in v for v in violations)

    # Kiểm tra hành động an toàn khi đường huyết ổn định (120 mg/dL)
    safe_action = {"carb": "MODERATE", "exercise": "MODERATE", "remind": False}
    is_safe_ok, violations_ok = safety_bundle.check_safety(glucose_mg_dl=120.0, action=safe_action)
    assert is_safe_ok
    assert len(violations_ok) == 0


def test_load_all_artifacts_container():
    """Kiểm tra nạp đồng bộ toàn bộ 4 mô hình."""
    container = load_all_artifacts()
    assert container.is_ready is True
    assert container.risk_model is not None
    assert container.kb is not None
    assert container.rl is not None
    assert container.safety is not None


def test_missing_file_raises_model_load_error(monkeypatch):
    """Kiểm tra khi thiếu file thì ném ModelLoadError để API trả mã lỗi 503."""
    fake_path = Path("models/non_existent_model.onnx")
    monkeypatch.setattr(settings, "ONNX_MODEL_PATH", fake_path)
    
    with pytest.raises(ModelLoadError) as exc_info:
        load_risk_model()
    assert "Thiếu tệp mô hình dự đoán bắt buộc" in str(exc_info.value)
