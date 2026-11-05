# scripts/run_demo_scenarios.py
# Thực thi 3 kịch bản lâm sàng mẫu từ báo cáo và lưu vết vào reports/metrics/demo_runs.json

import json
import os
import sys
import time
from datetime import datetime

# Cấu hình UTF-8 cho console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Đảm bảo đường dẫn gốc của project nằm trong sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.agents.coordinator_agent import CoordinatorAgent
from backend.app.schemas import ConsultRequest


def run_demo():
    print("=" * 70)
    print("CHẠY THỰC NGHIỆM 3 KỊCH BẢN LÂM SÀNG TRONG BÁO CÁO")
    print("=" * 70)

    coordinator = CoordinatorAgent()

    scenarios = [
        {
            "id": "scenario_1",
            "name": "Kịch bản 1: Hỏi đáp kiến thức y khoa chuẩn mực (ADA / Bộ Y tế)",
            "description": "Bệnh nhân tra cứu tiêu chuẩn chẩn đoán đái tháo đường dựa trên nồng độ đường huyết và HbA1c.",
            "request": ConsultRequest(
                message="Tiêu chuẩn chẩn đoán đái tháo đường theo chỉ số đường huyết và HbA1c là gì?",
                metrics=None
            )
        },
        {
            "id": "scenario_2",
            "name": "Kịch bản 2: Nhập chỉ số lâm sàng nhận tư vấn nguy cơ và lối sống",
            "description": "Bệnh nhân 45 tuổi, thừa cân nhẹ (BMI 27.5), HbA1c 6.8%, đường huyết 135 mg/dL. Xin tư vấn chế độ ăn và vận động.",
            "request": ConsultRequest(
                message="Tôi 45 tuổi, BMI 27.5, HbA1c 6.8, đường huyết 135 mg/dL. Xin tư vấn chế độ ăn và vận động",
                metrics={
                    "age": 45,
                    "gender": "Male",
                    "bmi": 27.5,
                    "hbA1c_level": 6.8,
                    "blood_glucose_level": 135.0,
                    "glucose_unit": "mg/dL",
                    "hypertension": 0,
                    "heart_disease": 0,
                    "smoking_history": "never",
                    "time_of_day": "morning"
                }
            )
        },
        {
            "id": "scenario_3",
            "name": "Kịch bản 3: Chỉ số nguy hiểm kích hoạt đường rút gọn cấp cứu",
            "description": "Bệnh nhân xuất hiện triệu chứng vã mồ hôi, run rẩy, đường huyết mao mạch giảm còn 52 mg/dL (< 70 mg/dL).",
            "request": ConsultRequest(
                message="Tôi thấy vã mồ hôi và run tay chân, đo đường huyết chỉ còn 52 mg/dL!",
                metrics={
                    "blood_glucose_level": 52.0,
                    "glucose_unit": "mg/dL",
                    "time_of_day": "morning"
                }
            )
        }
    ]

    results = {
        "execution_timestamp": datetime.now().isoformat(),
        "total_scenarios": len(scenarios),
        "scenarios_data": []
    }

    for idx, sc in enumerate(scenarios, 1):
        print(f"\n--- [{idx}/{len(scenarios)}] {sc['name']} ---")
        t0 = time.perf_counter()
        response = coordinator.consult(sc["request"])
        latency = (time.perf_counter() - t0) * 1000

        res_dict = response.model_dump()

        sc_record = {
            "scenario_id": sc["id"],
            "name": sc["name"],
            "description": sc["description"],
            "input": {
                "message": sc["request"].message,
                "metrics": sc["request"].metrics
            },
            "output": res_dict,
            "measured_client_latency_ms": round(latency, 2)
        }
        results["scenarios_data"].append(sc_record)

        print(f"Phiên tư vấn ID : {response.consultation_id}")
        print(f"Ý định phân loại: {response.intent}")
        print(f"Trạng thái      : {response.status}")
        print(f"Cấp cứu phát hiện: {response.emergency_detected}")
        print(f"Tổng thời gian  : {latency:.2f} ms")
        if response.emergency_alert:
            print(f"CẢNH BÁO CẤP CỨU: {response.emergency_alert[:120]}...")

    output_path = os.path.join(BASE_DIR, "reports", "metrics", "demo_runs.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"ĐÃ LƯU KẾT QUẢ THỰC NGHIỆM TẠI: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
