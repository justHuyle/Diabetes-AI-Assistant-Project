# TỔNG HỢP THÔNG SỐ VÀ ĐẶC TẢ ARTIFACTS CÁC MÔ HÌNH (ARTIFACT NOTES)
*Dự án: Hệ đa agent hỗ trợ tư vấn cho bệnh nhân tiểu đường*
*Phiên bản: 1.0.0 - Giai đoạn P1: Model Loading & Artifact Verification*

---

## 1. MÔ HÌNH DỰ ĐOÁN NGUY CƠ (AGENT DỰ ĐOÁN - DEEP LEARNING ONNX)

### a. Tệp Artifacts
- **Mô hình**: `models/risk_model.onnx` (17.1 KB)
- **Bộ chuẩn hóa**: `models/scaler.json` (1.78 KB)
- **Lược đồ đặc trưng**: `models/feature_schema.json` (4.13 KB)

### b. Danh sách 13 đặc trưng thô, thứ tự và đơn vị
Hệ thống tiếp nhận 13 trường thông tin từ người dùng:
1. `age`: float, đơn vị: **tuổi (năm)**, miền giá trị hợp lệ: $[0.08, 120.0]$.
2. `bmi`: float, đơn vị: **$\text{kg/m}^2$** (Chỉ số khối cơ thể), miền hợp lệ: $[10.0, 100.0]$.
3. `hbA1c_level`: float, đơn vị: **$\%$** (Tỷ lệ hemoglobin glycated), miền hợp lệ: $[3.0, 18.0]$.
4. `blood_glucose_level`: float, đơn vị: **$\text{mg/dL}$** (Nồng độ đường huyết), miền hợp lệ: $[40.0, 600.0]$.
5. `gender`: string, giá trị hợp lệ: `['Female', 'Male']`.
6. `smoking_history`: string, giá trị hợp lệ: `['No Info', 'never', 'former', 'current', 'not current', 'ever']`.
7. `hypertension`: int binary, `0`: Không tăng huyết áp, `1`: Có tăng huyết áp.
8. `heart_disease`: int binary, `0`: Không có bệnh tim mạch, `1`: Có bệnh tim mạch.
9. `race:AfricanAmerican`: int binary, $0$ hoặc $1$.
10. `race:Asian`: int binary, $0$ hoặc $1$ (Mặc định $1$ đối với bệnh nhân Việt Nam).
11. `race:Caucasian`: int binary, $0$ hoặc $1$.
12. `race:Hispanic`: int binary, $0$ hoặc $1$.
13. `race:Other`: int binary, $0$ hoặc $1$.

### c. Quy trình chuẩn hóa đầu vào thành vector 17 chiều
Mô hình ONNX nhận tensor float32 kích thước `[batch_size, 17]`. Phép biến đổi được định nghĩa trong `models/scaler.json`:
- **4 biến số học** được chuẩn hóa z-score: $z = \frac{x - \mu}{\sigma}$
  - `num__age`: $\mu = 41.858765, \sigma = 22.520828$
  - `num__bmi`: $\mu = 27.297406, \sigma = 6.614157$
  - `num__hbA1c_level`: $\mu = 5.526093, \sigma = 1.070871$
  - `num__blood_glucose_level`: $\mu = 138.044958, \sigma = 40.660407$
- **1 biến giới tính One-Hot (bỏ 'Female')**:
  - `cat__gender_Male`: $1.0$ nếu Male, $0.0$ nếu Female.
- **5 biến thói quen hút thuốc One-Hot (bỏ 'No Info')**:
  - `cat__smoking_history_current`
  - `cat__smoking_history_ever`
  - `cat__smoking_history_former`
  - `cat__smoking_history_never`
  - `cat__smoking_history_not current`
- **7 biến nhị phân (Passthrough)**:
  - `bin__hypertension`
  - `bin__heart_disease`
  - `bin__race:AfricanAmerican`
  - `bin__race:Asian`
  - `bin__race:Caucasian`
  - `bin__race:Hispanic`
  - `bin__race:Other`

### d. Ngưỡng quyết định đã chọn (Decision Threshold)
- **Ngưỡng tối ưu**: $\mathbf{\tau^* = 0.87}$ (dò tìm độc lập trên tập Validation nhằm tối ưu hóa $F_1\text{-score}$).
- **Quy tắc phân loại**:
  - Nếu $\hat{y} = P(\text{Diabetes}=1) \ge 0.87 \rightarrow \text{Nhãn } 1$ (Nguy cơ Đái tháo đường cao).
  - Nếu $\hat{y} < 0.87 \rightarrow \text{Nhãn } 0$ (Nguy cơ thấp / Không mắc).
- **Chỉ số kiểm chứng trên tập Test Holdout (NB01 Cell 5.1)**:
  - Accuracy: $0.9705$
  - Precision: $0.9512$
  - Recall: $0.6878$
  - $F_1\text{-score}$: $0.7984$
  - ROC-AUC: $0.9752$
  - Brier score: $0.0674$

