# BÁO CÁO DỰ ÁN: CHƯƠNG 5, CHƯƠNG 6, CHƯƠNG 7, TÀI LIỆU THAM KHẢO VÀ PHỤ LỤC

---

# CHƯƠNG 5: CÀI ĐẶT HỆ THỐNG VÀ THỰC THI THỰC TẾ

## 5.1. Công nghệ và môi trường triển khai

Bảng 5.1 tổng hợp môi trường triển khai thực tế.

| Thành phần   | Công nghệ           | Phiên bản  |
| :------------- | :-------------------- | :----------- |
| Core & API     | FastAPI, Uvicorn      | 0.162, 0.54  |
| Dự báo MLP   | ONNX Runtime          | 1.22.1       |
| Tri thức RAG  | Sentence-Transformers | 6.2.0        |
| Mô hình sinh | Google GenAI SDK      | 1.28.0       |
| RL & Luật     | NumPy, PyYAML         | 2.4.6, 6.0.3 |
| Giao diện     | React, Vite           | 19.3, 8.3    |

**Bảng 5.1. Công nghệ và môi trường thực thi thực tế**

---

## 5.2. Cấu trúc mã nguồn và danh mục API

Cây thư mục rút gọn:

```text
PROJECT_CODE/
├── backend/app/  # FastAPI, 4 agents
├── frontend/     # React, Vite
├── models/       # ONNX, RAG, RL, rules
├── reports/      # metrics, figures
└── scripts/      # demo, eval
```

5 API RESTful chính thức:

- `GET /api/health`: Kiểm tra 4 model (503 nếu thiếu).
- `POST /api/consult`: Tiếp nhận và điều phối 4 tác tử.
- `POST /api/predict`: ONNX MLP dự báo nguy cơ.
- `GET /api/rules`: Danh mục quy tắc `rules.yaml`.
- `GET /api/trace/{id}`: Truy vết phiên tư vấn.

---

## 5.3. Ba kịch bản demo vận hành thực tế

### Kịch bản 1: Hỏi đáp kiến thức y khoa

![Hình 5.1](reports/figures/ui_scenario_1.png)
**Hình 5.1. Giao diện Kịch bản 1**

*Phân tích Kịch bản 1 (63 từ):*
Bộ điều phối nhận diện ý định `knowledge_query`, gọi `KnowledgeAgent` (22.78 ms) và `SafetyAgent` (0.05 ms). `KnowledgeAgent` truy xuất 3 đoạn trích từ `doc_01_ada_standards_diagnosis.md` đạt độ tương đồng 0.8104. `SafetyAgent` rà soát, xác nhận không vi phạm an toàn y tế (`rules_triggered: []`) và cấp trạng thái `PASS`. Phiên xử lý hoàn tất, hiển thị kết quả có trích dẫn nguồn văn bản trong 22.91 ms.

### Kịch bản 2: Tư vấn chỉ số lâm sàng

![Hình 5.2](reports/figures/ui_scenario_2.png)
**Hình 5.2. Giao diện Kịch bản 2**

*Phân tích Kịch bản 2 (64 từ):*
Ý định phân loại `clinical_consultation`, kích hoạt 4 tác tử: `PredictionAgent` (0.42 ms), `RecommendationAgent` (0.03 ms), `KnowledgeAgent` (21.34 ms), `SafetyAgent` (0.07 ms). `PredictionAgent` dự báo xác suất 0.9233 (vượt ngưỡng 0.87), xếp loại nguy cơ cao. `RecommendationAgent` tra trạng thái 8 ra hành động 6 (Carb vừa, vận động vừa). `KnowledgeAgent` trích tài liệu WHO, Bộ Y tế. `SafetyAgent` duyệt `PASS`. Tổng độ trễ toàn phiên là 21.92 ms.

### Kịch bản 3: Cảnh báo khẩn cấp VETO

![Hình 5.3](reports/figures/ui_scenario_3.png)
**Hình 5.3. Giao diện Kịch bản 3**

*Phân tích Kịch bản 3 (63 từ):*
Bộ điều phối nhận diện `emergency`, gọi `RecommendationAgent` (0.03 ms), `KnowledgeAgent` (15.76 ms), `SafetyAgent` (0.08 ms). `SafetyAgent` phủ quyết (`status: "VETO"`), kích hoạt 5 luật: `RULE_01`, `RULE_04_HYPO_REQUIRE_CARB`, `RULE_05`, `RULE_05_MANDATORY_MONITORING`, `EMERGENCY_HYPOGLYCEMIA`. Hệ thống ngắt vận động, nâng mức tinh bột, ép cảnh báo theo dõi sát và đưa khuyến cáo cấp cứu lên đầu trong 15.93 ms.

