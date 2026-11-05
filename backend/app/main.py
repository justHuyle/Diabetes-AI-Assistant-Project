import os
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.loaders import (
    ModelContainer,
    ModelLoadError,
    load_all_artifacts,
)
from backend.app.agents.coordinator_agent import CoordinatorAgent, TRACE_STORE
from backend.app.schemas.consult import (
    ConsultRequest,
    PredictRequest,
    ConsultResponse,
    DoctorContactRequest,
    DoctorContactResponse,
)

# Bộ nhớ lưu trữ yêu cầu chuyển tiếp / liên hệ bác sĩ
DOCTOR_REFERRAL_STORE: Dict[str, Dict[str, Any]] = {}

DOCTOR_DIRECTORY = [
    {
        "id": "doc_bm_01",
        "name": "PGS. TS. BS. Nguyễn Khoa Diệu Vân",
        "title": "Nguyên Trưởng khoa Nội tiết - Đái tháo đường",
        "facility": "Khoa Nội tiết - Đái tháo đường, Bệnh viện Bạch Mai (Hà Nội)",
        "phone": "024.3869.3731",
        "address": "Số 78 Giải Phóng, Phương Mai, Đống Đa, Hà Nội",
        "available_hours": "07:30 - 17:00 (Thứ 2 - Thứ 6)"
    },
    {
        "id": "doc_dhy_02",
        "name": "PGS. TS. BS. Đỗ Trung Quân",
        "title": "Chủ tịch Hội Nội tiết & Đái tháo đường Hà Nội, Bệnh viện ĐHY Hà Nội",
        "facility": "Phòng khám Đa khoa, Bệnh viện Đại học Y Hà Nội",
        "phone": "1900.6422",
        "address": "Số 1 Tôn Thất Tùng, Đống Đa, Hà Nội",
        "available_hours": "07:00 - 16:30 (Thứ 2 - Thứ 7)"
    },
    {
        "id": "doc_cr_03",
        "name": "TS. BS. Lâm Văn Hoàng",
        "title": "Trưởng khoa Nội tiết, Bệnh viện Chợ Rẫy",
        "facility": "Khoa Nội tiết, Bệnh viện Chợ Rẫy (TP. Hồ Chí Minh)",
        "phone": "028.3855.4137",
        "address": "Số 201B Nguyễn Chí Thanh, Phường 12, Quận 5, TP. HCM",
        "available_hours": "07:00 - 16:00 (Thứ 2 - Thứ 6)"
    },
    {
        "id": "emergency_hotline",
        "name": "Tổng đài Cấp cứu Y tế Ngoại viện",
        "title": "Trực ban Cấp cứu 24/7 (Đường huyết <70 mg/dL hoặc >250 mg/dL)",
        "facility": "Mạng lưới Cấp cứu Y tế 115 Toàn quốc",
        "phone": "115",
        "address": "Phục vụ 24/7 trên toàn quốc",
        "available_hours": "24/24h hàng ngày"
    }
]

# Biến toàn cục lưu trữ container và coordinator
app_state: Dict[str, Any] = {
    "container": None,
    "coordinator": None,
    "model_status": {
        "risk_model": "uninitialized",
        "knowledge_base": "uninitialized",
        "rl_recommendation": "uninitialized",
        "safety_rules": "uninitialized",
        "gemini_api": "extractive_mode"
    }
}


def initialize_app_models():
    """Hàm khởi tạo và nạp mô hình vào app_state."""
    if settings.GEMINI_API_KEY:
        app_state["model_status"]["gemini_api"] = "configured"
    else:
        app_state["model_status"]["gemini_api"] = "extractive_mode"

    container = load_all_artifacts()
    app_state["container"] = container
    app_state["coordinator"] = CoordinatorAgent(container=container)
    app_state["model_status"]["risk_model"] = "ready"
    app_state["model_status"]["knowledge_base"] = "ready"
    app_state["model_status"]["rl_recommendation"] = "ready"
    app_state["model_status"]["safety_rules"] = "ready"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi tạo và nạp toàn bộ các mô hình khi máy chủ khởi động."""
    try:
        initialize_app_models()
    except ModelLoadError as e:
        app_state["model_status"]["error_detail"] = str(e)
    except Exception as e:
        app_state["model_status"]["error_detail"] = str(e)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Hệ đa agent hỗ trợ tư vấn cho bệnh nhân tiểu đường - PTIT",
    lifespan=lifespan
)

# Cấu hình CORS cho phép giao diện Frontend (Vite/React) kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ModelLoadError)
async def model_load_error_handler(request, exc: ModelLoadError):
    """Bắt lỗi thiếu model và trả HTTP 503 Service Unavailable."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Dịch vụ chưa sẵn sàng do thiếu tệp mô hình/cấu hình",
            "message": exc.message,
            "missing_file": str(exc.missing_path) if exc.missing_path else None
        }
    )


def get_coordinator() -> CoordinatorAgent:
    """Dependency helper lấy CoordinatorAgent, tự động nạp nếu chưa khởi tạo."""
    coordinator = app_state.get("coordinator")
    if not coordinator:
        try:
            initialize_app_models()
            coordinator = app_state.get("coordinator")
        except ModelLoadError as e:
            raise e
        except Exception as e:
            raise ModelLoadError(f"Không thể khởi tạo các mô hình: {str(e)}")

    if not coordinator:
        raise ModelLoadError("Hệ đa agent chưa được khởi tạo đầy đủ hoặc thiếu tệp model.")
    return coordinator