---

## 2. CƠ SỞ TRI THỨC VÀ RAG (AGENT TRI THỨC)

### a. Tệp Artifacts
- **Vector Index**: `models/kb_index/kb_production_index.pkl` (51.2 KB)
- **Siêu dữ liệu Chunks**: `models/kb_index/kb_chunks_metadata.json` (19.8 KB, 24 chunks)
- **Cấu hình KB**: `models/kb_index/kb_config.json`
- **Tập câu hỏi kiểm thử đã duyệt**: `data/eval/rag_questions_approved.json` (35 câu)

### b. Mô hình Embedding
- **Tên mô hình**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Số chiều vector**: $d = 384$ chiều.
- **Độ đo khoảng cách**: Cosine Similarity thông qua phép nhân ma trận $L_2\text{-normalized}$ (NumPy / FAISS `IndexFlatIP`).

### c. Cấu hình chia đoạn (Chunking Configuration)
- **Cấu hình tối ưu được chọn**: **Config B (Balanced)**
- **Kích thước đoạn**: $600$ ký tự.
- **Độ dài gối đầu (Overlap)**: $120$ ký tự.
- **Chiến lược ngắt ranh giới**: Boundary-Aware Text Splitter, tự động dò tìm các điểm ngắt tự nhiên (`\n\n`, `\n`, `. `, `; `, `, `).
- **Tài liệu nguồn được nạp (6 tài liệu chuẩn)**:
  - `DOC_01_ADA_DIAGNOSIS`: Tiêu chuẩn chẩn đoán ADA.
  - `DOC_02_MOH_VN_GUIDELINE`: Hướng dẫn chẩn đoán và điều trị ĐTĐ típ 2 (Bộ Y tế Việt Nam).
  - `DOC_03_WHO_SCREENING`: Hướng dẫn sàng lọc và dự phòng (WHO).
  - `DOC_04_NIDDK_HYPOGLYCEMIA`: Cấp cứu hạ đường huyết và quy tắc 15-15 (NIDDK).
  - `DOC_05_ADA_LIFESTYLE`: Quản lý dinh dưỡng và vận động (ADA).
  - `DOC_06_MOH_SAFETY_COMPLICATIONS`: Theo dõi biến chứng và giới hạn an toàn AI (Bộ Y tế).

---

## 3. HỌC TĂNG CƯỜNG VÀ HỆ LUẬT (AGENT ĐỀ XUẤT & AGENT AN TOÀN)

### a. Tệp Artifacts
- **Chính sách tối ưu**: `models/rl_policy.npy` ($24$ giá trị hành động tối ưu)
- **Bảng Q-Table**: `models/q_table.npy` (Ma trận kích thước $24 \times 12$)
- **Lược đồ rời rạc hóa**: `models/discretization.json` (7.75 KB)
- **Hệ luật an toàn**: `models/rules.yaml` (2.3 KB)

### b. Rời rạc hóa không gian trạng thái ($24$ trạng thái)
$$\text{state\_id} = \text{glucose\_bin} \times 4 + \text{time\_bin}$$
- **6 Bins Glucose**:
  - Bin 0 ($< 70\text{ mg/dL}$): Hạ đường huyết cấp tính (Severe Hypoglycemia)
  - Bin 1 ($70 - 99\text{ mg/dL}$): Cận bình thường thấp (Borderline Low)
  - Bin 2 ($100 - 140\text{ mg/dL}$): Khoảng mục tiêu tối ưu (Target Range - TIR)
  - Bin 3 ($141 - 180\text{ mg/dL}$): Đỉnh sau ăn chấp nhận được (Acceptable Postprandial)
  - Bin 4 ($181 - 250\text{ mg/dL}$): Tăng đường huyết cao (Elevated Hyperglycemia)
  - Bin 5 ($> 250\text{ mg/dL}$): Tăng đường huyết rất cao (Severe Hyperglycemia / DKA Risk)
- **4 Bins Khung giờ sinh học**:
  - 0: Buổi Sáng (trước/sau ăn sáng)
  - 1: Buổi Trưa (trước/sau ăn trưa)
  - 2: Buổi Tối (trước/sau ăn tối)
  - 3: Buổi Đêm (trước khi đi ngủ)

### c. Không gian 12 hành động lối sống
Gồm tổ hợp 3 tham số lối sống: $\text{Carb} \in \{\text{LOW}, \text{MODERATE}, \text{HIGH}\} \times \text{Exercise} \in \{\text{NONE}, \text{MODERATE}\} \times \text{Remind} \in \{\text{False}, \text{True}\}$.
Tuyệt đối không can thiệp đơn thuốc hay insulin.

---