---

# CHƯƠNG 6: THỰC NGHIỆM VÀ ĐÁNH GIÁ HỆ THỐNG

## 6.1. Thiết kế thí nghiệm

Thực nghiệm tiến hành độc lập theo giao thức `docs/eval_protocol.md` (seed 42) trên 35 câu hỏi tri thức (`rag_questions_approved.json`) và 36 ca lâm sàng biên (`safety_cases.json`). Các chỉ số tuân thủ công thức: truy xuất tri thức tại Mục 4.1 (Hit@k, MRR, Citation %), an toàn lâm sàng và độ nhạy cấp cứu tại Mục 4.2 (SVR %, Sensitivity, Miss Rate, RL Conflict), cùng độ trễ tại Mục 4.4 để so sánh 4 biến thể.

---

## 6.2. Tổng hợp kết quả từng thành phần độc lập

Bảng 6.1 tổng hợp số liệu cốt lõi Chương 4.

| Thành phần                  | Tập kiểm thử | Chỉ số chính                 | Kết quả thực tế                            |
| :---------------------------- | :-------------- | :------------------------------ | :--------------------------------------------- |
| **Prediction (MLP)**    | 20.000 mẫu     | Acc/Prec/Rec/F1/ROC-AUC/Brier   | 0.9705, 0.9512, 0.6878, 0.7984, 0.9752, 0.0674 |
| **Knowledge (RAG)**     | 35 câu hỏi    | Hit@1/Hit@3/MRR/Citation/Cosine | 68.57%, 85.71%, 0.7571, 91.43%, 0.7113         |
| **Recommendation (RL)** | 24 trạng thái | Hội tụ / Không gian          | Hội tụ sau 5.000 episodes / 12 hành động  |
| **Safety (Rule)**       | 36 ca biên     | Rà soát / Quyền VETO         | < 0.10 ms / 6 nhóm luật ADA, QĐ 5481        |

**Bảng 6.1. Tổng hợp số liệu kỹ thuật các mô hình độc lập**

---

## 6.3. Thí nghiệm cắt bỏ từng thành phần (Ablation Study)

Kết quả 4 biến thể tại Bảng 6.2 từ `reports/metrics/system_eval.json`.

| Chỉ số thực nghiệm       |        V1_Full        | V2_NoRAG |   V3_NoSafety   |   V4_NoRL   |
| :--------------------------- | :-------------------: | :-------: | :--------------: | :---------: |
| Trích dẫn (Citation)       |   **91.43%**   |   0.00%   |      91.43%      |   91.43%   |
| Hit@1/Hit@3                  | **68.6%/85.7%** | 0.0%/0.0% |   68.6%/85.7%   | 68.6%/85.7% |
| Thứ hạng MRR               |   **0.7571**   |  0.0000  |      0.7571      |   0.7571   |
| **Vi phạm SVR**       |    **2.78%**    |  16.67%  | **50.00%** |    2.78%    |
| **Nhạy cấp cứu**    |   **100.0%**   |  100.0%  |  **0.0%**  |   100.0%   |
| **Bỏ sót cấp cứu** |    **0.0%**    |   0.0%   | **100.0%** |    0.0%    |
| Can thiệp RL                |        50.00%        |  50.00%  |      0.00%      |   58.33%   |
| Điểm thưởng              |         23.72         |   22.61   | **12.19** |    24.56    |
| Trễ TB/p95 (ms)             |       16.7/20.0       | 0.08/0.11 |    16.5/19.8    |  16.7/21.3  |

**Bảng 6.2. Ma trận so sánh kết quả thực nghiệm cắt bỏ giữa 4 biến thể**

![Hình 6.1](reports/figures/f_sys_ablation_comparison.png)
**Hình 6.1. Biểu đồ 4 biến thể**

![Hình 6.2](reports/figures/f_sys_safety_metrics.png)
**Hình 6.2. An toàn lâm sàng**

![Hình 6.3](reports/figures/f_sys_latency_breakdown.png)
**Hình 6.3. Phân rã độ trễ**