# ==============================================================================
# DANH MỤC API ENDPOINTS
# ==============================================================================

@app.post("/api/consult", response_model=ConsultResponse, status_code=status.HTTP_200_OK)
async def consult(request: ConsultRequest):
    """Điểm cuối tiếp nhận câu hỏi và chỉ số lâm sàng, điều phối 4 agent tư vấn."""
    coordinator = get_coordinator()
    try:
        response = coordinator.consult(request)
        return response
    except ModelLoadError as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi trong quá trình điều phối tư vấn: {str(e)}"
        )


@app.post("/api/predict", status_code=status.HTTP_200_OK)
async def predict_risk(request: PredictRequest):
    """Điểm cuối chuyên trách gọi mô hình Deep Learning ONNX để dự báo rủi ro."""
    coordinator = get_coordinator()
    pred_agent = coordinator.prediction_agent

    input_data = request.model_dump()
    resp = pred_agent.run(input_data)

    if "INVALID_INPUT" in resp.flags or "PREDICTION_FAILED" in resp.flags:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=resp.content
        )

    return {
        "status": "success",
        "prediction": resp.content,
        "confidence": resp.confidence,
        "evidence": resp.evidence,
        "trace": resp.trace
    }


@app.get("/api/rules", status_code=status.HTTP_200_OK)
async def get_rules():
    """Truy vấn danh mục các luật y khoa và ngưỡng an toàn trong rules.yaml."""
    coordinator = get_coordinator()
    rules = coordinator.safety_agent.rules
    return {
        "status": "success",
        "total_rules": len(rules),
        "rules": rules
    }


@app.get("/api/health")
async def health_check():
    """Kiểm tra tình trạng sẵn sàng của hệ thống và từng mô hình thành phần."""
    statuses = dict(app_state["model_status"])
    is_healthy = all(
        statuses.get(m) == "ready"
        for m in ["risk_model", "knowledge_base", "rl_recommendation", "safety_rules"]
    )

    if not is_healthy:
        try:
            initialize_app_models()
            statuses = dict(app_state["model_status"])
            is_healthy = True
        except ModelLoadError as e:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "degraded",
                    "message": "Một hoặc nhiều mô hình chưa sẵn sàng",
                    "details": statuses,
                    "error": str(e)
                }
            )

    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "models": statuses
    }


@app.get("/api/trace/{consultation_id}", status_code=status.HTTP_200_OK)
async def get_trace(consultation_id: str):
    """Truy vấn vết thực thi của một phiên tư vấn theo ID."""
    if consultation_id not in TRACE_STORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy vết thực thi cho phiên tư vấn ID '{consultation_id}'"
        )
    return {
        "status": "success",
        "trace": TRACE_STORE[consultation_id]
    }


@app.get("/api/doctors", status_code=status.HTTP_200_OK)
async def get_doctor_directory():
    """Danh bạ các đơn vị và chuyên gia Nội tiết - Đái tháo đường phối hợp."""
    return {
        "status": "success",
        "total": len(DOCTOR_DIRECTORY),
        "doctors": DOCTOR_DIRECTORY
    }


@app.post("/api/doctor/contact", response_model=DoctorContactResponse, status_code=status.HTTP_200_OK)
async def contact_doctor(request: DoctorContactRequest):
    """Tiếp nhận yêu cầu chuyển tiếp hồ sơ và liên hệ Bác sĩ chuyên khoa."""
    phone_cleaned = request.patient_phone.strip()
    if not phone_cleaned or len(phone_cleaned) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Vui lòng cung cấp số điện thoại liên hệ hợp lệ để bác sĩ có thể gọi lại."
        )

    referral_id = f"REF-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.now().isoformat()

    record = {
        "referral_id": referral_id,
        "consultation_id": request.consultation_id,
        "patient_name": request.patient_name,
        "patient_phone": phone_cleaned,
        "facility_or_doctor": request.facility_or_doctor,
        "patient_notes": request.patient_notes,
        "clinical_summary": request.clinical_summary,
        "is_emergency": request.is_emergency,
        "created_at": now_iso,
        "status": "received"
    }
    DOCTOR_REFERRAL_STORE[referral_id] = record

    if request.is_emergency:
        msg = "YÊU CẦU CẤP CỨU ĐÃ ĐƯỢC CHUYỂN TỚI BÁC SĨ TRỰC VÀ KHOA CẤP CỨU LÂM SÀNG!"
        instructions = "CẢNH BÁO: Với dấu hiệu hạ đường huyết sâu hoặc nguy cơ toan ceton cấp, người nhà vui lòng GỌI NGAY CẤP CỨU 115 hoặc đưa bệnh nhân đến khoa Cấp cứu gần nhất, không chờ đợi gọi lại!"
    else:
        msg = "Hồ sơ tư vấn và thông tin liên hệ đã được chuyển thành công tới Bác sĩ Chuyên khoa Nội tiết."
        instructions = f"Mã tiếp nhận hồ sơ: {referral_id}. Bác sĩ hoặc điều dưỡng phụ trách tại {request.facility_or_doctor} sẽ chủ động liên hệ lại qua số điện thoại {phone_cleaned} trong thời gian sớm nhất."

    return DoctorContactResponse(
        referral_id=referral_id,
        status="received",
        created_at=now_iso,
        message=msg,
        instructions=instructions,
        emergency_hotline="115"
    )
