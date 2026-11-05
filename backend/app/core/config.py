from pathlib import Path
import os
from dotenv import load_dotenv

# Tự động nạp biến môi trường từ tệp .env ở thư mục gốc
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

class Settings:
    """Cấu hình toàn cục cho hệ thống đa tác tử tư vấn đái tháo đường."""
    PROJECT_NAME: str = "Hệ đa agent hỗ trợ tư vấn cho bệnh nhân tiểu đường"
    VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    
    # Đường dẫn thư mục gốc
    BASE_DIR: Path = PROJECT_ROOT
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    DATA_DIR: Path = PROJECT_ROOT / "data"
    REPORTS_DIR: Path = PROJECT_ROOT / "reports"
    
    # Artifacts của Agent Dự đoán (MLP ONNX)
    ONNX_MODEL_PATH: Path = MODELS_DIR / "risk_model.onnx"
    SCALER_PATH: Path = MODELS_DIR / "scaler.json"
    FEATURE_SCHEMA_PATH: Path = MODELS_DIR / "feature_schema.json"
    DECISION_THRESHOLD: float = 0.87  # Ngưỡng tối ưu hóa F1 từ NB01
    
    # Artifacts của Agent Tri thức (KB + RAG)
    KB_INDEX_DIR: Path = MODELS_DIR / "kb_index"
    KB_INDEX_PATH: Path = KB_INDEX_DIR / "kb_production_index.pkl"
    KB_CHUNKS_PATH: Path = KB_INDEX_DIR / "kb_chunks_metadata.json"
    KB_CONFIG_PATH: Path = KB_INDEX_DIR / "kb_config.json"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM: int = 384
    
    # Artifacts của Agent Đề xuất (RL Q-Table)
    RL_POLICY_PATH: Path = MODELS_DIR / "rl_policy.npy"
    Q_TABLE_PATH: Path = MODELS_DIR / "q_table.npy"
    DISCRETIZATION_PATH: Path = MODELS_DIR / "discretization.json"
    
    # Artifacts của Agent An toàn (Safety Rule-Based)
    RULES_PATH: Path = MODELS_DIR / "rules.yaml"
    
    # Bộ dữ liệu đánh giá RAG
    RAG_APPROVED_QUESTIONS_PATH: Path = DATA_DIR / "eval" / "rag_questions_approved.json"
    
    # Khóa API Gemini cho LLM (tùy chọn, không có thì fallback extractive KB)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