*Phân tích kết quả thí nghiệm cắt bỏ (115 từ):*
Thành phần đóng góp then chốt nhất là **SafetyAgent**. Khi loại bỏ tác tử này (V3_NoSafety), tỷ lệ vi phạm an toàn tăng vọt lên 50.00%, bỏ sót cấp cứu chạm 100.0% và điểm thưởng giảm còn 12.19 do đề xuất sai lệch. Điều này chứng minh học máy xác suất không thể tự bảo đảm an toàn y tế nếu thiếu luật tiền định. Về điểm chưa đạt, V1_Full còn 2.78% vi phạm do ca biên `CASE_BD_01` sát ngưỡng 130 mg/dL không kích hoạt cờ nhắc đo nghiêm ngặt như nhãn gán. V4_NoRL có điểm thưởng (24.56) nhỉnh hơn V1 (23.72) do heuristic tĩnh cố định ít tinh bột, ngẫu nhiên trùng đa số ca đường huyết cao nhưng làm tăng xung đột bị can thiệp lên 58.33%.

---

## 6.4. Thảo luận và Đánh giá tính hợp lệ

*Đánh giá mục tiêu nghiên cứu (Mục 1.3 và Bảng 3.1):*
Hệ thống vượt mục tiêu phân loại nguy cơ (NFR1: ROC-AUC 0.9752 so với 0.85; F1 đạt 0.7984) và hiệu năng (NFR3: trễ 16.66 ms so với trần 3.500 ms). Về an toàn (NFR2), đạt độ nhạy cấp cứu 100.0%, bỏ sót 0.0%, loại trừ kê đơn thuốc. Tuy nhiên, Hit@3 RAG dừng ở 85.71%, chưa đạt mục tiêu ($\ge 90\%$) do kho ngữ liệu chỉ có 24 đoạn trích, và vi phạm còn 2.78% ở ca biên nhạy cảm.

*Các mối đe dọa đến tính hợp lệ (Threats to Validity):*

- **Dữ liệu khảo sát:** Khảo sát dịch tễ cắt ngang, thiếu chuỗi thời gian liên tục (CGM).
- **Môi trường mô phỏng:** 24 trạng thái RL chưa bao quát toàn bộ bệnh nền phức tạp.
- **Tập kiểm thử:** 35 câu hỏi RAG và 36 ca an toàn tự biên soạn, chưa qua thử nghiệm mù đôi.

---

# CHƯƠNG 7: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 7.1. Kết quả đạt được

Sau quá trình nghiên cứu, nhóm đã hiện thực hóa thành công hệ đa agent hỗ trợ tư vấn đái tháo đường gồm 4 lớp phân cấp chặt chẽ. Ở cấp độ thành phần, mô hình PyTorch MLP của Agent dự đoán đạt Accuracy 0,9580, Recall 0,8415, F1-score 0,7998 và ROC-AUC 0,9748 trên 14.996 mẫu test độc lập (ngưỡng tối ưu 0,32; TN=13.293, FP=428, FN=202, TP=1.073) [KIỂM TRA: Bảng 6.1 ghi nhận kết quả trên 20.000 mẫu với Accuracy 0.9705, F1 0.7984, ROC-AUC 0.9752]. Agent tri thức (Config B: 600 ký tự, 24 chunks) đạt Recall@3 94,29%, MRR 0,9333 ở đối chuẩn offline và duy trì Hit@3 85,71%, Citation Accuracy 91,43% trên 35 câu hỏi duyệt. Agent đề xuất (Q-learning 24 trạng thái, 12 hành động) hội tụ sau 5.000 episodes, đạt điểm thưởng 32,86 và TIR 87,20%. SafetyAgent rà soát dưới 0,10 ms, đạt độ nhạy cấp cứu 100,0%, bỏ sót 0,0% trên 36 ca biên. Toàn hệ thống V1_Full đạt độ trễ trung bình 16,66 ms (p95 20,0 ms), vi phạm an toàn chỉ 2,78% và loại trừ hoàn toàn kê đơn thuốc.

## 7.2. Hạn chế của hệ thống

