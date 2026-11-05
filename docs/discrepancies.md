# BẢNG ĐỐI CHIẾU VÀ ĐIỂM SAI LỆCH KỸ THUẬT (DISCREPANCIES LOG)
*Dự án: Hệ đa agent hỗ trợ tư vấn cho bệnh nhân tiểu đường*
*Tài liệu tham chiếu gốc: `docs/report.md` (Chương 3 và 4)*
*Hiện trạng thực tế: Dữ liệu và mô hình tại `models/`, `notebooks/`*

---

## 1. SAI KHÁC VỀ KHÔNG GIAN TRẠNG THÁI RL (AGENT ĐỀ XUẤT)

### Hiện tượng:
- **Đặc tả trong `docs/report.md` (Chương 2 dòng 133, Chương 3 dòng 267):**
  Trạng thái RL được biểu diễn lý thuyết là:
  $$s = \langle \text{Glucose}, \text{BMI}, \text{Activity} \rangle$$
- **Thực tế trong mô hình đã huấn luyện (`models/rl_policy.npy`, `models/discretization.json`, `notebooks/N3.ipynb`):**
  Không gian trạng thái có kích thước 24 ($\text{cardinality} = 24$), tính theo công thức:
  $$\text{state\_id} = \text{glucose\_bin} \times 4 + \text{time\_bin}$$
  Gồm 6 khoảng glucose ($<70, 70-99, 100-140, 141-180, 181-250, >250\text{ mg/dL}$) và 4 khung giờ trong ngày (Sáng, Trưa, Tối, Đêm). Không chứa chiều `BMI` và không chứa chiều `Activity`.

### Đề xuất xử lý:
- Giữ nguyên mô hình Q-table 24 trạng thái đã hội tụ thực tế trong `models/rl_policy.npy`.
- **KHÔNG** tự tạo Q-table giả có thêm biến BMI.
- Ghi nhận báo cáo: RL tập trung tối ưu hóa phản ứng tức thời theo nồng độ đường huyết và nhịp sinh học bữa ăn trong ngày.

---

## 2. BẤT ĐỒNG BỘ ĐẦU VÀO GIỮA CÁC AGENT TRONG PHIÊN TƯ VẤN

### Hiện tượng:
- **Agent Dự đoán (Deep Learning - ONNX):** Đòi hỏi đầy đủ 13 trường thông tin: `age`, `gender`, `bmi`, `blood_glucose_level`, `hbA1c_level`, `hypertension`, `heart_disease`, `smoking_history`, và 5 cờ chủng tộc `race:*`.
- **Agent Đề xuất (RL):** Chỉ cần `blood_glucose_level` và `time_bin` (buổi trong ngày).
- **Agent An toàn (Safety):** Cần `blood_glucose_level`, hành động của RL, và văn bản câu hỏi của người dùng.
- **Agent Tri thức (KB/RAG):** Chỉ cần câu hỏi tự nhiên của người dùng.

### Đề xuất ánh xạ & Nguyên tắc bất biến:
1. **Trường dữ liệu chung:** `blood_glucose_level` được dùng chung cho cả Dự đoán, RL và An toàn.
2. **Khung thời gian (`time_bin`):** Người dùng có thể chọn hoặc hệ thống tự động gán theo giờ thực tế của phiên truy vấn:
   - 05:00 - 10:59 $\rightarrow$ Sáng (`time_bin = 0`)
   - 11:00 - 13:59 $\rightarrow$ Trưa (`time_bin = 1`)
   - 14:00 - 20:59 $\rightarrow$ Tối (`time_bin = 2`)
   - 21:00 - 04:59 $\rightarrow$ Đêm (`time_bin = 3`)
3. **Chủng tộc (Race):** Đối với người dùng Việt Nam, mặc định ánh xạ `race:Asian = 1`, các cờ `race:*` khác bằng 0.
4. **CHỖ TUYỆT ĐỐI KHÔNG BỊA SỐ LIỆU:**
   - Nếu người dùng chỉ nhập câu hỏi hoặc chỉ nhập đường huyết mà **thiếu các chỉ số dịch tễ** (`age`, `bmi`, `hbA1c_level`,...):
     - **KHÔNG ĐƯỢC TỰ ĐỘNG ĐIỀN TRUNG BÌNH (Mean/Default Imputation)** để ép chạy mô hình Deep Learning.
     - Agent Điều phối phải trả về phản hồi: Vẫn giải đáp tri thức (RAG), vẫn tư vấn lối sống (RL) và kiểm tra an toàn nếu có đường huyết, nhưng thông báo rõ: *"Chưa đủ chỉ số để dự đoán xác suất rủi ro tiểu đường (thiếu tuổi, BMI, HbA1c,...)"*.
     - Nếu người dùng gọi riêng endpoint `/api/predict` mà thiếu trường bắt buộc, API trả mã lỗi HTTP `422 Unprocessable Entity` chỉ rõ các trường thiếu.

---

## 3. LỆCH ĐƠN VỊ ĐO ĐƯỜNG HUYẾT (mg/dL vs mmol/L)

### Hiện tượng:
- Tài liệu y tế Việt Nam (Bộ Y tế) và thực tế xét nghiệm tại các bệnh viện Việt Nam chủ yếu dùng đơn vị **$\text{mmol/L}$** (ví dụ: mục tiêu đói $3.9 - 5.6\text{ mmol/L}$, cảnh báo cấp cứu $< 3.9$ hoặc $\ge 14.0\text{ mmol/L}$).
- Tập dữ liệu huấn luyện (`diabetes_dataset.csv`), bộ chuẩn hóa (`models/scaler.json`), bảng rời rạc hóa (`models/discretization.json`) và luật (`rules.yaml`) đều định chuẩn theo **$\text{mg/dL}$** (ngưỡng 70, 100, 140, 180, 250 mg/dL).

### Đề xuất ánh xạ:
- Cung cấp cơ chế chuyển đổi hai chiều chuẩn hóa:
  $$\text{Glucose (mg/dL)} = \text{Glucose (mmol/L)} \times 18.0182$$
  $$\text{Glucose (mmol/L)} = \frac{\text{Glucose (mg/dL)}}{18.0182}$$
- Giao diện người dùng cho phép chọn đơn vị nhập (`mmol/L` hoặc `mg/dL`). Backend quy về `mg/dL` trước khi đưa vào mô hình số học, và hiển thị song song cả hai đơn vị trong kết quả tư vấn để người bệnh dễ theo dõi.

---

## 4. TÀI NGUYÊN SẴN CÓ TRÊN Ổ ĐĨA VS YÊU CẦU RUNTIME

### Hiện tượng:
- Các tệp mô hình đã huấn luyện hoàn tất nằm trong `models/` và `notebooks/`.
- Thư mục `kb_index/`, `data/eval/`, và `reports/` chưa được tách ra độc lập trên thư mục gốc.

### Kế hoạch giải quyết:
- Ở Phase 1 (P1), ta thực hiện nạp và xác thực toàn bộ model:
  - Sao chép `rules.yaml` vào `models/` hoặc tạo symlink chuẩn.
  - Tái xuất Production Knowledge Base Index (`kb_production_index.pkl`, `kb_chunks_metadata.json`, `kb_config.json`) từ notebook N2 vào `models/kb_index/`.
  - Trích xuất 35 câu hỏi kiểm thử đã duyệt từ N2 Cell 19 vào `data/eval/rag_questions_approved.json`.
  - Khởi tạo thư mục `reports/metrics/` và `reports/figures/` để sẵn sàng cho các pha kiểm thử và đánh giá.
