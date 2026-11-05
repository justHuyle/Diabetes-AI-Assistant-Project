from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConsultRequest(BaseModel):
    """Lược đồ dữ liệu yêu cầu tư vấn gửi tới POST /api/consult."""
    message: Optional[str] = Field(default="", description="Câu hỏi ngôn ngữ tự nhiên của người dùng")
    query: Optional[str] = Field(default=None, description="Tương đương với message, cho phép dùng hoán đổi")
    metrics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Các chỉ số lâm sàng (đường huyết, HbA1c, BMI,...)")
    glucose_unit: Optional[str] = Field(default="mg/dL", description="Đơn vị nồng độ glucose: 'mg/dL' hoặc 'mmol/L'")
    time_of_day: Optional[str] = Field(default=None, description="Thời điểm trong ngày: Sáng, Trưa, Tối, Đêm")
    time_bin: Optional[int] = Field(default=None, ge=0, le=3, description="Chỉ số khung giờ 0..3")


class PredictRequest(BaseModel):
    """Lược đồ yêu cầu dự đoán nguy cơ gửi tới POST /api/predict."""
    age: float = Field(..., ge=0.08, le=120.0, description="Tuổi bệnh nhân")
    bmi: float = Field(..., ge=10.0, le=100.0, description="Chỉ số khối cơ thể (kg/m²)")
    hbA1c_level: float = Field(..., ge=3.0, le=18.0, description="Tỷ lệ HbA1c (%)")
    blood_glucose_level: float = Field(..., ge=40.0, le=600.0, description="Đường huyết")
    gender: str = Field(..., description="Giới tính: Female hoặc Male")
    smoking_history: Optional[str] = Field(default="never", description="Tiền sử hút thuốc")
    hypertension: Optional[int] = Field(default=0, ge=0, le=1, description="Tiền sử tăng huyết áp (0 hoặc 1)")
    heart_disease: Optional[int] = Field(default=0, ge=0, le=1, description="Tiền sử bệnh tim mạch (0 hoặc 1)")
    glucose_unit: Optional[str] = Field(default="mg/dL", description="Đơn vị đường huyết: 'mg/dL' hoặc 'mmol/L'")
    race: Optional[str] = Field(default="Asian", description="Chủng tộc, mặc định Asian cho bệnh nhân VN")


class ConsultResponse(BaseModel):
    """Cấu trúc phản hồi hợp nhất từ Hệ đa tác tử theo thứ tự ưu tiên."""
    consultation_id: str
    intent: str
    status: str  # PASS, MODIFY, VETO
    priority_order: str = "Safety > Knowledge > Recommendation > Prediction"
    emergency_detected: bool = False
    emergency_alert: Optional[str] = None
    summary: str
    safety_review: Dict[str, Any]
    knowledge_response: Optional[Dict[str, Any]] = None
    recommendation_response: Optional[Dict[str, Any]] = None
    prediction_response: Optional[Dict[str, Any]] = None
    trace: Dict[str, Any]