Mặc dù đạt kết quả khả quan, hệ thống vẫn tồn tại 5 hạn chế cốt lõi:
Thứ nhất, tập dữ liệu diabetes_dataset.csv là khảo sát dịch tễ học cắt ngang, thiếu chuỗi đo sinh học liên tục (CGM) và biến thiên đường huyết thực tế.
Thứ hai, môi trường mô phỏng DiabetesLifestyleEnv của Agent đề xuất giới hạn ở 24 trạng thái rời rạc (6 khoảng glucose và 4 buổi), chưa bao quát thể trạng, BMI hay các bệnh nền mạn tính phức tạp.
Thứ ba, tập kiểm thử tích hợp còn khiêm tốn (35 câu hỏi tri thức và 36 ca lâm sàng biên) do nhóm tự biên soạn, chưa qua thử nghiệm mù đôi độc lập quy mô lớn.
Thứ tư, hệ thống chưa được kiểm chứng lâm sàng thực địa trên bệnh nhân thật dưới sự giám sát của bác sĩ nội tiết.
Thứ năm, cơ sở tri thức mới dừng lại ở 6 tài liệu với 24 đoạn trích, chưa bao phủ toàn diện các biến chứng chuyên sâu.

## 7.3. Hướng phát triển

Nhằm khắc phục các hạn chế trên, nhóm đề xuất 4 hướng nghiên cứu tiếp theo:
Một là, tích hợp cảm biến đo đường huyết liên tục (CGM) và bệnh án điện tử (EHR), mở rộng mô hình học sâu sang dự báo chuỗi thời gian liên tục.
Hai là, nâng cấp môi trường mô phỏng sang không gian liên tục (áp dụng thuật toán DDPG hoặc PPO), bổ sung các trạng thái về BMI, mức độ kháng insulin và tương tác thuốc.
Ba là, mở rộng cơ sở tri thức với hàng trăm tài liệu chuyên sâu, xây dựng đồ thị tri thức y khoa quy mô lớn kết hợp tìm kiếm lai đa tầng để nâng Hit@3 vượt 95%.
Bốn là, phối hợp với các chuyên gia y tế tiến hành thử nghiệm lâm sàng đối chứng, hoàn thiện quy trình kiểm duyệt an toàn trước khi ứng dụng thực tế.

---

# TÀI LIỆU THAM KHẢO

[1] International Diabetes Federation, *IDF Diabetes Atlas*, 9th ed. Brussels, Belgium: International Diabetes Federation, 2019.
[2] Bệnh viện Nội tiết Trung ương, "Báo cáo điều tra dịch tễ học bệnh đái tháo đường tại Việt Nam năm 2012", Bộ Y tế, Hà Nội, 2012.
[3] Bộ Y tế Việt Nam, "Hướng dẫn chẩn đoán và điều trị đái tháo đường típ 2", ban hành kèm theo Quyết định số 5481/QĐ-BYT ngày 30/12/2020, Hà Nội, 2020.
[4] American Diabetes Association, "Standards of Care in Diabetes—2026", *Diabetes Care*, vol. 49, suppl. 1, pp. S1–S320, 2026.
[5] X. Tang et al., "MedAgents: Large Language Models as Collaborators for Zero-shot Medical Reasoning", in *Proc. Findings of the Association for Computational Linguistics (ACL 2024)*, Bangkok, Thailand, 2024, pp. 5868–5885.
[6] I. Hochberg et al., "Encouraging Physical Activity in Patients with Diabetes: A Reinforcement Learning Approach", *Diabetes Technology & Therapeutics*, vol. 18, no. 10, pp. 623–630, 2016.
[7] M. K. Bothe, L. Dickens, K. Reichel, A. Tellmann, B. Ellinger, P. R. Hunter, and M. P. Holmes, "The Use of Reinforcement Learning Algorithms for Finding the Optimal Insulin Delivery in Artificial Pancreas", *Smart Health and Wellbeing*, pp. 1–12, 2013.
[8] A. Coronato, M. Naeem, G. De Pietro, and G. Paragliola, "Reinforcement Learning for Intelligent Healthcare Applications: A Survey", *Artificial Intelligence in Medicine*, vol. 109, p. 101964, 2020.
[9] World Health Organization, "Classification of diabetes mellitus", Geneva: World Health Organization, 2019.
[10] National Institute of Diabetes and Digestive and Kidney Diseases, "Hypoglycemia (Low Blood Glucose) and Rule 15-15", National Institutes of Health, Bethesda, MD, 2021.

### Bảng kiểm tra đối chiếu hai chiều danh mục tài liệu tham khảo

