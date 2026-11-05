import os
import json
import pickle
import numpy as np
import yaml
import onnxruntime as ort
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from sentence_transformers import SentenceTransformer

from backend.app.core.config import settings


class ModelLoadError(Exception):
    """Ngoại lệ khi không thể nạp mô hình hoặc thiếu tệp artifact.
    FastAPI bắt ngoại lệ này để phản hồi mã lỗi HTTP 503 Service Unavailable.
    """
    def __init__(self, message: str, missing_path: Optional[Path] = None):
        super().__init__(message)
        self.message = message
        self.missing_path = missing_path


class HybridVectorIndex:
    """Động cơ truy vấn Vector Index hỗ trợ Cosine Similarity.
    Tương thích tuyệt đối với lớp trong Notebook NB02, hỗ trợ cả FAISS và NumPy fallback.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectors = None
        self.metadata = []
        self.use_faiss = False
        try:
            import faiss
            self.index = faiss.IndexFlatIP(dimension)
            self.use_faiss = True
        except ImportError:
            self.index = None
            self.use_faiss = False

    def add_documents(self, embeddings: np.ndarray, doc_metadata: List[dict]):
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-12
        normalized_embeddings = (embeddings / norms).astype(np.float32)
        self.metadata.extend(doc_metadata)
        if self.vectors is None:
            self.vectors = normalized_embeddings
        else:
            self.vectors = np.vstack([self.vectors, normalized_embeddings])
        if self.use_faiss and self.index is not None:
            self.index.add(normalized_embeddings)

    def search(self, query_vector: np.ndarray, top_k: int = 3) -> List[dict]:
        q_norm = np.linalg.norm(query_vector)
        if q_norm == 0:
            q_norm = 1e-12
        q_norm_vec = (query_vector / q_norm).astype(np.float32).reshape(1, -1)
        
        if self.use_faiss and self.index is not None:
            scores, indices = self.index.search(q_norm_vec, top_k)
            ret_scores = scores[0]
            ret_indices = indices[0]
        else:
            sims = np.dot(self.vectors, q_norm_vec.T).flatten()
            ret_indices = np.argsort(sims)[::-1][:top_k]
            ret_scores = sims[ret_indices]
            
        results = []
        for rank, (idx, score) in enumerate(zip(ret_indices, ret_scores), start=1):
            if 0 <= idx < len(self.metadata):
                item = dict(self.metadata[idx])
                item["rank"] = rank
                item["similarity_score"] = float(score)
                results.append(item)
        return results

    @classmethod
    def load(cls, filepath: Path) -> "HybridVectorIndex":
        if not filepath.exists():
            raise ModelLoadError(f"Không tìm thấy tệp Vector Index: {filepath}", filepath)
        with open(filepath, "rb") as f:
            payload = pickle.load(f)
        inst = cls(dimension=payload["dimension"])
        inst.use_faiss = payload.get("use_faiss", False)
        inst.metadata = payload.get("metadata", [])
        inst.vectors = payload.get("vectors", None)
        if inst.use_faiss and "faiss_bytes" in payload:
            try:
                import faiss
                inst.index = faiss.deserialize_index(payload["faiss_bytes"])
            except Exception:
                inst.use_faiss = False
                inst.index = None
        return inst


class RiskModelArtifacts:
    """Đóng gói mô hình Deep Learning ONNX, scaler và feature schema."""
    def __init__(self, session: ort.InferenceSession, scaler: dict, schema: dict):
        self.session = session
        self.scaler = scaler
        self.schema = schema
        self.threshold = float(schema.get("decision_threshold_f1_optimal", 0.87))
        self.input_name = session.get_inputs()[0].name
        self.output_name = session.get_outputs()[0].name

    def preprocess(self, raw_input: Dict[str, Any]) -> np.ndarray:
        """Tiền xử lý 13 đặc trưng thô thành vector 17 chiều chuẩn hóa."""
        num_features = self.scaler["numerical_features"]
        means = np.array(self.scaler["scaler_mean"], dtype=np.float32)
        scales = np.array(self.scaler["scaler_scale"], dtype=np.float32)
        
        # 1. Chuẩn hóa 4 biến số học qua StandardScaler
        num_vals = []
        for feat in num_features:
            if feat not in raw_input:
                raise ValueError(f"Thiếu trường dữ liệu số học bắt buộc: '{feat}'")
            num_vals.append(float(raw_input[feat]))
        scaled_num = (np.array(num_vals, dtype=np.float32) - means) / scales

        # 2. Mã hóa One-Hot cho gender (drop='Female')
        gender = str(raw_input.get("gender", "")).strip()
        cat_gender_male = 1.0 if gender.lower() == "male" else 0.0

        # 3. Mã hóa One-Hot cho smoking_history (drop='No Info')
        smoking = str(raw_input.get("smoking_history", "")).strip()
        smoking_categories = ["current", "ever", "former", "never", "not current"]
        cat_smoking = [1.0 if smoking == cat else 0.0 for cat in smoking_categories]

        # 4. Trích xuất 7 biến nhị phân
        bin_features = [
            float(raw_input.get("hypertension", 0)),
            float(raw_input.get("heart_disease", 0)),
            float(raw_input.get("race:AfricanAmerican", 0)),
            float(raw_input.get("race:Asian", 1)),  # Mặc định Asian=1 cho bệnh nhân Việt Nam
            float(raw_input.get("race:Caucasian", 0)),
            float(raw_input.get("race:Hispanic", 0)),
            float(raw_input.get("race:Other", 0)),
        ]

        # Ghép thành vector 17 chiều
        vector_17 = np.concatenate([
            scaled_num,
            [cat_gender_male],
            cat_smoking,
            bin_features
        ]).astype(np.float32)

        return vector_17.reshape(1, 17)

    def predict_proba(self, raw_input: Dict[str, Any]) -> Tuple[float, int]:
        """Tính toán xác suất nguy cơ và nhãn nhị phân theo ngưỡng tối ưu."""
        x = self.preprocess(raw_input)
        outputs = self.session.run([self.output_name], {self.input_name: x})
        prob = float(outputs[0][0])
        label = 1 if prob >= self.threshold else 0
        return prob, label


class KnowledgeBaseArtifacts:
    """Đóng gói chỉ mục vector KB, metadata đoạn trích và mô hình embedding."""
    def __init__(self, index: HybridVectorIndex, metadata: List[dict], config: dict, embedder: SentenceTransformer):
        self.index = index
        self.metadata = metadata
        self.config = config
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 3) -> List[dict]:
        """Mã hóa câu hỏi truy vấn và tìm kiếm top-k đoạn văn bản liên quan nhất."""
        query_vec = self.embedder.encode(query, convert_to_numpy=True)
        return self.index.search(query_vec, top_k=top_k)


class RLRecommendationArtifacts:
    """Đóng gói Q-table, bảng chính sách tối ưu và lược đồ rời rạc hóa."""
    def __init__(self, q_table: np.ndarray, policy: np.ndarray, discretization: dict):
        self.q_table = q_table
        self.policy = policy
        self.discretization = discretization
        self.actions = discretization["action_space_definitions"]["actions"]
        self.glucose_bins = discretization["state_space_discretization"]["glucose_bins"]

    def discretize_state(self, glucose_mg_dl: float, time_bin: int) -> int:
        """Ánh xạ nồng độ glucose và khung giờ thành state_id (0..23)."""
        time_bin = max(0, min(3, int(time_bin)))
        glucose_bin = 0
        if glucose_mg_dl < 70.0:
            glucose_bin = 0
        elif glucose_mg_dl < 100.0:
            glucose_bin = 1
        elif glucose_mg_dl <= 140.0:
            glucose_bin = 2
        elif glucose_mg_dl <= 180.0:
            glucose_bin = 3
        elif glucose_mg_dl <= 250.0:
            glucose_bin = 4
        else:
            glucose_bin = 5
        return glucose_bin * 4 + time_bin

    def recommend(self, glucose_mg_dl: float, time_bin: int) -> dict:
        """Tra cứu hành động khuyến nghị lối sống tối ưu từ chính sách pi*(s)."""
        state_id = self.discretize_state(glucose_mg_dl, time_bin)
        action_id = int(self.policy[state_id])
        action_details = next((a for a in self.actions if a["action_id"] == action_id), None)
        return {
            "state_id": state_id,
            "action_id": action_id,
            "details": action_details,
            "q_values": self.q_table[state_id].tolist()
        }


class SafetyRulesArtifacts:
    """Đóng gói các quy tắc an toàn y tế lâm sàng từ rules.yaml."""
    def __init__(self, rules_data: dict):
        self.rules = rules_data.get("safety_rules", {})

    def check_safety(self, glucose_mg_dl: float, action: dict) -> Tuple[bool, List[str]]:
        """Kiểm tra xem hành động lối sống có vi phạm luật an toàn lâm sàng không."""
        violations = []
        carb = action.get("carb", "MODERATE")
        exercise = action.get("exercise", "NONE")
        remind = action.get("remind", False)

        # RULE_01: Cấm vận động khi glucose < 100
        if glucose_mg_dl < 100 and exercise in ["MODERATE", "HIGH"]:
            violations.append("RULE_01_HYPO_NO_EXERCISE: Đường huyết dưới 100 mg/dL, cấm tập thể dục để tránh hạ đường huyết sâu.")

        # RULE_02: Cấm vận động khi glucose > 250
        if glucose_mg_dl > 250 and exercise in ["MODERATE", "HIGH"]:
            violations.append("RULE_02_HYPER_NO_EXERCISE: Đường huyết trên 250 mg/dL, cấm vận động cường độ vừa/cao (nguy cơ toan ceton).")

        # RULE_03: Cấm ăn High Carb khi glucose > 180
        if glucose_mg_dl > 180 and carb == "HIGH":
            violations.append("RULE_03_HYPER_RESTRICT_CARB: Đường huyết cao (>180 mg/dL), cấm khuyến nghị bữa ăn nhiều tinh bột.")

        # RULE_04: Cấm cắt kiệt tinh bột (Low Carb) khi glucose < 80
        if glucose_mg_dl < 80 and carb == "LOW":
            violations.append("RULE_04_HYPO_REQUIRE_CARB: Đường huyết cận hạ (<80 mg/dL), cấm cắt kiệt tinh bột.")

        # RULE_05: Bắt buộc nhắc đo đường huyết khi glucose < 70 hoặc > 250
        if (glucose_mg_dl < 70 or glucose_mg_dl > 250) and not remind:
            violations.append("RULE_05_MANDATORY_MONITORING: Đường huyết ở vùng nguy hiểm, bắt buộc kích hoạt cờ nhắc đo đường huyết.")

        is_safe = len(violations) == 0
        return is_safe, violations


class ModelContainer:
    """Kho chứa duy nhất lưu trữ toàn bộ 4 bộ mô hình đã nạp vào bộ nhớ."""
    def __init__(
        self,
        risk_model: RiskModelArtifacts,
        kb: KnowledgeBaseArtifacts,
        rl: RLRecommendationArtifacts,
        safety: SafetyRulesArtifacts
    ):
        self.risk_model = risk_model
        self.kb = kb
        self.rl = rl
        self.safety = safety
        self.is_ready = True


# ==============================================================================
# HÀM NẠP TỪ Ổ ĐĨA KÈM CƠ CHẾ KIỂM SOÁT LỖI HTTP 503
# ==============================================================================

def load_risk_model() -> RiskModelArtifacts:
    """Nạp mô hình ONNX, scaler và feature schema."""
    onnx_path = settings.ONNX_MODEL_PATH
    scaler_path = settings.SCALER_PATH
    schema_path = settings.FEATURE_SCHEMA_PATH

    for p in [onnx_path, scaler_path, schema_path]:
        if not p.exists():
            raise ModelLoadError(f"Thiếu tệp mô hình dự đoán bắt buộc: {p.name}", p)

    try:
        session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        with open(scaler_path, "r", encoding="utf-8") as f:
            scaler = json.load(f)
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        return RiskModelArtifacts(session=session, scaler=scaler, schema=schema)
    except Exception as e:
        raise ModelLoadError(f"Lỗi khi nạp mô hình ONNX/Scaler: {str(e)}")


def load_knowledge_base() -> KnowledgeBaseArtifacts:
    """Nạp Production KB Vector Index, chunks metadata và mô hình embedding."""
    idx_path = settings.KB_INDEX_PATH
    meta_path = settings.KB_CHUNKS_PATH
    cfg_path = settings.KB_CONFIG_PATH

    for p in [idx_path, meta_path, cfg_path]:
        if not p.exists():
            raise ModelLoadError(f"Thiếu tệp cơ sở tri thức bắt buộc: {p.name}", p)

    try:
        index = HybridVectorIndex.load(idx_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        with open(cfg_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        return KnowledgeBaseArtifacts(index=index, metadata=metadata, config=config, embedder=embedder)
    except Exception as e:
        raise ModelLoadError(f"Lỗi khi nạp cơ sở tri thức / mô hình embedding: {str(e)}")


def load_rl_recommendation() -> RLRecommendationArtifacts:
    """Nạp Q-table, policy và discretization.json."""
    policy_path = settings.RL_POLICY_PATH
    q_table_path = settings.Q_TABLE_PATH
    disc_path = settings.DISCRETIZATION_PATH

    for p in [policy_path, q_table_path, disc_path]:
        if not p.exists():
            raise ModelLoadError(f"Thiếu tệp học tăng cường bắt buộc: {p.name}", p)

    try:
        policy = np.load(str(policy_path))
        q_table = np.load(str(q_table_path))
        with open(disc_path, "r", encoding="utf-8") as f:
            disc = json.load(f)

        # Kiểm định kích thước
        cardinality_states = disc["state_space_discretization"]["cardinality"]
        cardinality_actions = disc["action_space_definitions"]["cardinality"]
        if q_table.shape != (cardinality_states, cardinality_actions):
            raise ValueError(f"Kích thước Q-table {q_table.shape} không khớp với discretization ({cardinality_states}, {cardinality_actions})")
        if policy.shape != (cardinality_states,):
            raise ValueError(f"Kích thước policy {policy.shape} không khớp với {cardinality_states} trạng thái")

        return RLRecommendationArtifacts(q_table=q_table, policy=policy, discretization=disc)
    except Exception as e:
        raise ModelLoadError(f"Lỗi khi nạp mô hình Học tăng cường (RL): {str(e)}")


def load_safety_rules() -> SafetyRulesArtifacts:
    """Nạp tệp quy tắc an toàn y tế rules.yaml."""
    rules_path = settings.RULES_PATH
    if not rules_path.exists():
        raise ModelLoadError(f"Thiếu tệp luật an toàn y tế bắt buộc: {rules_path.name}", rules_path)

    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            rules_data = yaml.safe_load(f)
        return SafetyRulesArtifacts(rules_data=rules_data)
    except Exception as e:
        raise ModelLoadError(f"Lỗi khi nạp tệp luật an toàn rules.yaml: {str(e)}")


def load_all_artifacts() -> ModelContainer:
    """Nạp đồng thời toàn bộ 4 thành phần. Nếu thiếu bất kỳ thành phần nào thì ném ModelLoadError."""
    risk_model = load_risk_model()
    kb = load_knowledge_base()
    rl = load_rl_recommendation()
    safety = load_safety_rules()
    return ModelContainer(risk_model=risk_model, kb=kb, rl=rl, safety=safety)
