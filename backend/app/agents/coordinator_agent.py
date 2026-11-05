import time
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from backend.app.agents.base import BaseAgent, AgentResponse
from backend.app.agents.prediction_agent import PredictionAgent
from backend.app.agents.knowledge_agent import KnowledgeAgent
from backend.app.agents.recommendation_agent import RecommendationAgent
from backend.app.agents.safety_agent import SafetyAgent, SafetyReviewResult
from backend.app.core.loaders import ModelContainer, load_all_artifacts
from backend.app.schemas.consult import ConsultRequest, ConsultResponse

# Bộ nhớ lưu vết các phiên tư vấn trong phiên làm việc
TRACE_STORE: Dict[str, Dict[str, Any]] = {}


class CoordinatorAgent(BaseAgent):
    """Agent Điều phối trung tâm (Orchestrator) chịu trách nhiệm:
    1. Phân loại ý định (Intent Classification).
    2. Định tuyến tới 4 agent chuyên trách.
    3. Đảm bảo SafetyAgent luôn chạy cuối cùng để kiểm duyệt.
    4. Hợp nhất phản hồi theo thứ tự ưu tiên bất biến: An toàn > Tri thức > Đề xuất > Dự đoán.
    5. Ghi nhận toàn bộ vết thực thi (Execution Trace).
    """

    def __init__(self, container: Optional[ModelContainer] = None):
        super().__init__(name="CoordinatorAgent")
        self.container = container or load_all_artifacts()
        self.prediction_agent = PredictionAgent(artifacts=self.container.risk_model)
        self.knowledge_agent = KnowledgeAgent(artifacts=self.container.kb)
        self.recommendation_agent = RecommendationAgent(artifacts=self.container.rl)
        self.safety_agent = SafetyAgent(artifacts=self.container.safety)

    def classify_intent(self, query: str, metrics: Dict[str, Any]) -> str:
        """Phân loại ý định người dùng bằng hệ luật xác định kết hợp từ khóa y khoa."""
        q_lower = query.lower()

        # 1. Tình huống cấp cứu khẩn cấp (Emergency)
        emergency_keywords = [
            "hôn mê", "ngất", "bất tỉnh", "co giật", "khó thở dữ dội", "cấp cứu",
            "thở mùi táo chín", "đo đường huyết dưới 50", "đo đường huyết 300",
            "vã mồ hôi lạnh run rẩy"
        ]
        if any(kw in q_lower for kw in emergency_keywords):
            return "emergency"

        glucose_val = metrics.get("blood_glucose_level")
        if glucose_val is not None:
            try:
                g = float(glucose_val)
                unit = str(metrics.get("glucose_unit", "mg/dL")).strip().lower()
                if unit in ["mmol/l", "mmol"] or g < 35.0:
                    g = g * 18.0182
                if g < 70.0 or g > 250.0:
                    return "emergency"
            except (ValueError, TypeError):
                pass

        # 2. Ngoài phạm vi / Yêu cầu kê đơn thuốc (Out of Scope / Prescription)
        prescription_keywords = [
            "kê đơn", "cho đơn thuốc", "uống thuốc gì", "mua thuốc gì",
            "chỉnh liều", "tăng liều", "giảm liều", "đổi liều",
            "tiêm bao nhiêu", "tiêm mấy đơn vị", "liều insulin", "tiêm insulin bao nhiêu",
            "metformin mấy viên", "uống mấy viên", "đơn thuốc"
        ]
        if any(kw in q_lower for kw in prescription_keywords):
            return "out_of_scope"

        # 3. Nhập chỉ số để nhận tư vấn sức khỏe (Clinical Consultation)
        has_metrics = bool(metrics and any(
            k in metrics for k in ["blood_glucose_level", "age", "bmi", "hbA1c_level"]
        ))
        consult_keywords = ["chỉ số của tôi", "tôi có bị", "nguy cơ", "kết quả xét nghiệm", "tư vấn giúp tôi"]
        if has_metrics or any(kw in q_lower for kw in consult_keywords):
            return "clinical_consultation"

        # 4. Phân biệt Hỏi đáp tri thức y khoa chuẩn (Knowledge Query) hay Hội thoại xã giao (Chitchat)
        diabetes_keywords = [
            "đái tháo đường", "tiểu đường", "đường huyết", "glucose", "hba1c", "insulin",
            "chẩn đoán", "tiền đái tháo đường", "tiền tiểu đường", "toan ceton", "dinh dưỡng",
            "tinh bột", "carb", "tập thể dục", "vận động", "ada", "bộ y tế", "5481",
            "chỉ số", "xét nghiệm", "biến chứng", "lúc đói", "sau ăn"
        ]
        if any(dk in q_lower for dk in diabetes_keywords):
            return "knowledge_query"

        chitchat_keywords = [
            "chào", "hello", "hi", "hey", "bạn là ai", "bạn tên gì", "giúp được gì",
            "thời tiết", "kể chuyện", "hôm nay ăn gì", "hài hước", "cảm ơn", "thanks", "tạm biệt", "bye"
        ]
        if any(ck in q_lower for ck in chitchat_keywords):
            return "chitchat"

        if query.strip():
            # Mặc định phân loại chitchat để Gemini trò chuyện linh hoạt khi ngoài ngữ liệu đái tháo đường
            return "chitchat"

        return "clinical_consultation"

    def _normalize_metrics(self, raw_metrics: Dict[str, Any], global_unit: str) -> Dict[str, Any]:
        """Chuẩn hóa các trường chỉ số và đồng bộ đơn vị đo đường huyết."""
        metrics = dict(raw_metrics)
        unit = str(metrics.get("glucose_unit", global_unit)).strip()
        metrics["glucose_unit"] = unit
        return metrics

    def consult(self, request: ConsultRequest) -> ConsultResponse:
        """Quy trình điều phối đa tác tử toàn diện."""
        start_time = time.perf_counter()
        consultation_id = str(uuid.uuid4())

        query = (request.message or request.query or "").strip()
        metrics = self._normalize_metrics(request.metrics or {}, request.glucose_unit or "mg/dL")
        if request.time_of_day and "time_of_day" not in metrics:
            metrics["time_of_day"] = request.time_of_day
        if request.time_bin is not None and "time_bin" not in metrics:
            metrics["time_bin"] = request.time_bin

        # 1. Phân loại ý định
        intent = self.classify_intent(query, metrics)

        # Cấu trúc ghi vết thực thi (Execution Trace)
        trace_payload: Dict[str, Any] = {
            "consultation_id": consultation_id,
            "created_at": datetime.now().isoformat(),
            "intent": intent,
            "steps": [],
            "agents_called": [],
            "rules_triggered": [],
            "sources_cited": []
        }

        agent_responses: Dict[str, AgentResponse] = {}

        # 2. ĐỊNH TUYẾN GỌI CÁC AGENT CHUYÊN TRÁCH

        # Bước 2a: Agent Dự đoán (Prediction)
        # Chỉ gọi khi có đủ 4 biến số học cơ bản, không tự điền giả
        can_predict = all(k in metrics for k in ["age", "bmi", "hbA1c_level", "blood_glucose_level", "gender"])
        if can_predict:
            t0 = time.perf_counter()
            pred_resp = self.prediction_agent.run(metrics)
            dur = (time.perf_counter() - t0) * 1000
            agent_responses["prediction_agent"] = pred_resp
            trace_payload["agents_called"].append("PredictionAgent")
            trace_payload["steps"].append({
                "agent": "PredictionAgent",
                "duration_ms": round(dur, 2),
                "status": "success" if "PASS" in pred_resp.flags or "HIGH_RISK_DETECTED" in pred_resp.flags else "error",
                "flags": pred_resp.flags
            })

        # Bước 2b: Agent Đề xuất lối sống (Recommendation)
        # Gọi khi có chỉ số đường huyết
        if "blood_glucose_level" in metrics and metrics["blood_glucose_level"] is not None:
            t0 = time.perf_counter()
            rec_resp = self.recommendation_agent.run(metrics)
            dur = (time.perf_counter() - t0) * 1000
            agent_responses["recommendation_agent"] = rec_resp
            trace_payload["agents_called"].append("RecommendationAgent")
            trace_payload["steps"].append({
                "agent": "RecommendationAgent",
                "duration_ms": round(dur, 2),
                "status": "success" if "PASS" in rec_resp.flags else "skipped",
                "flags": rec_resp.flags
            })

        # Bước 2c: Agent Tri thức (Knowledge)
        # Gọi khi có câu hỏi văn bản hoặc khi cần tra cứu tài liệu liên quan đến ca bệnh
        effective_query = query
        if not effective_query and "blood_glucose_level" in metrics:
            g = float(metrics["blood_glucose_level"])
            effective_query = f"Mục tiêu kiểm soát đường huyết và xử trí mức đường {g:.1f}"

        if effective_query:
            t0 = time.perf_counter()
            allow_cc = (intent == "chitchat" or not can_predict)
            kb_resp = self.knowledge_agent.run({"query": effective_query, "top_k": 3, "allow_chitchat": allow_cc})
            dur = (time.perf_counter() - t0) * 1000
            agent_responses["knowledge_agent"] = kb_resp
            trace_payload["agents_called"].append("KnowledgeAgent")
            trace_payload["steps"].append({
                "agent": "KnowledgeAgent",
                "duration_ms": round(dur, 2),
                "status": "success" if "PASS" in kb_resp.flags else ("chitchat" if "CONVERSATIONAL_CHITCHAT" in kb_resp.flags else "refused"),
                "flags": kb_resp.flags
            })
            if kb_resp.evidence:
                for ev in kb_resp.evidence:
                    trace_payload["sources_cited"].append(ev.get("source_file"))

        # Bước 2d: SafetyAgent LUÔN LUÔN CHẠY CUỐI ĐỂ THẨM ĐỊNH TOÀN BỘ
        t0 = time.perf_counter()
        safety_review: SafetyReviewResult = self.safety_agent.review(
            responses=agent_responses,
            metrics=metrics,
            query=query
        )
        dur = (time.perf_counter() - t0) * 1000
        trace_payload["agents_called"].append("SafetyAgent")
        trace_payload["rules_triggered"] = safety_review.triggered_rules
        trace_payload["steps"].append({
            "agent": "SafetyAgent",
            "duration_ms": round(dur, 2),
            "status": safety_review.status,
            "rules_triggered": safety_review.triggered_rules,
            "modifications": safety_review.modifications_made
        })

        # 3. HỢP NHẤT KẾT QUẢ THEO THỨ TỰ ƯU TIÊN (Safety > Knowledge > Recommendation > Prediction)
        total_latency = (time.perf_counter() - start_time) * 1000
        trace_payload["total_latency_ms"] = round(total_latency, 2)

        # Xây dựng bản tóm tắt hợp nhất
        summary_sections = []

        if safety_review.emergency_detected and safety_review.emergency_message:
            summary_sections.append(f"🚨 [CẢNH BÁO KHẨN CẤP]\n{safety_review.emergency_message}")

        if "RULE_06_NO_MEDICATION_IN_RL" in safety_review.triggered_rules:
            summary_sections.append(
                "⚠️ [LƯU Ý AN TOÀN Y TẾ]\nHệ thống AI không có thẩm quyền kê đơn thuốc hoặc điều chỉnh liều insulin. Vui lòng tham khảo trực tiếp bác sĩ chuyên khoa."
            )

        if "knowledge_agent" in agent_responses:
            k_ans = agent_responses["knowledge_agent"].content.get("answer")
            if k_ans:
                if intent == "chitchat" or agent_responses["knowledge_agent"].content.get("mode") == "conversational_chitchat":
                    summary_sections.append(f"💬 [HỘI THOẠI TRỢ LÝ]\n{k_ans}")
                else:
                    summary_sections.append(f"📚 [TRI THỨC Y KHOA]\n{k_ans}")

        if "recommendation_agent" in agent_responses:
            rec_c = agent_responses["recommendation_agent"].content
            if "lifestyle_plan" in rec_c:
                plan = rec_c["lifestyle_plan"]
                summary_sections.append(
                    f"🏃 [KẾ HOẠCH LỐI SỐNG]\n• Dinh dưỡng: {plan['nutrition']['label']}\n"
                    f"• Vận động: {plan['exercise']['label']}\n"
                    f"• Theo dõi: {plan['monitoring']['label']}"
                )

        if "prediction_agent" in agent_responses:
            p_c = agent_responses["prediction_agent"].content
            if "risk_category" in p_c:
                summary_sections.append(
                    f"📊 [DỰ BÁO RỦI RO]\n{p_c['risk_category']} (Xác suất rủi ro: {p_c['risk_probability']*100:.1f}%, Ngưỡng quyết định: {p_c['decision_threshold']})"
                )

        if intent == "chitchat" and "knowledge_agent" in agent_responses:
            k_ans = agent_responses["knowledge_agent"].content.get("answer")
            if k_ans and len(summary_sections) <= 1:
                final_summary = k_ans
            else:
                final_summary = "\n\n".join(summary_sections) if summary_sections else "Phiên tư vấn hoàn tất."
        else:
            final_summary = "\n\n".join(summary_sections) if summary_sections else "Phiên tư vấn hoàn tất."

        # Lưu vết vào bộ nhớ để phục vụ endpoint GET /api/trace/{id}
        TRACE_STORE[consultation_id] = trace_payload

        return ConsultResponse(
            consultation_id=consultation_id,
            intent=intent,
            status=safety_review.status,
            priority_order="Safety > Knowledge > Recommendation > Prediction",
            emergency_detected=safety_review.emergency_detected,
            emergency_alert=safety_review.emergency_message,
            summary=final_summary,
            safety_review=safety_review.model_dump(),
            knowledge_response=agent_responses.get("knowledge_agent").model_dump() if "knowledge_agent" in agent_responses else None,
            recommendation_response=agent_responses.get("recommendation_agent").model_dump() if "recommendation_agent" in agent_responses else None,
            prediction_response=agent_responses.get("prediction_agent").model_dump() if "prediction_agent" in agent_responses else None,
            trace=trace_payload
        )

    def run(self, request: Dict[str, Any]) -> AgentResponse:
        """Thực thi qua giao diện BaseAgent."""
        consult_req = ConsultRequest(**request)
        res = self.consult(consult_req)
        return AgentResponse(
            agent=self.name,
            content=res.model_dump(),
            confidence=1.0,
            evidence=res.trace.get("sources_cited", []),
            flags=[res.status],
            trace=res.trace
        )
