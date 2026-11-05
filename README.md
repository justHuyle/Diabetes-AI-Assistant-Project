# Hệ Đa Agent Hỗ Trợ Tư Vấn Cho Bệnh Nhân Tiểu Đường

> **Đề tài:** Phát triển các hệ thống thông minh (PTIT)  
> **Kiến trúc:** Hệ thống đa tác tử phối hợp (Multi-Agent System) với cơ chế giải quyết xung đột có thứ tự ưu tiên bất biến: **An toàn lâm sàng > Tri thức chuẩn > Đề xuất lối sống > Dự báo nguy cơ**.

---

## 1. Giới thiệu tổng quan

Hệ thống được thiết kế theo mô hình ghi chép và hỗ trợ quyết định lâm sàng tại phòng khám, bao gồm **1 Agent Điều phối (Coordinator / Orchestrator)** và **4 Agent chuyên trách**:

1. **PredictionAgent (Tác tử Dự đoán nguy cơ):**
   - Sử dụng mô hình Deep Learning (MLP) đã huấn luyện và đóng gói dưới định dạng chuẩn **ONNX Runtime** (`models/risk_model.onnx`).
   - Chuẩn hóa đầu vào số học qua `scaler.json` theo đúng thứ tự 16 đặc trưng (`feature_schema.json`).
   - Phân loại rủi ro theo ngưỡng quyết định lâm sàng tối ưu $\tau^* = 0.87$ (tối đa hóa $F_1$-score trên tập nhãn mất cân bằng).

2. **KnowledgeAgent (Tác tử Tri thức chuẩn y khoa):**
   - Hệ thống RAG (Retrieval-Augmented Generation) tra cứu ngữ nghĩa dựa trên FAISS vector index (`models/kb_index/`).
   - Sử dụng mô hình Sentence Transformers (`sentence-transformers/all-MiniLM-L6-v2`) đồng nhất với lúc lập chỉ mục.
   - Cơ chế sinh câu trả lời bắt buộc dẫn nguồn trích dẫn y khoa (tên văn bản hướng dẫn, số trang/mục).
   - Tự động chuyển đổi chế độ linh hoạt: Sử dụng Gemini API nếu có khóa `.env`; nếu không có khóa, hoạt động ở **Chế độ Extractive thuần túy** (trích xuất nguyên văn đoạn chuẩn từ Hướng dẫn chẩn đoán và điều trị của Bộ Y tế và ADA).

3. **RecommendationAgent (Tác tử Đề xuất lối sống):**
   - Áp dụng chính sách Học tăng cường (Reinforcement Learning - Q-learning) từ bảng Q-table đã hội tụ (`models/rl_policy.npy`, kích thước 24 trạng thái $\times$ 12 hành động).
   - Rời rạc hóa trạng thái theo nồng độ glucose mao mạch và thời điểm trong ngày (`discretization.json`).
   - **Cam kết y tế:** Chỉ khuyến nghị dinh dưỡng và vận động thể lực phù hợp thể trạng; tuyệt đối **KHÔNG** can thiệp liều thuốc hoặc tiêm insulin.

4. **SafetyAgent (Tác tử An toàn & Kiểm duyệt - Quyền VETO):**
   - Nạp hệ luật xác định từ `models/rules.yaml` (các quy chuẩn ADA / Bộ Y tế Việt Nam).
   - **Luôn thực thi cuối cùng** để rà soát toàn bộ khuyến nghị từ các agent khác.
   - Nắm giữ **quyền VETO (phủ quyết tối cao)**: Tự động ghi đè, chặn đề xuất vận động thể lực khi đường huyết bất thường (nguy cơ hạ đường huyết cấp hoặc nhiễm toan ceton), và kích hoạt cảnh báo khẩn cấp hướng dẫn người bệnh đến ngay cơ sở y tế.

---

## 2. Cây thư mục dự án (Rút gọn)

