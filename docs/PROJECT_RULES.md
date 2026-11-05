# QUY TẮC PHÁT TRIỂN DỰ ÁN (PROJECT RULES)
*Dự án: Hệ đa agent hỗ trợ tư vấn cho bệnh nhân tiểu đường*
*Môn học: Phát triển các hệ thống thông minh - PTIT*

---

## 1. NGUYÊN TẮC BẤT BIẾN (CORE RULES)

1. **Tuyệt đối không trả kết quả giả (No Mock Data / No Fake Results):**
   - Không bao giờ bịa đặt số liệu hoặc sinh dữ liệu giả khi thiếu mô hình hay tham số.
   - Nếu thiếu checkpoint mô hình hoặc thiếu dữ liệu đầu vào bắt buộc, API phải trả mã lỗi HTTP `503 Service Unavailable` kèm thông báo lỗi rõ ràng về thành phần bị thiếu.

2. **Dữ liệu thực nghiệm phải lấy từ chạy thật:**
   - Toàn bộ bảng số liệu, ma trận đánh giá và biểu đồ phục vụ báo cáo phải xuất trực tiếp từ quá trình chạy thực tế trên notebook hoặc script đánh giá.
   - Chỉ số dạng số lưu tại: `reports/metrics/*.json`.
   - Biểu đồ và đồ thị lưu tại: `reports/figures/*.png`.

3. **Bảo toàn nguyên bản tài liệu đặc tả `docs/report.md`:**
   - Không được tự ý chỉnh sửa nội dung trong `docs/report.md`.
   - Mọi điểm sai khác, xung đột hoặc chưa đồng nhất giữa báo cáo lý thuyết và thực tế triển khai phải được ghi chép minh bạch tại `docs/discrepancies.md` và thông báo ngay cho người phụ trách.

4. **Kỷ luật phát triển theo từng lượt (Phase Scope Discipline):**
   - Mỗi lượt làm việc chỉ tập trung thực hiện đúng phạm vi được giao.
   - Không tự ý viết lại (rewrite) các tệp mã nguồn hoặc module đã hoàn thiện và chạy ổn định.
   - Chạy kiểm thử tự động (Unit Test / Integration Test) thành công trước khi thông báo hoàn tất nhiệm vụ.
   - Mỗi lượt kết thúc bắt buộc phải tạo git commit có thông điệp mô tả cụ thể.

5. **Phong cách chú thích mã nguồn (Code Comments):**
   - Chú thích ngắn gọn, tự nhiên bằng tiếng Việt.
   - Tập trung giải thích logic nghiệp vụ y khoa hoặc giải thuật; không chú thích các điều hiển nhiên của cú pháp ngôn ngữ.

6. **Xử lý giới hạn ngữ cảnh (Context Boundary Handling):**
   - Khi tiến gần giới hạn dung lượng token/context, phải chủ động dừng lại ở ranh giới tệp hoàn chỉnh.
   - Ghi chú `TODO` cụ thể tại điểm dừng; tuyệt đối không bỏ dở mã nguồn giữa chừng hoặc tạo ra tệp bị đứt gãy cú pháp.

---

## 2. QUY ĐỊNH KIẾN TRÚC & CÔNG NGHỆ

1. **Mô hình kiến trúc đa tác tử (Multi-Agent Architecture):**
   - **Agent Điều phối (Coordinator):** Quản lý ngữ cảnh, định tuyến thông điệp tới 4 tác tử chuyên trách và tổng hợp phản hồi.
   - **Agent Dự đoán (Prediction):** Chạy mô hình phân loại Deep Learning MLP qua `onnxruntime`, đánh giá nguy cơ tiểu đường nhị phân.
   - **Agent Tri thức (Knowledge):** Kết hợp Cơ sở tri thức (KB) và Vector RAG trích xuất từ tài liệu Bộ Y tế & ADA.
   - **Agent Đề xuất (Recommendation):** Sử dụng Học tăng cường (RL, Q-table) chỉ để đề xuất lối sống (dinh dưỡng, vận động, đo đường huyết). Tuyệt đối **KHÔNG** kê đơn hoặc điều chỉnh liều thuốc/insulin.
   - **Agent An toàn (Safety):** Dựa trên hệ luật (Rule-based) giám sát lâm sàng, sở hữu **quyền phủ quyết (Veto Power)** tuyệt đối khi phát hiện nguy cơ hạ đường huyết, toan ceton, hoặc yêu cầu kê đơn bất hợp pháp.

2. **Thứ tự ưu tiên khi xung đột (Conflict Resolution Priority):**
   $$\text{Safety (An toàn)} > \text{Knowledge (Tri thức)} > \text{Recommendation (Đề xuất)} > \text{Prediction (Dự đoán)}$$

3. **Ngăn xếp công nghệ đã thống nhất (Tech Stack):**
   - **Backend:** Python 3.11, FastAPI, Pydantic, ONNX Runtime.
   - **Frontend:** Vite + React + Pure CSS (CSS thuần, không sử dụng Tailwind CSS, không dùng thư viện UI dựng sẵn như AntD, MUI hay Bootstrap).
   - **LLM Integration:** Tích hợp Google Gemini API qua biến môi trường `.env` (`GEMINI_API_KEY`). Nếu không có khóa API, hệ thống tự động kích hoạt **chế độ extractive (trích xuất nguyên văn)** từ KB kèm trích dẫn nguồn tài liệu chuẩn mực.