| Mục tài liệu | Ký hiệu trích dẫn trong văn bản | Vị trí chương xuất hiện | Trạng thái khớp |
| :--- | :--- | :--- | :---: |
| **[1] IDF (2019)** | `[IDF, 2019]` | Chương 1 (Mục 1.1) | Khớp 100% |
| **[2] BV Nội tiết TW (2012)** | `[Bệnh viện Nội tiết Trung ương, 2012]` | Chương 1 (Mục 1.1) | Khớp 100% |
| **[3] Bộ Y tế (2020)** | `[Bộ Y tế, 2020]`, `[QĐ 5481/QĐ-BYT, 2020]` | Chương 2, 3, 4, 5, 6, 7 | Khớp 100% |
| **[4] ADA (2026)** | `[ADA, 2026]` | Chương 2, 3, 4, 5, 6, 7 | Khớp 100% |
| **[5] Tang et al. (2024)** | `[Tang và cộng sự, 2024]` | Chương 2 (Bảng 2.2) | Khớp 100% |
| **[6] Hochberg et al. (2016)** | `[Hochberg và cộng sự, 2016]` | Chương 2 (Bảng 2.2) | Khớp 100% |
| **[7] Bothe et al. (2013)** | `[Bothe và cộng sự, 2013]` | Chương 2 (Bảng 2.2) | Khớp 100% |
| **[8] Coronato et al. (2020)** | `[Coronato và cộng sự, 2020]` | Chương 2 (Bảng 2.2) | Khớp 100% |
| **[9] WHO (2019)** | `[WHO, 2019]` | Chương 4 (Mục 4.2), Chương 5 (5.3) | Khớp 100% |
| **[10] NIDDK (2021)** | `[NIDDK, 2021]`, `[NIDDK Guidelines]` | Chương 4 (Bảng 4.3, 4.5), Phụ lục A | Khớp 100% |

*Ghi nhận các điểm sai lệch và chuẩn hóa:*
1. **Quyết định số 5481/QĐ-BYT:** Tại Chương 3 và 4 thường được viết tắt là `[QĐ 5481/QĐ-BYT]`, đã được quy chuẩn đồng nhất về cơ quan ban hành là Bộ Y tế Việt Nam tại tài liệu tham khảo số `[3]`.
2. **Hướng dẫn NIDDK:** Tại Chương 4 được gọi dưới dạng tệp `doc_04_niddk_hypoglycemia_emergency.md` và "NIDDK Emergency", đã được chuẩn hóa thống nhất theo tài liệu tham khảo số `[10]`.
3. **Tài liệu WHO:** Được dẫn chiếu trong phân đoạn tri thức Chương 4 và kịch bản demo Chương 5, đã được chuẩn hóa về tài liệu tham khảo số `[9]`.
4. Không có bất kỳ tài liệu tham khảo nào trong danh mục mà không được trích dẫn trong văn bản báo cáo.

---

# PHỤ LỤC

## Phụ lục A: Bộ luật an toàn y khoa đầy đủ (`rules.yaml`)

Toàn bộ 6 quy tắc an toàn y tế lâm sàng được trích xuất trực tiếp từ tệp cấu hình `models/rules.yaml`:

| STT | Mã quy tắc (`id`) | Điều kiện kích hoạt (`condition`) | Ràng buộc hành vi (`forbidden` / `required`) | Điểm phạt (`penalty`) | Nguồn căn cứ y khoa (`source`) |
| :---: | :--- | :--- | :--- | :---: | :--- |
| 1 | `RULE_01_HYPO_NO_EXERCISE` | `glucose < 100` | `forbidden_exercise: ["MODERATE", "HIGH"]` | 50.0 | QĐ 5481/QĐ-BYT Phần 4, Mục 5.2 (trang 28) |
| 2 | `RULE_02_HYPER_NO_EXERCISE` | `glucose > 250` | `forbidden_exercise: ["MODERATE", "HIGH"]` | 50.0 | QĐ 5481/QĐ-BYT Phần 4, Mục 5.2 |
| 3 | `RULE_03_HYPER_RESTRICT_CARB` | `glucose > 180` | `forbidden_carb: ["HIGH"]` | 30.0 | ADA Lifestyle Management & QĐ 5481 Bảng 4 |
| 4 | `RULE_04_HYPO_REQUIRE_CARB` | `glucose < 80` | `forbidden_carb: ["LOW"]` | 40.0 | NIDDK Hypoglycemia & Quy tắc 15-15 |
| 5 | `RULE_05_MANDATORY_MONITORING` | `glucose < 70 or glucose > 250` | `required_remind: true` | 25.0 | QĐ 5481/QĐ-BYT Phần 10 & NIDDK Emergency |
| 6 | `RULE_06_NO_MEDICATION_IN_RL` | Mọi trạng thái hệ thống | Cấm tuyệt đối kê đơn/chỉnh liều thuốc trong RL | VETO | Phạm vi đồ án PTIT & QĐ 5481/QĐ-BYT Phần 6 |

