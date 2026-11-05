import time
from typing import Any, Dict, List, Optional
import numpy as np

from backend.app.agents.base import BaseAgent, AgentResponse
from backend.app.core.loaders import RiskModelArtifacts, load_risk_model


class PredictionAgent(BaseAgent):
    """Agent Dự đoán nguy cơ mắc đái tháo đường sử dụng mô hình Deep Learning MLP (ONNX)."""

    def __init__(self, artifacts: Optional[RiskModelArtifacts] = None):
        super().__init__(name="PredictionAgent")
        self.artifacts = artifacts or load_risk_model()
        self.schema = self.artifacts.schema
        self.scaler = self.artifacts.scaler
        self.threshold = self.artifacts.threshold

    def validate_inputs(self, data: Dict[str, Any]) -> List[str]:
        """Kiểm tra tính đầy đủ và miền giá trị hợp lệ theo feature_schema.json."""
        errors = []
        schema_features = {f["name"]: f for f in self.schema["input_features_schema"]}

        # 1. Kiểm tra 4 biến số học bắt buộc
        num_fields = ["age", "bmi", "hbA1c_level", "blood_glucose_level"]
        for field in num_fields:
            if field not in data or data[field] is None:
                errors.append(f"Thiếu trường số học bắt buộc: '{field}'")
                continue
            try:
                val = float(data[field])
                f_meta = schema_features.get(field, {})
                v_range = f_meta.get("valid_range", {})
                min_v = v_range.get("min")
                max_v = v_range.get("max")
                if min_v is not None and val < min_v:
                    errors.append(f"Trường '{field}' có giá trị {val} nhỏ hơn mức tối thiểu cho phép ({min_v})")
                if max_v is not None and val > max_v:
                    errors.append(f"Trường '{field}' có giá trị {val} vượt quá mức tối đa cho phép ({max_v})")
            except (ValueError, TypeError):
                errors.append(f"Trường '{field}' phải là số thực hợp lệ (nhận được: {data[field]})")

        # 2. Kiểm tra giới tính
        if "gender" not in data or not str(data["gender"]).strip():
            errors.append("Thiếu trường dữ liệu: 'gender'")
        else:
            gender_val = str(data["gender"]).strip()
            valid_genders = schema_features.get("gender", {}).get("valid_values", ["Female", "Male"])
            # Cho phép kiểm tra không phân biệt hoa thường
            if not any(gender_val.lower() == g.lower() for g in valid_genders):
                errors.append(f"Trường 'gender' không hợp lệ: '{gender_val}'. Giá trị hợp lệ: {valid_genders}")

        # 3. Kiểm tra tiền sử hút thuốc
        if "smoking_history" in data and data["smoking_history"] is not None:
            smoking_val = str(data["smoking_history"]).strip()
            valid_smokings = schema_features.get("smoking_history", {}).get("valid_values", [])
            if valid_smokings and smoking_val not in valid_smokings:
                errors.append(f"Trường 'smoking_history' không hợp lệ: '{smoking_val}'. Giá trị hợp lệ: {valid_smokings}")

        # 4. Kiểm tra các biến nhị phân nếu có nhập
        bin_fields = ["hypertension", "heart_disease"]
        for b_field in bin_fields:
            if b_field in data and data[b_field] is not None:
                try:
                    b_val = int(data[b_field])
                    if b_val not in [0, 1]:
                        errors.append(f"Trường nhị phân '{b_field}' chỉ nhận giá trị 0 hoặc 1")
                except (ValueError, TypeError):
                    errors.append(f"Trường nhị phân '{b_field}' phải là số nguyên 0 hoặc 1")

        return errors

    def run(self, request: Dict[str, Any]) -> AgentResponse:
        """Tiếp nhận thông số sức khỏe dạng bảng và tính toán xác suất nguy cơ."""
        start_time = time.perf_counter()

        # 1. Kiểm tra tính hợp lệ của đầu vào
        validation_errors = self.validate_inputs(request)
        if validation_errors:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return AgentResponse(
                agent=self.name,
                content={
                    "error": "Dữ liệu đầu vào không hợp lệ hoặc thiếu trường bắt buộc",
                    "details": validation_errors,
                    "invalid_fields": [e.split("'")[1] for e in validation_errors if "'" in e]
                },
                confidence=0.0,
                evidence=[],
                flags=["INVALID_INPUT", "PREDICTION_FAILED"],
                trace={
                    "latency_ms": round(elapsed_ms, 2),
                    "status": "error",
                    "validation_errors": validation_errors
                }
            )

        # 2. Xử lý quy đổi glucose nếu người dùng nhập đơn vị mmol/L
        input_data = dict(request)
        unit = str(input_data.get("glucose_unit", "mg/dL")).strip()
        if unit.lower() in ["mmol/l", "mmol"]:
            # Quy đổi mmol/L sang mg/dL
            input_data["blood_glucose_level"] = float(input_data["blood_glucose_level"]) * 18.0182

        # 3. Chuẩn hóa One-Hot và chạy suy luận mô hình ONNX
        try:
            prob, label = self.artifacts.predict_proba(input_data)
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return AgentResponse(
                agent=self.name,
                content={"error": f"Lỗi suy luận mô hình ONNX: {str(e)}"},
                confidence=0.0,
                flags=["PREDICTION_ERROR"],
                trace={"latency_ms": round(elapsed_ms, 2), "error": str(e)}
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        category = "Nguy cơ cao (Mắc đái tháo đường)" if label == 1 else "Nguy cơ thấp (Bình thường / Tiền ĐTĐ)"

        return AgentResponse(
            agent=self.name,
            content={
                "risk_probability": round(prob, 4),
                "predicted_label": label,
                "risk_category": category,
                "decision_threshold": self.threshold,
                "is_high_risk": bool(label == 1),
                "clinical_metrics_evaluated": {
                    "age": input_data["age"],
                    "bmi": input_data["bmi"],
                    "hbA1c_level": input_data["hbA1c_level"],
                    "blood_glucose_level_mg_dl": round(input_data["blood_glucose_level"], 2)
                }
            },
            confidence=round(prob, 4),
            evidence=[{
                "model_name": "DiabetesMLP (ONNX)",
                "decision_threshold": self.threshold,
                "validation_f1": 0.7993,
                "test_roc_auc": 0.9752
            }],
            flags=["PASS" if label == 0 else "HIGH_RISK_DETECTED"],
            trace={
                "latency_ms": round(elapsed_ms, 2),
                "feature_count_transformed": 17,
                "status": "success"
            }
        )
