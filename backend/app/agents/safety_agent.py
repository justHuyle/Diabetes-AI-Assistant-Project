import time
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from backend.app.agents.base import BaseAgent, AgentResponse
from backend.app.core.loaders import SafetyRulesArtifacts, load_safety_rules


class SafetyReviewResult(BaseModel):
    """Kết quả thẩm định của Agent an toàn đối với toàn bộ phiên tư vấn."""
    status: str = Field(..., description="Trạng thái kiểm duyệt: 'PASS', 'MODIFY', 'VETO'")
    emergency_detected: bool = Field(default=False, description="Cờ kích hoạt đường rút gọn cấp cứu khẩn cấp")
    emergency_message: Optional[str] = Field(default=None, description="Nội dung cảnh báo cấp cứu nếu có")
    triggered_rules: List[str] = Field(default_factory=list, description="Danh sách các mã luật đã bị kích hoạt")
    modifications_made: List[str] = Field(default_factory=list, description="Các can thiệp hiệu chỉnh đã thực hiện")
    sanitized_responses: Dict[str, Any] = Field(default_factory=dict, description="Các phản hồi sau khi đã được thẩm định an toàn")


class SafetyAgent(BaseAgent):
    """Agent An toàn y tế lâm sàng chịu trách nhiệm giám sát, phủ quyết (Veto) và bảo vệ bệnh nhân."""

    def __init__(self, artifacts: Optional[SafetyRulesArtifacts] = None):
        super().__init__(name="SafetyAgent")
        self.artifacts = artifacts or load_safety_rules()
        self.rules = self.artifacts.rules

        # Danh sách từ khóa cấm kê đơn hoặc yêu cầu chỉnh liều thuốc/insulin
        self.prescription_keywords = [
            "kê đơn", "cho đơn thuốc", "uống thuốc gì", "mua thuốc gì",
            "chỉnh liều", "tăng liều", "giảm liều", "đổi liều",
            "tiêm bao nhiêu", "tiêm mấy đơn vị", "liều insulin", "tiêm insulin bao nhiêu",
            "metformin mấy viên", "uống mấy viên", "đơn thuốc"
        ]

    def _extract_glucose(self, metrics: Dict[str, Any]) -> Optional[float]:
        """Trích xuất và quy đổi giá trị đường huyết về đơn vị mg/dL."""
        val = metrics.get("blood_glucose_level")
        if val is None:
            return None
        try:
            f_val = float(val)
            unit = str(metrics.get("glucose_unit", "mg/dL")).strip().lower()
            if unit in ["mmol/l", "mmol"] or f_val < 35.0:
                return f_val * 18.0182
            return f_val
        except (ValueError, TypeError):
            return None

    def _check_emergency(self, glucose_mg_dl: float) -> Tuple[bool, Optional[str], List[str]]:
        """Đường rút gọn cấp cứu (Emergency Short-Circuit) khi phát hiện chỉ số đe dọa sinh mạng."""
        if glucose_mg_dl < 70.0:
            msg = (
                "🚨 **CẢNH BÁO CẤP CỨU KHẨN CẤP: HẠ ĐƯỜNG HUYẾT NGUY HIỂM (< 70 mg/dL / 3.9 mmol/L)!**\n"
                "• **Xử trí ngay lập tức (Quy tắc 15-15)**: Uống ngay 1/2 cốc nước ngọt có đường (120ml), nước ép hoa quả, hoặc 3-4 viên đường/kẹo ngọt.\n"
                "• **Nghỉ ngơi tại chỗ trong 15 phút**, sau đó đo lại đường huyết mao mạch.\n"
                "• **TUYỆT ĐỐI CẤM TẬP THỂ DỤC** hoặc nhịn ăn.\n"
                "• Nếu xuất hiện dấu hiệu vã mồ hôi lạnh, run rẩy nặng, lú lẫn hoặc bất tỉnh, người nhà phải **gọi cấp cứu 115 hoặc đưa ngay đến bệnh viện**!"
            )
            return True, msg, ["EMERGENCY_HYPOGLYCEMIA", "RULE_01_TRIGGERED", "RULE_05_TRIGGERED"]

        if glucose_mg_dl > 250.0:
            msg = (
                "🚨 **CẢNH BÁO CẤP CỨU: TĂNG ĐƯỜNG HUYẾT RẤT CAO (> 250 mg/dL / 14.0 mmol/L)!**\n"
                "• Chỉ số đường huyết vượt ngưỡng an toàn nghiêm trọng, mang nguy cơ cao biến chứng cấp tính **Nhiễm toan ceton (DKA)** hoặc tăng áp lực thẩm thấu.\n"
                "• **TUYỆT ĐỐI KHÔNG TẬP THỂ DỤC** cường độ vừa hoặc nặng (vận động lúc này sẽ làm phóng thích thêm ceton vào máu gây nguy hiểm tính mạng).\n"
                "• Uống nhiều nước lọc (tránh nước ngọt), liên hệ ngay bác sĩ điều trị hoặc đến cơ sở y tế gần nhất để được kiểm tra và xử trí kịp thời."
            )
            return True, msg, ["EMERGENCY_HYPERGLYCEMIA", "RULE_02_TRIGGERED", "RULE_05_TRIGGERED"]

        return False, None, []

    def _detect_prescription_request(self, query: str) -> bool:
        """Phát hiện câu hỏi của người dùng có chứa yêu cầu kê đơn hoặc chỉnh liều thuốc không."""
        q_lower = query.lower()
        for kw in self.prescription_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                return True
        return False

    def review(
        self,
        responses: Dict[str, AgentResponse],
        metrics: Dict[str, Any],
        query: str = ""
    ) -> SafetyReviewResult:
        """Hàm thẩm định trung tâm: kiểm duyệt, phủ quyết hoặc chỉnh sửa phản hồi của các agent khác."""
        triggered_rules = []
        modifications = []
        status = "PASS"
        emergency_detected = False
        emergency_msg = None

        glucose_mg_dl = self._extract_glucose(metrics)

        # 1. ĐƯỜNG RÚT GỌN CẤP CỨU (EMERGENCY SHORT-CIRCUIT)
        if glucose_mg_dl is not None:
            is_emerg, e_msg, e_flags = self._check_emergency(glucose_mg_dl)
            if is_emerg:
                emergency_detected = True
                emergency_msg = e_msg
                status = "VETO"
                triggered_rules.extend(e_flags)
                modifications.append("Kích hoạt cảnh báo cấp cứu khẩn cấp ưu tiên lên đầu toàn bộ phản hồi.")

        # 2. KIỂM DUYỆT TỪ KHÓA CẤM KÊ ĐƠN THUỐC (RULE_06)
        if query and self._detect_prescription_request(query):
            status = "VETO"
            triggered_rules.append("RULE_06_NO_MEDICATION_IN_RL")
            prescription_refusal = (
                "⚠️ **TUYỆT ĐỐI TỪ CHỐI KÊ ĐƠN / CHỈNH LIỀU THUỐC**: "
                "Theo quy định an toàn y tế và phạm vi của đồ án, hệ thống trí tuệ nhân tạo chỉ cung cấp thông tin giáo dục sức khỏe và tư vấn lối sống. "
                "Hệ thống **nghiêm cấm tuyệt đối** việc kê đơn thuốc mới hoặc điều chỉnh liều lượng Metformin, Sulfonylurea, Insulin. "
                "Mọi quyết định dùng thuốc bắt buộc phải có chỉ định trực tiếp từ bác sĩ chuyên khoa sau khi thăm khám lâm sàng."
            )
            modifications.append("Chặn yêu cầu kê đơn thuốc / chỉnh liều y tế; chèn thông điệp từ chối theo luật y đức.")
            if "knowledge_agent" in responses:
                # Đính kèm từ chối vào phản hồi tri thức
                old_ans = responses["knowledge_agent"].content.get("answer", "")
                responses["knowledge_agent"].content["answer"] = f"{prescription_refusal}\n\n---\n{old_ans}"
                responses["knowledge_agent"].flags.append("VETO_PRESCRIPTION_REFUSED")

        # 3. THẨM ĐỊNH CHI TIẾT CÁC QUY TẮC AN TOÀN TRÊN KHUYẾN NGHỊ LỐI SỐNG (RL)
        if "recommendation_agent" in responses and glucose_mg_dl is not None:
            rec_resp = responses["recommendation_agent"]
            plan = rec_resp.content.get("lifestyle_plan", {})
            curr_carb = plan.get("nutrition", {}).get("level", "MODERATE")
            curr_ex = plan.get("exercise", {}).get("level", "NONE")
            curr_remind = plan.get("monitoring", {}).get("required", False)

            # RULE_01: Cấm vận động khi đường huyết < 100 mg/dL
            if glucose_mg_dl < 100.0 and curr_ex != "NONE":
                status = "MODIFY" if status != "VETO" else "VETO"
                triggered_rules.append("RULE_01_HYPO_NO_EXERCISE")
                plan["exercise"]["level"] = "NONE"
                plan["exercise"]["label"] = "Tạm nghỉ thể lực (Agent An toàn đã hiệu chỉnh: Cấm tập khi đường huyết < 100 mg/dL)"
                modifications.append("RULE_01: Chuyển vận động về NONE vì đường huyết < 100 mg/dL.")

            # RULE_02: Cấm vận động khi đường huyết > 250 mg/dL
            if glucose_mg_dl > 250.0 and curr_ex != "NONE":
                status = "MODIFY" if status != "VETO" else "VETO"
                triggered_rules.append("RULE_02_HYPER_NO_EXERCISE")
                plan["exercise"]["level"] = "NONE"
                plan["exercise"]["label"] = "Tạm nghỉ thể lực (Agent An toàn đã hiệu chỉnh: Nguy cơ toan ceton khi đường huyết > 250 mg/dL)"
                modifications.append("RULE_02: Chuyển vận động về NONE vì đường huyết > 250 mg/dL.")

            # RULE_03: Cấm ăn High Carb khi đường huyết > 180 mg/dL
            if glucose_mg_dl > 180.0 and curr_carb == "HIGH":
                status = "MODIFY" if status != "VETO" else "VETO"
                triggered_rules.append("RULE_03_HYPER_RESTRICT_CARB")
                plan["nutrition"]["level"] = "LOW"
                plan["nutrition"]["label"] = "Bữa ăn mức tinh bột LOW (Agent An toàn hiệu chỉnh: Cấm High Carb khi đường huyết > 180 mg/dL)"
                modifications.append("RULE_03: Hạ khẩu phần tinh bột từ HIGH xuống LOW vì đường huyết > 180 mg/dL.")

            # RULE_04: Cấm cắt kiệt tinh bột (Low Carb) khi đường huyết < 80 mg/dL
            if glucose_mg_dl < 80.0 and curr_carb == "LOW":
                status = "MODIFY" if status != "VETO" else "VETO"
                triggered_rules.append("RULE_04_HYPO_REQUIRE_CARB")
                plan["nutrition"]["level"] = "MODERATE"
                plan["nutrition"]["label"] = "Bữa ăn mức tinh bột MODERATE (Agent An toàn hiệu chỉnh: Cấm Low Carb khi đường huyết cận hạ)"
                modifications.append("RULE_04: Nâng khẩu phần tinh bột từ LOW lên MODERATE vì đường huyết < 80 mg/dL.")

            # RULE_05: Bắt buộc nhắc đo đường huyết khi < 70 hoặc > 250 mg/dL
            if (glucose_mg_dl < 70.0 or glucose_mg_dl > 250.0) and not curr_remind:
                status = "MODIFY" if status != "VETO" else "VETO"
                triggered_rules.append("RULE_05_MANDATORY_MONITORING")
                plan["monitoring"]["required"] = True
                plan["monitoring"]["label"] = "Bắt buộc đo lại đường huyết (Agent An toàn kích hoạt do chỉ số bất thường)"
                modifications.append("RULE_05: Kích hoạt cờ nhắc đo đường huyết bắt buộc.")

            # Đồng bộ lại tóm tắt nếu có sửa đổi
            if modifications:
                rec_resp.flags.append("SAFETY_MODIFIED")
                rec_resp.trace["safety_modifications"] = modifications

        # Đóng gói kết quả thẩm định
        sanitized = {k: v.model_dump() for k, v in responses.items()}

        return SafetyReviewResult(
            status=status,
            emergency_detected=emergency_detected,
            emergency_message=emergency_msg,
            triggered_rules=list(set(triggered_rules)),
            modifications_made=modifications,
            sanitized_responses=sanitized
        )

    def run(self, request: Dict[str, Any]) -> AgentResponse:
        """Thực thi độc lập kiểm tra luật an toàn trên một bộ thông số đầu vào."""
        start_time = time.perf_counter()
        glucose_mg_dl = self._extract_glucose(request)
        query = str(request.get("query", ""))

        if glucose_mg_dl is None:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return AgentResponse(
                agent=self.name,
                content={"status": "PASS", "message": "Không có thông số sinh hóa để kiểm duyệt luật ngưỡng."},
                confidence=1.0,
                flags=["NO_METRICS_TO_CHECK"],
                trace={"latency_ms": round(elapsed_ms, 2), "status": "pass_no_metrics"}
            )

        # Kiểm tra cấp cứu
        is_emerg, e_msg, e_flags = self._check_emergency(glucose_mg_dl)
        # Kiểm tra kê đơn
        is_presc = self._detect_prescription_request(query)

        flags = []
        if is_emerg:
            flags.extend(e_flags)
            flags.append("VETO")
        if is_presc:
            flags.append("RULE_06_TRIGGERED")
            flags.append("VETO")
        if not flags:
            flags.append("PASS")

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return AgentResponse(
            agent=self.name,
            content={
                "safety_status": "VETO" if ("VETO" in flags) else "PASS",
                "emergency_detected": is_emerg,
                "emergency_message": e_msg,
                "prescription_request_detected": is_presc,
                "glucose_evaluated_mg_dl": round(glucose_mg_dl, 1)
            },
            confidence=1.0,
            evidence=[{"rules_checked": len(self.rules)}],
            flags=flags,
            trace={"latency_ms": round(elapsed_ms, 2), "status": "success"}
        )