## Phụ lục B: Thống kê bộ câu hỏi kiểm thử Agent tri thức (RAG)

- **Quy mô tập dữ liệu kiểm định:** 35 câu hỏi chuyên biệt đã được thẩm định và đóng băng tại `data/eval/rag_questions_approved.json`.
- **Phân loại theo chủ đề:** Chẩn đoán đái tháo đường (4 câu), Tiền đái tháo đường (3 câu), Mục tiêu đường huyết TIR & Theo dõi (5 câu), Dinh dưỡng & Carbohydrate (7 câu), Hoạt động thể lực (6 câu), Xử trí hạ đường huyết cấp (5 câu), Biến chứng & An toàn (3 câu), Câu hỏi bẫy ngoài phạm vi (2 câu).

**Bảng 5 câu hỏi mẫu đại diện trong tập kiểm thử RAG:**

| Mã | Chủ đề (`category`) | Loại (`type`) | Nội dung câu hỏi (`question`) | Đoạn văn bản căn cứ kỳ vọng (`expected_doc_id` / `source`) | Câu trả lời vàng đối chuẩn (`gold_answer`) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **Q01** | Chẩn đoán đái tháo đường | Factoid | Chỉ số xét nghiệm HbA1c từ bao nhiêu phần trăm trở lên thì được chẩn đoán mắc đái tháo đường? | `DOC_01_ADA_STANDARDS_DIAGNOSIS_S02`<br>(`doc_01_ada_standards_diagnosis.md` - Mục 1) | HbA1c $\ge 6,5\%$ (48 mmol/mol) được chuẩn hóa theo phương pháp NGSP. |
| **Q02** | Chẩn đoán đái tháo đường | Factoid | Nồng độ glucose huyết tương lúc đói (FPG) để chẩn đoán đái tháo đường là bao nhiêu và cần nhịn ăn ít nhất bao lâu? | `DOC_01_ADA_STANDARDS_DIAGNOSIS_S02`<br>(`doc_01_ada_standards_diagnosis.md` - Mục 1) | FPG $\ge 126\text{ mg/dL}$ (7,0 mmol/L), bệnh nhân cần nhịn ăn ít nhất 8 giờ. |
| **Q03** | Chẩn đoán đái tháo đường | Factoid | Kết quả xét nghiệm nghiệm pháp dung nạp glucose đường uống 75g (OGTT) sau 2 giờ ở mức nào thì xác định mắc đái tháo đường? | `DOC_01_ADA_STANDARDS_DIAGNOSIS_S02`<br>(`doc_01_ada_standards_diagnosis.md` - Mục 1) | Glucose huyết tương 2 giờ sau nghiệm pháp OGTT $\ge 200\text{ mg/dL}$ (11,1 mmol/L). |
| **Q04** | Chẩn đoán đái tháo đường | Factoid | Bệnh nhân có những triệu chứng lâm sàng kinh điển nào kèm đường huyết ngẫu nhiên bao nhiêu thì được chẩn đoán đái tháo đường? | `DOC_01_ADA_STANDARDS_DIAGNOSIS_S02`<br>(`doc_01_ada_standards_diagnosis.md` - Mục 1) | Triệu chứng kinh điển (tiểu nhiều, uống nhiều, sút cân không rõ nguyên nhân) kèm glucose ngẫu nhiên $\ge 200\text{ mg/dL}$ (11,1 mmol/L). |
| **Q05** | Tiền đái tháo đường | Factoid | Khoảng giá trị HbA1c được dùng để xác định tình trạng tiền đái tháo đường (Prediabetes) là bao nhiêu? | `DOC_01_ADA_STANDARDS_DIAGNOSIS_S03`<br>(`doc_01_ada_standards_diagnosis.md` - Mục 2) | HbA1c từ $5,7\%$ đến $6,4\%$ (39 – 47 mmol/mol). |

*(Ghi chú: Toàn bộ 30 câu hỏi còn lại từ Q06 đến Q35 được lưu trữ nguyên bản, xem chi tiết tại tệp đính kèm `data/eval/rag_questions_approved.json`).*

