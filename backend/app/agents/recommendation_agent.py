import time
from datetime import datetime
from typing import Any, Dict, Optional

from backend.app.agents.base import BaseAgent, AgentResponse
from backend.app.core.loaders import RLRecommendationArtifacts, load_rl_recommendation


class RecommendationAgent(BaseAgent):
    """Agent Đề xuất lối sống (Dinh dưỡng, Vận động, Đo đường huyết) dựa trên chính sách Q-Learning (RL).
    NGHIÊM CẤM TUYỆT ĐỐI HÀNH ĐỘNG KÊ ĐƠN HOẶC ĐIỀU CHỈNH LIỀU THUỐC/INSULIN.
    """

    def __init__(self, artifacts: Optional[RLRecommendationArtifacts] = None):
        super().__init__(name="RecommendationAgent")
        self.artifacts = artifacts or load_rl_recommendation()
        self.discretization = self.artifacts.discretization

    def _infer_time_bin(self, request: Dict[str, Any]) -> int:
        """Xác định khung giờ sinh học (0: Sáng, 1: Trưa, 2: Tối, 3: Đêm)."""
        if "time_bin" in request and request["time_bin"] is not None:
            try:
                t = int(request["time_bin"])
                return max(0, min(3, t))
            except (ValueError, TypeError):
                pass

        if "time_of_day" in request and request["time_of_day"] is not None:
            val = str(request["time_of_day"]).strip().lower()
            if "sáng" in val or "morning" in val:
                return 0
            if "trưa" in val or "lunch" in val or "noon" in val:
                return 1
            if "tối" in val or "dinner" in val or "evening" in val:
                return 2
            if "đêm" in val or "night" in val or "bedtime" in val:
                return 3

        # Mặc định suy diễn theo giờ thực của hệ thống
        hour = datetime.now().hour
        if 5 <= hour < 11:
            return 0
        elif 11 <= hour < 14:
            return 1
        elif 14 <= hour < 21:
            return 2
        else:
            return 3

    def _generate_rationale(self, carb: str, exercise: str, remind: bool, glucose_val: float) -> Dict[str, str]:
        """Tạo lý do giải thích y khoa ngắn gọn cho từng thành phần lối sống."""
        # Giải thích dinh dưỡng
        if carb == "LOW":
            carb_reason = f"Đường huyết hiện tại ({glucose_val:.1f} mg/dL) ở mức cao; khuyến nghị giảm tinh bột nhanh để tránh làm đường huyết tăng thêm."
        elif carb == "MODERATE":
            carb_reason = f"Đường huyết trong ngưỡng kiểm soát ({glucose_val:.1f} mg/dL); khuyến nghị khẩu phần tinh bột phức hợp cân bằng (Đĩa ăn lành mạnh: 1/4 tinh bột, 1/4 đạm nạc, 1/2 rau củ)."
        else:
            carb_reason = f"Đường huyết có xu hướng thấp ({glucose_val:.1f} mg/dL); cần nạp đủ carbohydrate lành mạnh để duy trì năng lượng và ngăn ngừa hạ đường huyết."

        # Giải thích vận động
        if exercise == "NONE":
            if glucose_val < 100:
                exercise_reason = f"Đường huyết thấp (<100 mg/dL); tạm thời NGHỈ NGƠI, cấm tập thể dục nhằm loại bỏ nguy cơ hạ đường huyết nguy hiểm."
            elif glucose_val > 250:
                exercise_reason = f"Đường huyết rất cao (>250 mg/dL); tạm dừng vận động thể lực cường độ vừa/cao để phòng ngừa nguy cơ nhiễm toan ceton (DKA)."
            else:
                exercise_reason = "Khung giờ nghỉ ngơi tĩnh; không yêu cầu vận động thể lực."
        else:
            exercise_reason = f"Đường huyết nằm trong vùng an toàn ({glucose_val:.1f} mg/dL); khuyến khích vận động vừa phải (đi bộ nhanh 20-30 phút) giúp tăng nhạy cảm insulin và tiêu hao glucose dư thừa."

        # Giải thích nhắc nhở đo đường huyết
        if remind:
            remind_reason = f"Chỉ số đường huyết ({glucose_val:.1f} mg/dL) nằm ngoài khoảng mục tiêu; bắt buộc đo lại đường huyết mao mạch sau 15-30 phút để theo dõi tiến triển."
        else:
            remind_reason = "Chỉ số đường huyết trong khoảng an toàn; duy trì lịch theo dõi đường huyết định kỳ thông thường."

        return {
            "nutrition_rationale": carb_reason,
            "exercise_rationale": exercise_reason,
            "monitoring_rationale": remind_reason
        }

    def run(self, request: Dict[str, Any]) -> AgentResponse:
        start_time = time.perf_counter()

        # 1. Kiểm tra biến đường huyết bắt buộc
        glucose_raw = request.get("blood_glucose_level")
        if glucose_raw is None or str(glucose_raw).strip() == "":
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return AgentResponse(
                agent=self.name,
                content={
                    "message": "Chưa đủ dữ liệu để đề xuất kế hoạch lối sống.",
                    "reason": "Thiếu thông số nồng độ đường huyết (blood_glucose_level). Vui lòng cung cấp chỉ số đường huyết để nhận tư vấn dinh dưỡng và vận động.",
                    "missing_fields": ["blood_glucose_level"]
                },
                confidence=0.0,
                evidence=[],
                flags=["INSUFFICIENT_DATA", "RECOMMENDATION_SKIPPED"],
                trace={
                    "latency_ms": round(elapsed_ms, 2),
                    "status": "skipped_missing_glucose"
                }
            )

        # 2. Xử lý đơn vị đo đường huyết
        try:
            glucose_val = float(glucose_raw)
            unit = str(request.get("glucose_unit", "mg/dL")).strip().lower()
            if unit in ["mmol/l", "mmol"] or glucose_val < 35.0:
                # Tự động quy đổi nếu người dùng nhập mmol/L hoặc giá trị < 35
                glucose_mg_dl = glucose_val * 18.0182
            else:
                glucose_mg_dl = glucose_val
        except (ValueError, TypeError):
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return AgentResponse(
                agent=self.name,
                content={"error": f"Giá trị đường huyết không hợp lệ: {glucose_raw}"},
                confidence=0.0,
                flags=["INVALID_GLUCOSE_VALUE"],
                trace={"latency_ms": round(elapsed_ms, 2), "status": "error"}
            )

        # 3. Xác định khung giờ và tra cứu Q-Table
        time_bin = self._infer_time_bin(request)
        rec_data = self.artifacts.recommend(glucose_mg_dl=glucose_mg_dl, time_bin=time_bin)
        state_id = rec_data["state_id"]
        action_id = rec_data["action_id"]
        action_details = rec_data["details"]

        carb = action_details["carb"]
        exercise = action_details["exercise"]
        remind = action_details["remind"]

        # 4. Tạo lý giải y khoa cho khuyến nghị
        rationales = self._generate_rationale(carb, exercise, remind, glucose_mg_dl)

        time_labels = ["Sáng (Trước/Sau ăn)", "Trưa (Trước/Sau ăn)", "Tối (Trước/Sau ăn)", "Đêm (Trước khi ngủ)"]
        time_label = time_labels[time_bin] if 0 <= time_bin < len(time_labels) else f"Khung giờ {time_bin}"

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return AgentResponse(
            agent=self.name,
            content={
                "recommendation_summary": f"Dinh dưỡng: {carb} Carb | Vận động: {exercise} | Nhắc đo: {'Bắt buộc đo lại' if remind else 'Bình thường'}",
                "state_mapping": {
                    "state_id": state_id,
                    "glucose_evaluated_mg_dl": round(glucose_mg_dl, 1),
                    "glucose_evaluated_mmol_l": round(glucose_mg_dl / 18.0182, 2),
                    "time_slot": time_label
                },
                "lifestyle_plan": {
                    "nutrition": {
                        "level": carb,
                        "label": f"Bữa ăn mức tinh bột {carb}",
                        "rationale": rationales["nutrition_rationale"]
                    },
                    "exercise": {
                        "level": exercise,
                        "label": "Tạm nghỉ thể lực" if exercise == "NONE" else "Vận động thể lực vừa phải (đi bộ 20-30 phút)",
                        "rationale": rationales["exercise_rationale"]
                    },
                    "monitoring": {
                        "required": remind,
                        "label": "Bắt buộc đo lại đường huyết" if remind else "Theo dõi định kỳ",
                        "rationale": rationales["monitoring_rationale"]
                    }
                },
                "action_id": action_id,
                "disclaimer": "Đề xuất lối sống chỉ mang tính hỗ trợ giáo dục sức khỏe, KHÔNG thay thế phác đồ điều trị của bác sĩ chuyên khoa."
            },
            confidence=0.95,  # Chính sách Q-Table tối ưu đã hội tụ qua 5 seeds
            evidence=[{
                "policy_source": "Tabular Q-Learning (NB03)",
                "state_id": state_id,
                "action_id": action_id,
                "action_schema": action_details["label"]
            }],
            flags=["PASS", "LIFESTYLE_RECOMMENDATION_ACTIVE"],
            trace={
                "latency_ms": round(elapsed_ms, 2),
                "state_id": state_id,
                "action_id": action_id,
                "status": "success"
            }
        )
