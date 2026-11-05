from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Cấu trúc dữ liệu phản hồi thống nhất của mọi tác tử theo đặc tả Chương 3."""
    agent: str = Field(..., description="Tên định danh của Agent phát sinh phản hồi")
    content: Any = Field(..., description="Nội dung kết quả tư vấn, dự đoán hoặc đề xuất")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Độ tự tin lượng hóa [0.0, 1.0]")
    evidence: Any = Field(default_factory=list, description="Căn cứ y khoa, nguồn trích dẫn hoặc chỉ số chứng minh")
    flags: List[str] = Field(default_factory=list, description="Các cờ trạng thái kiểm soát (PASS, VETO, EMERGENCY,...)")
    trace: Dict[str, Any] = Field(default_factory=dict, description="Thông tin vết thực thi và độ trễ tính toán")


class BaseAgent(ABC):
    """Lớp cơ sở trừu tượng cho tất cả các tác tử trong hệ đa tác tử."""
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, request: Dict[str, Any]) -> AgentResponse:
        """Phương thức thực thi chính tiếp nhận yêu cầu và trả về AgentResponse."""
        pass