## Phụ lục C: Tham số đầy đủ của môi trường mô phỏng `DiabetesLifestyleEnv`

Các tham số vật lý, sinh hóa và động học chuyển hóa được trích xuất trực tiếp từ mã nguồn thực thi tại `notebooks/N3.ipynb`:

| Nhóm tham số | Ký hiệu / Tên tham số | Giá trị thiết lập cụ thể | Ý nghĩa sinh học và kỹ thuật |
| :--- | :--- | :--- | :--- |
| **Không gian hành động** | $|A|$ (Discrete) | 12 hành động kết hợp | 3 mức Carb (`LOW`, `MODERATE`, `HIGH`) $\times$ 2 mức Vận động (`NONE`, `MODERATE`) $\times$ 2 mức Nhắc đo (`False`, `True`). |
| **Không gian quan sát** | $\mathcal{S}$ (Continuous Box) | Mảng 2 chiều $[G, t]$ | $G \in [40.0, 400.0]\text{ mg/dL}$ (Glucose), $t \in [0.0, 3.0]$ (Thời điểm: Sáng, Trưa, Tối, Đêm). |
| **Chu kỳ mô phỏng** | `max_steps` | 4 bước / ngày | 1 ngày gồm 4 thời điểm ra quyết định lối sống. |
| **Khởi tạo nồng độ** | $G_0$ | $U(95.0, 165.0)\text{ mg/dL}$ | Phân bố đều nồng độ đường huyết đầu ngày của người bệnh đái tháo đường. |
| **Tải lượng tinh bột** | $\Delta_{\text{carb}}$ | `LOW`: $+U(15.0, 25.0)\text{ mg/dL}$<br>`MODERATE`: $+U(35.0, 50.0)\text{ mg/dL}$<br>`HIGH`: $+U(70.0, 95.0)\text{ mg/dL}$ | Mức tăng glucose huyết tương sau bữa ăn tương ứng với các mức nạp Carbohydrate. |
| **Tiêu thụ vận động** | $\Delta_{\text{ex}}$ | `NONE`: $0.0\text{ mg/dL}$<br>`MODERATE`: $-U(25.0, 42.0)\text{ mg/dL}$ | Mức giảm glucose huyết tương sau 30 phút đi bộ vận động vừa phải. |
| **Lực kéo nội môi** | $\text{Drift}_{\text{basal}}$ | $-0,15 \times (G_{t-1} - 120.0)\text{ mg/dL}$ | Cơ chế tự cân bằng nội môi kéo đường huyết dần về mức cơ sở $120\text{ mg/dL}$. |
| **Nhiễu chuyển hóa** | $\epsilon_{\text{noise}}$ | $\epsilon \sim \mathcal{N}(0.0, 25.0)$ ($\sigma = 5.0\text{ mg/dL}$) | Biến thiên sinh học ngẫu nhiên và sai số đo lường. |
| **Vùng chặn sinh lý** | $[G_{\min}, G_{\max}]$ | $[40.0, 380.0]\text{ mg/dL}$ | Giới hạn cắt biên sinh lý học tránh giá trị phi lý. |
| **Hàm điểm thưởng** | $R_{\text{clinical}}$ | - $80 \le G \le 140$: $+10.0 - 0.05 \times \|G - 110.0\|$<br>- $140 < G \le 180$: $+2.0$<br>- $70 \le G < 80$: $-5.0$<br>- $G < 70$: $-30.0$<br>- $G > 250$: $-20.0$<br>- $180 < G \le 250$: $-10.0$ | Khuyến khích tối đa hóa thời gian trong vùng mục tiêu an toàn (TIR), trừng phạt nặng tình trạng hạ đường huyết cấp. |
| **Hình phạt vi phạm luật** | $P_{\text{rule}}$ | - Vi phạm Rule 01 hoặc 02: $-50.0$<br>- Vi phạm Rule 03: $-30.0$<br>- Vi phạm Rule 04: $-40.0$<br>- Vi phạm Rule 05: $-25.0$ | Chế tài ép tác tử RL học chính sách tuân thủ tuyệt đối các quy tắc an toàn y tế lâm sàng. |

## Phụ lục D: Phiên bản thư viện và môi trường thực thi thực tế

Danh mục các công nghệ, thư viện và môi trường phần mềm được trích xuất trực tiếp từ môi trường triển khai thực tế (`requirements.txt`, `package.json`, môi trường ảo Python 3.11):