```text
PROJECT_CODE/
├── backend/                        # Backend FastAPI dịch vụ đa tác tử
│   └── app/
│       ├── agents/                 # 4 Agent chuyên trách & Coordinator
│       │   ├── base.py             # Lớp cơ sở BaseAgent, chuẩn AgentResponse
│       │   ├── coordinator_agent.py # Bộ điều phối, định tuyến, hợp nhất phản hồi
│       │   ├── knowledge_agent.py  # Tác tử RAG & Extractive KB
│       │   ├── prediction_agent.py # Tác tử ONNX MLP phân loại rủi ro
│       │   ├── recommendation_agent.py # Tác tử tra cứu bảng Q-table RL
│       │   └── safety_agent.py     # Tác tử luật an toàn (Quyền VETO)
│       ├── core/
│       │   ├── config.py           # Cấu hình Pydantic BaseSettings, đọc .env
│       │   └── loaders.py          # Nạp mô hình, ném HTTP 503 khi thiếu file
│       ├── schemas/                # Lược đồ dữ liệu Pydantic request/response
│       └── main.py                 # FastAPI app, CORS, API Endpoints, Lifespan
├── data/
│   ├── eval/                       # Dữ liệu đánh giá thực nghiệm
│   │   ├── rag_questions_approved.json # 35 câu hỏi tri thức y khoa chuẩn
│   │   └── safety_cases.json       # 36 ca lâm sàng kiểm thử an toàn
│   └── raw/                        # Tài liệu hướng dẫn lâm sàng Bộ Y tế & ADA
├── docs/                           # Tài liệu thiết kế & quy ước kỹ thuật
│   ├── PROJECT_RULES.md            # 6 quy tắc phát triển cốt lõi bất biến
│   ├── artifact_notes.md           # Đặc tả kỹ thuật mô hình, scaler, Q-table
│   ├── eval_protocol.md            # Giao thức đánh giá 4 biến thể (Ablation)
│   ├── discrepancies.md            # Biên bản đối chiếu sai khác notebook/báo cáo
│   └── report.md                   # Báo cáo đề tài lý thuyết gốc
├── frontend/                       # Giao diện Vite + React + CSS thuần
│   ├── src/
│   │   ├── components/             # Form hồ sơ, phiếu tư vấn, thanh trạng thái
│   │   ├── content/                # fields.vi.json (nhãn tiếng Việt & kịch bản)
│   │   ├── services/api.js         # Kết nối API Backend
│   │   ├── App.jsx                 # Bố cục 2 cột bất đối xứng
│   │   └── App.css                 # CSS thuần (Source Serif 4, IBM Plex Sans)
│   ├── index.html
│   └── package.json
├── models/                         # Trọng số mô hình đã huấn luyện sẵn
│   ├── discretization.json         # Cấu hình rời rạc hóa trạng thái & hành động RL
│   ├── feature_schema.json         # Danh mục 16 đặc trưng ONNX
│   ├── kb_index/                   # Cơ sở tri thức FAISS index & metadata
│   │   ├── index.faiss
│   │   └── metadata.json
│   ├── risk_model.onnx             # Mô hình MLP ONNX
│   ├── rl_policy.npy               # Q-table học tăng cường (24 x 12)
│   ├── rules.yaml                  # Hệ luật an toàn lâm sàng
│   └── scaler.json                 # Hệ số chuẩn hóa StandardScaler
├── reports/
│   ├── figures/                    # Biểu đồ đánh giá 200 dpi & ảnh chụp giao diện
│   │   ├── f_sys_ablation_comparison.png
│   │   ├── f_sys_safety_metrics.png
│   │   ├── f_sys_latency_breakdown.png
│   │   ├── ui_scenario_1.png
│   │   ├── ui_scenario_2.png
│   │   ├── ui_scenario_3.png
│   │   └── ui_error_503.png
│   └── metrics/                    # Dữ liệu định lượng thực tế
│       ├── demo_runs.json          # Kết quả chạy 3 kịch bản demo
│       └── system_eval.json        # Kết quả đánh giá thực nghiệm 4 biến thể
├── scripts/                        # Scripts tự động hóa và thực nghiệm
│   ├── capture_ui.py               # Chụp ảnh màn hình 3 kịch bản bằng Selenium
│   ├── eval_system.py              # Đánh giá 4 biến thể theo docs/eval_protocol.md
│   └── run_demo_scenarios.py       # Chạy 3 kịch bản lâm sàng chuẩn
├── tests/                          # Bộ kiểm thử tự động pytest
│   ├── test_agents.py              # Kiểm thử đơn vị từng Agent
│   ├── test_api_scenarios.py       # Kiểm thử kịch bản tích hợp API & thứ tự ưu tiên
│   └── test_artifacts.py           # Kiểm thử tính toàn vẹn của models/
├── requirements.txt                # Danh mục thư viện Python
└── README.md
```