## 4. BẢNG ÁNH XẠ: ĐẦU VÀO NGƯỜI DÙNG NHẬP $\Rightarrow$ ĐẦU VÀO TỪNG AGENT

| Trường dữ liệu người dùng nhập | Kiểu dữ liệu / Đơn vị | Ánh xạ Agent Dự đoán (DL) | Ánh xạ Agent Tri thức (KB) | Ánh xạ Agent Đề xuất (RL) | Ánh xạ Agent An toàn (Safety) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `query` (Câu hỏi tự nhiên) | `string` | Không dùng | **Đầu vào chính** để trích xuất vector truy vấn | Không dùng | Kiểm tra từ khóa cấm kê đơn thuốc |
| `blood_glucose_level` | `float` ($\text{mmol/L}$ hoặc $\text{mg/dL}$) | Chuẩn hóa vào `num__blood_glucose_level` | Không dùng | Quy đổi sang $\text{mg/dL} \rightarrow$ tính `glucose_bin` ($0..5$) | So sánh ngưỡng an toàn ($<100, >180, <80, <70, >250$) |
| `glucose_unit` | `string` (`'mmol/L'` hoặc `'mg/dL'`) | Chuyển thành $\text{mg/dL}$ | Không dùng | Chuyển thành $\text{mg/dL}$ | Chuyển thành $\text{mg/dL}$ |
| `time_of_day` | `string` / `int` (Sáng, Trưa, Tối, Đêm) | Không dùng | Không dùng | Ánh xạ sang `time_bin` ($0..3$) | Không dùng |
| `age` | `float` (tuổi) | Chuẩn hóa vào `num__age` | Không dùng | Không dùng | Không dùng |
| `gender` | `string` (`'Female'`, `'Male'`) | Mã hóa `cat__gender_Male` ($0$ hoặc $1$) | Không dùng | Không dùng | Không dùng |
| `bmi` | `float` ($\text{kg/m}^2$) | Chuẩn hóa vào `num__bmi` | Không dùng | Không dùng | Không dùng |
| `hbA1c_level` | `float` ($\%$) | Chuẩn hóa vào `num__hbA1c_level` | Không dùng | Không dùng | Cảnh báo mạn tính nếu $\ge 6.5\%$ |
| `hypertension` | `int` ($0$ hoặc $1$) | `bin__hypertension` | Không dùng | Không dùng | Không dùng |
| `heart_disease` | `int` ($0$ hoặc $1$) | `bin__heart_disease` | Không dùng | Không dùng | Không dùng |
| `smoking_history` | `string` (`never`, `former`, `current`,...) | One-Hot $5$ cột `cat__smoking_history_*` | Không dùng | Không dùng | Không dùng |
| `race` | `string` | Mặc định `race:Asian = 1`, còn lại $0$ | Không dùng | Không dùng | Không dùng |

---

## 5. CÁC ĐIỂM CHƯA THỂ ÁNH XẠ VÀ NGUYÊN TẮC BẤT BIẾN (KHÔNG BỊA SỐ LIỆU)

1. **Thiếu biến khảo sát dịch tễ khi người dùng chỉ hỏi bệnh**:
   - Nếu người dùng chỉ gửi câu hỏi hội thoại hoặc chỉ nhập kết quả thử que đường huyết nhanh (ví dụ: *"Tôi vừa đo được 6.2 mmol/L sau bữa trưa"*):
   - **Chỗ KHÔNG THỂ ánh xạ**: Các biến `age`, `bmi`, `hbA1c_level`, `hypertension`, `heart_disease`, `smoking_history` không thể tự suy ra từ câu hỏi văn bản.
   - **Xử lý bắt buộc**:
     - **TUYỆT ĐỐI KHÔNG TỰ ĐIỀN GIÁ TRỊ TRUNG BÌNH (Mean Imputation)** để ép chạy mô hình Deep Learning.
     - Hệ thống kích hoạt bình thường: Agent Tri thức (trả lời kiến thức), Agent Đề xuất (tư vấn lối sống theo đường huyết), Agent An toàn (kiểm duyệt).
     - Đối với Agent Dự đoán: Phản hồi cờ `prediction_skipped = True` kèm thông báo: *"Chưa đủ dữ liệu lâm sàng bắt buộc (tuổi, BMI, HbA1c, bệnh nền) để dự đoán nguy cơ mắc bệnh"*.
2. **Biến BMI và Activity trong công thức lý thuyết của Báo cáo**:
   - Báo cáo lý thuyết Chương 3 ghi: $s = \langle \text{Glucose}, \text{BMI}, \text{Activity} \rangle$.
   - Mô hình Q-table thực tế được huấn luyện chỉ dựa trên: $s = \langle \text{glucose\_bin}, \text{time\_bin} \rangle$.
   - **Xử lý**: Hệ thống chỉ ánh xạ `glucose` và `time_bin` vào Q-table. Không tự chế thuật toán thêm chiều BMI vào Q-table hiện có.