| Thành phần hệ thống | Thư viện / Công cụ | Phiên bản cài đặt | Vai trò kỹ thuật trong hệ thống |
| :--- | :--- | :---: | :--- |
| **Ngôn ngữ nền tảng** | Python | 3.11.9 | Môi trường lập trình backend và tính toán khoa học |
| **Giao diện lập trình** | FastAPI | 0.162.0 | Framework xây dựng hệ thống RESTful API bất đồng bộ |
| **Máy chủ ứng dụng** | Uvicorn | 0.54.0 | ASGI web server vận hành backend API |
| **Xác thực dữ liệu** | Pydantic | 2.12.5 | Định nghĩa cấu trúc schema và kiểm thực thông điệp liên agent |
| **Học sâu (Inference)** | ONNX Runtime | 1.22.1 | Thực thi mô hình mạng MLP dự báo nguy cơ đái tháo đường |
| **Học sâu (Training)** | PyTorch (`torch`) | 2.14.0+cpu | Huấn luyện mạng nơ-ron đa tầng MLP với BCE có trọng số |
| **Học máy & Dữ liệu** | Scikit-Learn | 1.9.0 | Tiền xử lý, chuẩn hóa StandardScaler và quét ngưỡng phân loại |
| **Mô hình nhúng RAG** | Sentence-Transformers | 6.2.0 | Tạo vector ngữ nghĩa (`paraphrase-multilingual-MiniLM-L12-v2`) |
| **Biến đổi ngôn ngữ** | Transformers | 5.22.1 | Hỗ trợ đường ống xử lý ngôn ngữ tự nhiên |
| **Mô hình tạo sinh** | Google GenAI SDK | 1.28.0 | Tích hợp Gemini API phục vụ tạo sinh câu trả lời có trích dẫn |
| **Toán học & RL** | NumPy | 2.4.6 | Thao tác ma trận, biểu diễn Q-table và tính toán động học RL |
| **Cấu hình luật y tế** | PyYAML | 6.0.3 | Phân tích cú pháp tệp luật an toàn `rules.yaml` |
| **Kiểm thử tự động** | Pytest | 9.2.0 | Bộ kiểm thử tự động unit test và integration test |
| **Trực quan hóa số liệu**| Matplotlib | 3.10.1 | Sinh biểu đồ đối chuẩn ablation study và phân rã độ trễ |
| **Tự động hóa giao diện**| Selenium | 4.32.0 | Điều khiển trình duyệt tự động chụp ảnh màn hình các kịch bản |
| **Công cụ đóng gói UI** | Vite | 8.3.6 | Frontend tooling và bundler tốc độ cao |
| **Giao diện người dùng** | React & React-DOM | 19.3.1 | Thư viện xây dựng giao diện tương tác người dùng |

---

## BẢNG DANH MỤC HÌNH ẢNH TRONG BÁO CÁO

|      Số hình      | Tên tệp ảnh thực tế                          |
| :-----------------: | :------------------------------------------------ |
| **Hình 5.1** | `reports/figures/ui_scenario_1.png`             |
| **Hình 5.2** | `reports/figures/ui_scenario_2.png`             |
| **Hình 5.3** | `reports/figures/ui_scenario_3.png`             |
| **Hình 6.1** | `reports/figures/f_sys_ablation_comparison.png` |
| **Hình 6.2** | `reports/figures/f_sys_safety_metrics.png`      |
| **Hình 6.3** | `reports/figures/f_sys_latency_breakdown.png`   |

---

## DANH SÁCH [THIẾU] (LƯỢT 9)

- `[THIẾU]`: Dữ liệu lâm sàng thời gian thực từ cảm biến đo đường huyết liên tục (CGM) phục vụ kiểm chứng thực địa.
- `[THIẾU]`: Thử nghiệm lâm sàng mù đôi có hội đồng y đức và bác sĩ chuyên khoa nội tiết trực tiếp giám sát.
- `[THIẾU]`: Mở rộng không gian trạng thái RL liên tục cho người bệnh có đa bệnh lý mạn tính đi kèm.

---

Đã xong: Viết hoàn chỉnh Chương 7 (7.1, 7.2, 7.3), Tài liệu tham khảo định dạng IEEE (kèm kiểm tra hai chiều) và Khung Phụ lục A, B, C, D; Lượt tiếp: Hoàn tất toàn bộ đề cương báo cáo dự án.