---

## 3. Hướng dẫn cài đặt và thiết lập môi trường

### 3.1. Yêu cầu hệ thống
- **Hệ điều hành:** Windows 10/11, macOS, hoặc Linux.
- **Python:** Phiên bản **3.11.x** (Khuyến nghị 3.11.9).
- **Node.js:** Phiên bản **v18+** hoặc **v20+** (kèm `npm`).
- **Google Chrome:** Cần cài đặt nếu muốn chạy script chụp ảnh màn hình tự động (`scripts/capture_ui.py`).

### 3.2. Cài đặt môi trường Python (Backend)
```powershell
# 1. Tạo môi trường ảo virtualenv
python -m venv .venv

# 2. Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
# source .venv/bin/activate

# 3. Nâng cấp pip và cài đặt thư viện phụ thuộc
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3. Cài đặt môi trường Node.js (Frontend)
```powershell
cd frontend
npm install
cd ..
```

### 3.4. Cấu hình tệp môi trường `.env`
Tạo tệp `.env` tại thư mục gốc của dự án (`PROJECT_CODE/.env`):
```ini
# Cấu hình khóa Gemini API (Tùy chọn)
# Nếu cung cấp khóa, KnowledgeAgent sẽ sử dụng LLM để sinh lời văn giải thích tự nhiên kèm trích dẫn nguồn.
# Nếu bỏ trống hoặc không có mạng, hệ thống tự động chạy ở CHẾ ĐỘ EXTRACTIVE (trích đoạn nguyên văn có metadata).
GEMINI_API_KEY=your_gemini_api_key_here

# Cấu hình môi trường chạy
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3.5. Kiểm tra vị trí các tệp mô hình trong `models/`
Đảm bảo thư mục `models/` có đầy đủ 7 thành phần bắt buộc (đã huấn luyện từ notebook, không huấn luyện lại):
- `models/risk_model.onnx`: Mô hình phân loại nguy cơ ONNX.
- `models/scaler.json`: Trung bình và phương sai chuẩn hóa 16 đặc trưng.
- `models/feature_schema.json`: Thứ tự và khoảng giá trị hợp lệ của đặc trưng.
- `models/kb_index/index.faiss` & `models/kb_index/metadata.json`: Chỉ mục vector tri thức.
- `models/rl_policy.npy`: Bảng Q-table đề xuất lối sống kích thước 24 $\times$ 12.
- `models/discretization.json`: Ánh xạ trạng thái và hành động RL.
- `models/rules.yaml`: Hệ luật an toàn lâm sàng.

> **Lưu ý nguyên tắc docs/PROJECT_RULES.md:** Nếu thiếu bất kỳ tệp mô hình nào, backend sẽ từ chối sinh dữ liệu giả và trả về mã lỗi `HTTP 503 Service Unavailable`.

---

## 4. Hướng dẫn vận hành hệ thống

### 4.1. Khởi động Backend API Server
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
# Hoặc chỉ định trực tiếp:
# .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`
- Endpoint kiểm tra sức khỏe: `http://127.0.0.1:8000/api/health`

### 4.2. Khởi động Frontend Web Application
Mở một cửa sổ dòng lệnh thứ hai:
```powershell
cd frontend
npm run dev
```
- Ứng dụng giao diện mở tại: `http://localhost:5173`
- Giao diện được thiết kế theo phong cách **Tờ phiếu khám phòng khám** (Clinical Record Sheet), bảng màu giấy ấm cổ điển `#F6F3EE`, phông chữ học thuật `Source Serif 4` và `IBM Plex Sans`, hoàn toàn không phụ thuộc vào kết nối mạng bên ngoài (font đã được nhúng cục bộ qua `@fontsource`).

---

## 5. Danh mục API Endpoints thực tế

| Phương thức | Đường dẫn Endpoint | Mô tả chức năng | Mã trạng thái |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Kiểm tra tình trạng nạp của 4 mô hình AI và chế độ RAG | `200 OK` / `503 Unavailable` |
| `POST` | `/api/consult` | Tiếp nhận câu hỏi và chỉ số đo, điều phối 4 tác tử | `200 OK` / `503 Unavailable` |
| `POST` | `/api/predict` | Điểm cuối chuyên trách gọi ONNX MLP dự báo nguy cơ | `200 OK` / `422 Unprocessable` |
| `GET` | `/api/rules` | Truy xuất toàn bộ danh mục luật an toàn lâm sàng (`rules.yaml`) | `200 OK` |
| `GET` | `/api/trace/{id}` | Truy xuất toàn bộ vết thực thi (Execution Trace) của một phiên | `200 OK` / `404 Not Found` |

---

## 6. Kiểm thử tự động (Unit & Integration Tests)

Hệ thống cung cấp bộ kiểm thử toàn diện với **37 ca kiểm thử** bao phủ toàn bộ các mô hình, các tác tử độc lập, kịch bản tích hợp và thứ tự ưu tiên:

```powershell
# Chạy toàn bộ test suite
pytest -v tests/
```

- `tests/test_artifacts.py`: Kiểm thử tính toàn vẹn của mô hình ONNX, Q-table shape `(24, 12)`, FAISS index vector, và luật an toàn.
- `tests/test_agents.py`: Kiểm thử độc lập từng agent (Prediction, Knowledge, Recommendation, Safety).
- `tests/test_api_scenarios.py`: Kiểm thử tích hợp 3 kịch bản mẫu, kịch bản kê đơn thuốc bị chặn, kịch bản lỗi thiếu model trả HTTP 503, và kiểm tra quyền VETO của SafetyAgent.

---

## 7. Đánh giá thực nghiệm và Nghiên cứu cắt bỏ (Ablation Study)

Hệ thống được đánh giá định lượng nghiêm ngặt theo giao thức `docs/eval_protocol.md` trên 4 biến thể:
- **V1_Full:** Hệ thống hoàn chỉnh (Đầy đủ 4 Agent).
- **V2_NoRAG:** Tắt tác tử Tri thức chuẩn (Zero-Retrieval).
- **V3_NoSafety:** Tắt tác tử An toàn lâm sàng (Không thẩm định, không phủ quyết).
- **V4_NoRL:** Thay thế Q-table bằng chiến lược Heuristic cơ bản.

### 7.1. Chạy kịch bản Demo
```powershell
python scripts/run_demo_scenarios.py
```
Kết quả được lưu tại: `reports/metrics/demo_runs.json`.

### 7.2. Chạy đánh giá toàn diện 4 biến thể và vẽ biểu đồ
```powershell
python scripts/eval_system.py
```
Kết quả số liệu thực nghiệm được lưu tại: `reports/metrics/system_eval.json` và xuất 3 biểu đồ độ phân giải 200 dpi tại `reports/figures/`:
1. `f_sys_ablation_comparison.png`: So sánh tỷ lệ vi phạm an toàn, độ trích dẫn chính xác và phần thưởng lâm sàng giữa 4 biến thể.
2. `f_sys_safety_metrics.png`: Phân tích chuyên sâu năng lực an toàn (Độ nhạy cấp cứu 100%, Tỷ lệ bỏ sót 0%).
3. `f_sys_latency_breakdown.png`: Thời gian xử lý trung bình và phân vị p95 của từng tác tử.

### 7.3. Chụp ảnh màn hình giao diện thực tế
```powershell
python scripts/capture_ui.py
```
Tự động lưu ảnh giao diện độ nét cao tại:
- `reports/figures/ui_scenario_1.png`: Kịch bản 1 - Hỏi tiêu chuẩn chẩn đoán (Trích dẫn tài liệu y khoa ADA/Bộ Y tế).
- `reports/figures/ui_scenario_2.png`: Kịch bản 2 - Tư vấn chỉ số lâm sàng (Dự báo nguy cơ, Đề xuất dinh dưỡng và vận động).
- `reports/figures/ui_scenario_3.png`: Kịch bản 3 - Tình huống cấp cứu hạ đường huyết (Kích hoạt quyền VETO, cảnh báo đỏ).
- `reports/figures/ui_error_503.png`: Màn hình cảnh báo khi thiếu tệp mô hình chuẩn (Không sinh dữ liệu giả theo `docs/PROJECT_RULES.md`).
