HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG
BỘ MÔN PHÁT TRIỂN CÁC HỆ THỐNG THÔNG MINH
PROJECT
Giảng Viên Hướng Dẫn: PGS. TS. Trần Đình Quế

| Họ và tên: | Lê Bùi Quốc Huy || --- | --- || Mã Sinh Viên: | B23DCCN387 || Lớp: | D23CNPM04 |
Hà Nội – 2026

# CHƯƠNG 1: GIỚI THIỆU

## Bối cảnh và tính cấp thiết
Đái tháo đường là bệnh lý rối loạn chuyển hóa mạn tính đặc trưng bởi tình trạng tăng glucose huyết do khiếm khuyết về tiết insulin, tác động của insulin hoặc cả hai. Theo báo cáo của Liên đoàn Đái tháo đường Quốc tế (IDF) năm 2019, toàn cầu có 463 triệu người trưởng thành mắc bệnh, đe dọa nghiêm trọng đến sức khỏe cộng đồng qua các biến chứng tim mạch, thận và mắt. Tại Việt Nam, nghiên cứu năm 2012 của Bệnh viện Nội tiết Trung ương ghi nhận tỷ lệ đái tháo đường chưa được chẩn đoán trong cộng đồng lên tới 63,6%, phản ánh sự thiếu hụt lớn trong công tác sàng lọc sớm. Dù có đến 70% ca bệnh đái tháo đường típ 2 có thể phòng ngừa hoặc làm chậm tiến triển bằng chế độ dinh dưỡng và vận động thể lực hợp lý, đa số bệnh nhân vẫn gặp khó khăn trong việc tiếp cận các hướng dẫn y khoa đáng tin cậy.
Thực tế lâm sàng đòi hỏi người bệnh phải được theo dõi chỉ số đường huyết liên tục và nhận tư vấn lối sống kịp thời nhằm duy trì mức glucose huyết mục tiêu từ 80 – 130 mg/dL lúc đói. Tuy nhiên, các mô hình học máy (Machine Learning) truyền thống chỉ dừng lại ở phép dự đoán xác suất tĩnh  từ dữ liệu bảng mà không thể tương tác giải thích hay đối thoại ngữ cảnh. Ngược lại, các mô hình ngôn ngữ lớn hoạt động độc lập lại tiềm ẩn nguy cơ ảo giác tri thức y khoa và thiếu cơ chế bảo đảm an toàn xác định. Do đó, việc xây dựng một hệ đa agent tích hợp học sâu, đồ thị tri thức, học tăng cường và hệ luật an toàn là giải pháp cấp thiết để hỗ trợ tư vấn cá nhân hóa cho người bệnh

## Phát biểu bài toán
Hệ thống tiếp nhận thông số sinh hóa cùng câu hỏi tự nhiên của người dùng để trả về dự đoán nguy cơ, câu trả lời y khoa có trích dẫn, khuyến nghị lối sống và cảnh báo an toàn. Không gian đầu vào tại mỗi phiên tương tác được hình thức hóa thành bộ dữ liệu X:
Trong đó,  là vector chỉ số sức khỏe dạng bảng gồm tuổi, chỉ số khối cơ thể (BMI), nồng độ glucose máu, HbA1c, tiền sử tăng huyết áp, bệnh tim mạch và thói quen hút thuốc;  là câu hỏi dạng văn bản thể hiện thắc mắc của người bệnh.
Không gian đầu ra hợp nhất Y được biểu diễn toán học như sau:
Trong đó:
kèm xác suất  do Agent dự đoán (Deep Learning) tính toán để sàng lọc rủi ro
là câu trả lời tri thức y khoa do Agent tri thức (KB + RAG) sinh ra, gắn kèm nguồn bằng chứng từ hướng dẫn chuẩn mực của ADA và Bộ Y tế
là quyết định can thiệp dinh dưỡng và thể lực được tối ưu bởi Agent đề xuất qua thuật toán Học tăng cường (Reinforcement Learning) tương tác với môi trường mô phỏng
là các cảnh báo cấp cứu (đường huyết hạ < 3,9 mmol/L hoặc quá cao) cùng quyết định kiểm duyệt từ Agent an toàn (Rule-based)
Agent điều phối quản lý luồng thông điệp theo thứ tự ưu tiên giải quyết xung đột bất biến:

## Mục tiêu và phạm vi
Mục tiêu của đề tài là xây dựng hệ đa agent thông minh hỗ trợ sàng lọc rủi ro, cung cấp tri thức y khoa có bằng chứng trích dẫn và hướng dẫn điều chỉnh lối sống an toàn cho bệnh nhân đái tháo đường. Ranh giới nghiên cứu được xác lập minh bạch tại Bảng 1.1

| Hạng mục xem xét | Trong phạm vi (In-Scope) | Ngoài phạm vi (Out-of-Scope) || --- | --- | --- || Vai trò y tế | Sàng lọc nguy cơ ban đầu và cung cấp thông tin y khoa tham khảo có dẫn nguồn. | Chẩn đoán bệnh chính thức hoặc thay thế kết luận của bác sĩ chuyên khoa. || Can thiệp điều trị | Đề xuất thói quen dinh dưỡng giảm đường đơn và tập thể dục tối thiểu 150 phút/tuần. | Kê đơn thuốc mới, đề xuất hoặc điều chỉnh liều thuốc hạ áp, Metformin và Insulin. || Dữ liệu nghiên cứu | Khai thác tập dữ liệu bảng ẩn danh phục vụ học thuật (diabetes_dataset.csv). | Sử dụng hồ sơ bệnh án điện tử thật hoặc thông tin định danh cá nhân nhạy cảm. || Xử lý tình huống | Nhận diện dấu hiệu hạ đường huyết (< 3,9 mmol/) để kích hoạt cảnh báo khẩn. | Trực tiếp can thiệp hoặc chỉ định phác đồ cấp cứu nội trú toan ceton và tăng áp lực thẩm thấu. |

**Bảng 1.1. Bảng phân định trong phạm vi và ngoài phạm vi của hệ thống**

*Phân tích Bảng 1.1*

**Bảng thể hiện ranh giới bảo đảm an toàn lâm sàng của hệ thống. Quan sát chính cho thấy hệ thống loại trừ hoàn toàn việc kê đơn thuốc, chỉnh liều insulin và chẩn đoán điều trị thực tế. Ý nghĩa là xác lập quyền phủ quyết tuyệt đối cho Agent an toàn khi phát hiện vi phạm. Hạn chế là hệ thống chỉ đóng vai trò tham vấn trên dữ liệu mô phỏng.**

## Đóng góp và bố cục báo cáo
Trong khuôn khổ đề tài môn học, nhóm thực hiện ba đóng góp kỹ thuật chính:
Nhóm đề xuất kiến trúc hệ đa agent bốn lớp với cơ chế điều phối phân cấp và giao thức giải quyết xung đột ưu tiên tuyệt đối cho an toàn y khoa.
Nhóm hiện thực hóa mô hình Deep Learning phân loại rủi ro trên dữ liệu bảng kết hợp đường ống lai giữa Đồ thị tri thức và Vector RAG có trích dẫn tường minh.
Nhóm xây dựng giải thuật Học tăng cường định hướng lối sống trong môi trường mô phỏng tích hợp bộ lọc luật y khoa ngăn chặn triệt để hành vi kê đơn tự động.
Báo cáo được bố cục thành 7 chương: Chương 1 giới thiệu tổng quan; Chương 2 trình bày cơ sở lý thuyết; Chương 3 phân tích yêu cầu và thiết kế kiến trúc hệ thống; Chương 4 đặc tả chi tiết các agent chuyên trách; Chương 5 trình bày cài đặt mã nguồn và demo; Chương 6 thực nghiệm và đánh giá chất lượng; Chương 7 kết luận và hướng phát triển tương lai.

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

## Đóng góp và bố cục báo cáo
Đái tháo đường là nhóm bệnh lý rối loạn chuyển hóa mạn tính đặc trưng bởi tình trạng tăng đường huyết do suy giảm bài tiết insulin, giảm tác động sinh học của hormone này hoặc phối hợp cả hai. Tình trạng tăng đường huyết kéo dài gây tổn thương vi mạch ở võng mạc, cầu thận, hệ thần kinh và làm gia tăng nguy cơ biến cố tim mạch xơ vữa. Trong dự án, các khái niệm bệnh học này là cơ sở để định nghĩa không gian nhãn cho Agent dự đoán, thiết lập các đỉnh thực thể trong đồ thị tri thức của Agent tri thức, đồng thời xác lập các điều kiện kích hoạt luật bảo vệ trong Agent an toàn.
Hệ thống tập trung vào 5 chỉ số lâm sàng cốt lõi được thu thập trong khám sàng lọc ngoại trú theo tài liệu của Bộ Y tế và Hiệp hội Đái tháo đường Hoa Kỳ: đường huyết đói, đường huyết sau nghiệm pháp hoặc bất kỳ, chỉ số HbA1c, chỉ số khối cơ thể (BMI) và huyết áp.

| Tên chỉ số lâm sàng | Đơn vị đo chuẩn | Ngưỡng tham chiếu (Bình thường / Tiền ĐTĐ / ĐTĐ) | Nguồn tài liệu y khoa chuẩn | Ý nghĩa lâm sàng trong hệ thống | Tên chỉ số lâm sàng || --- | --- | --- | --- | --- | --- || Glucose huyết đói (FPG) | mg/dL (mmol/L) | Bình thường: < 100 (< 5,6)Tiền ĐTĐ: 100 – 125 (5,6 – 6,9)ĐTĐ: ≥ 126 (≥ 7,0) | Bộ Y tế (2020), ADA (2026) | Phản ánh nồng độ đường huyết sau nhịn ăn ít nhất 8 giờ; dùng làm đầu vào cho Agent dự đoán và điều kiện kiểm tra của Agent an toàn. | Glucose huyết đói (FPG) || Glucose sau nghiệm pháp (2-h PG) / Bất kỳ (RPG) | mg/dL (mmol/L) | Bình thường: < 140 (< 7,8)Tiền ĐTĐ: 140 – 199 (7,8 – 11,0)ĐTĐ: ≥ 200 (≥ 11,1) | Bộ Y tế (2020), ADA (2026) | Đánh giá dung nạp glucose sau ăn; kích hoạt cảnh báo khẩn cấp nếu RPG ≥ 200 kèm triệu chứng tăng đường huyết cấp. | Glucose sau nghiệm pháp (2-h PG) / Bất kỳ (RPG) || Hemoglobin Glycated (HbA1c) | % (mmol/mol) | Bình thường: < 5,7 (< 39)Tiền ĐTĐ: 5,7 – 6,4 (39 – 47)ĐTĐ: ≥ 6,5 (≥ 48) | Bộ Y tế (2020), ADA (2026) | Đo lường mức đường huyết trung bình trong 2–3 tháng; làm chỉ báo phân tầng rủi ro mạn tính trong Agent dự đoán. | Hemoglobin Glycated (HbA1c) || Chỉ số khối cơ thể (BMI) | kg/m² | Bình thường: 18,5 – 22,9Thừa cân: 23,0 – 24,9Béo phì: ≥ 25,0 (chuẩn châu Á) | Bộ Y tế (2020), ADA (2026) | Đánh giá tình trạng đề kháng insulin mô mỡ; dùng làm trạng thái đầu vào cho Agent đề xuất lối sống. | Chỉ số khối cơ thể (BMI) |

**Bảng 2.1. Các chỉ số lâm sàng cốt lõi sử dụng trong hệ thống tư vấn đái tháo đường**

*Phân tích Bảng 2.1*

**Bảng 2.1 tổng hợp các thang đo sinh hóa định lượng và ngưỡng tham chiếu theo hướng dẫn của Bộ Y tế và ADA. Quan sát chính cho thấy ranh giới rõ rệt giữa ba trạng thái chuyển hóa qua các ngưỡng sinh hóa xác định. Ý nghĩa đối với thiết kế là cung cấp dữ liệu số hóa chuẩn cho Agent dự đoán và xác lập luật ngưỡng tiền định cho Agent an toàn. Hạn chế là các chỉ số cắt ngang chưa phản ánh được sự biến động đường huyết liên tục theo chu kỳ ngày đêm.**

## Intelligent Agent

## Intelligent Agent là thực thể tính toán có khả năng cảm nhận môi trường thông qua các cảm biến (sensors), duy trì trạng thái nội tại và thực hiện các hành động (actions) thông qua cơ cấu chấp hành (actuators) để đạt mục tiêu dựa trên chính sách quyết định  Trong đề tài, mô hình tác tử được sử dụng để đóng gói các chức năng tính toán chuyên biệt thành các khối có trách nhiệm độc lập và giao tiếp chuẩn hóa.
Nhiệm vụ của tác tử được đặc tả theo mô hình PEAS:
Performance Measure (Độ đo hiệu năng): Tối đa hóa chỉ số F1-score trong phân loại rủi ro, tối đa hóa Recall@k trong truy xuất tài liệu y khoa và đảm bảo tỷ lệ vi phạm luật an toàn bằng 0.
Environment (Môi trường): Giao diện hỏi đáp của người dùng, cơ sở dữ liệu bệnh nhân dạng bảng, kho vector văn bản y khoa và môi trường mô phỏng đáp ứng đường huyết.
Actuators (Cơ cấu chấp hành): Lệnh định tuyến thông điệp, nhãn xác suất rủi ro, văn bản giải thích kèm trích dẫn, hành động đề xuất lối sống và cảnh báo an toàn.
Sensors (Cảm biến): Bộ tiếp nhận câu hỏi dạng văn bản tự nhiên và bộ trích xuất vector chỉsố lâm sàng.
Các loại tác tử chính được phân công cụ thể cho từng thành phần trong hệ thống:
Tác tử phản xạ dựa trên luật (Rule-based Agent): Áp dụng cho Agent an toàn nhằm kiểm tra tức thời các điều kiện cấm như kê đơn thuốc hoặc tập thể lực khi đường huyết quá cao.
Tác tử học tập (Learning Agent): Áp dụng cho Agent dự đoán (học biểu diễn bảng qua mạng nơ-ron sâu) và Agent đề xuất (học chính sách tối ưu hóa vận động qua Q-learning).
Tác tử lai kết hợp tri thức và mục tiêu (Hybrid/Deliberative Agent): Áp dụng cho Agent tri thức (GraphRAG) và Agent điều phối để quản lý bộ nhớ, phân tích ngữ cảnh và lập kế hoạch trả lời.

**Hình 2.1. Chu trình cảm nhận - ra quyết định - hành động của Tác tử thông minh**

*Phân tích Hình 2.1*

**Hình 2.1 thể hiện vòng lặp tương tác khép kín giữa tác tử và môi trường vận hành. Quan sát chính là luồng xử lý thông tin đi từ thu nhận cảm biến, cập nhật trạng thái nội tại, áp dụng chính sách suy luận đến phát sinh hành động. Ý nghĩa thiết kế là giúp module hóa các thành phần, cho phép mỗi tác tử tối ưu hóa thuật toán nội bộ mà không làm xáo trộn hệ thống. Hạn chế là tác tử đơn lẻ không thể tự giải quyết xung đột khi gặp nhiều mục tiêu đối nghịch.**

## Multi-Agent System – MAS

## Multi-Agent System là hệ thống gồm nhiều Intelligent Agent tương tác với nhau thông qua thông điệp, trạng thái chia sẻ hoặc môi trường chung để giải quyết bài toán phức hợp . So với hệ đơn tác tử, hệ đa tác tử cho phép phân tách một bài toán y tế phức tạp thành các mảng chuyên trách độc lập nhằm giảm tải ngữ cảnh cho từng mô hình và cô lập lỗi cục bộ. Tuy nhiên, hệ đa tác tử đòi hỏi chi phí tính toán cao hơn cho việc giao tiếp và cần thiết lập cơ chế kiểm soát đồng thuận để xử lý xung đột thông tin giữa các tác tử.
Trong dự án, nhóm lựa chọn mô hình điều phối phân cấp tập trung. Agent điều phối đóng vai trò trung tâm tiếp nhận yêu cầu từ người dùng, phân tích ý định và định tuyến công việc đến 4 agent chuyên trách bằng định dạng thông điệp thống nhất gồm message_id, sender, receiver, type và payload.
Thứ tự ưu tiên giải quyết xung đột được ấn định bất biến để bảo đảm tính nghiêm ngặt về y tế:

**Hình 2.2. Kiến trúc điều phối phân cấp và luồng kiểm duyệt trong Hệ đa agent**

*Phân tích Hình 2.2*

**Hình 2.2 biểu diễn mô hình phối hợp hình sao phân cấp giữa Agent điều phối và các tác tử chuyên trách. Điểm cốt lõi là toàn bộ dữ liệu tổng hợp bắt buộc phải qua Agent an toàn kiểm duyệt trước khi gửi đến người dùng. Ý nghĩa đối với thiết kế là đảm bảo các khuyến nghị luôn tuân thủ quy tắc lâm sàng. Hạn chế là Agent điều phối có thể trở thành điểm nghẽn cổ chai nếu lưu lượng truy vấn tăng cao.**

## Deep Learning cho dữ liệu bảng
Mạng nơ-ron truyền thẳng đa tầng (Multi-Layer Perceptron - MLP) là kiến trúc học sâu gồm nhiều tầng nơ-ron liên kết đầy đủ, biến đổi vector đặc trưng dạng bảng  qua các hàm biến đổi affine và hàm kích hoạt phi tuyến nhằm trích xuất biểu diễn ẩn cấp cao:
Trong đó  và  là trọng số và độ lệch có thể học;  tạo tính phi tuyến;  ánh xạ đầu ra về miền xác suất nguy cơ  . Trong hệ thống, MLP là thành phần xử lý của Agent dự đoán nhằm phân loại nguy cơ mắc bệnh từ chỉ số sức khỏe.
Mô hình được huấn luyện bằng hàm mất mát Binary Cross-Entropy (BCE):
Do dữ liệu y tế thực tế thường gặp hiện tượng mất cân bằng lớp nghiêm trọng (tỷ lệ mắc bệnh thấp hơn nhiều so với nhóm bình thường), hàm mất mát có trọng số (Class-weighted BCE) được áp dụng để cân bằng độ ảnh hưởng giữa các lớp:
Hệ thống đánh giá hiệu năng mô hình qua diện tích dưới đường cong ROC (ROC-AUC), độ nhạy (Recall) để hạn chế bỏ sót ca bệnh nguy cơ, và điểm F1-score điều hòa. Xác suất đầu ra được kiểm chuẩn (Calibration) nhằm bảo đảm điểm số dự đoán khớp với tỷ lệ rủi ro thực tế, kết hợp phân tích trọng số tầng ẩn đầu tiên để cung cấp lời giải thích cơ sở cho Agent điều phối.

## Cơ sở tri thức và RAG (KB và RAG)
Cơ sở tri thức dạng Đồ thị tri thức (Knowledge Graph - KG) là mạng ngữ nghĩa $G = (V, E)$ biểu diễn tri thức thông qua các đỉnh thực thể $V$ và cạnh quan hệ $E$ theo dạng bộ ba $(s, r, o)$ (chủ thể - quan hệ - đối tượng). Sinh văn bản tăng cường truy xuất (Retrieval-Augmented Generation - RAG) là kỹ thuật tìm kiếm các đoạn văn bản chứng minh liên quan trong kho tài liệu ngoài trước khi đưa vào mô hình ngôn ngữ để tổng hợp câu trả lời.
Trong dự án, sự kết hợp giữa KG và Vector RAG (GraphRAG) tạo thành nền tảng của Agent tri thức, giúp ngăn chặn hiện tượng tạo thông tin sai lệch và đảm bảo mọi tư vấn đều có nguồn dẫn từ tài liệu của Bộ Y tế và ADA. Quy trình thực hiện chia thành pha lập chỉ mục ngoại tuyến và pha truy xuấttrực tuyến:

**Hình 2.3. Đường ống truy xuất lai giữa Đồ thị tri thức và Vector RAG**

*Phân tích Hình 2.3*

**Hình 2.3 biểu diễn chu trình từ xử lý dữ liệu ngoại tuyến đến suy luận trực tuyến trong Agent tri thức. Điểm nổi bật là việc kết hợp đồng thời sự kiện cấu trúc từ đồ thị và bằng chứng diễn giải từ kho vector. Ý nghĩa thiết kế là cung cấp ngữ cảnh đa tầng kèm chỉ thị neo bám chặt chẽ cho mô hình ngôn ngữ. Hạn chế là hiệu quả truy xuất phụ thuộc vào chất lượng phân đoạn văn bản và độ bao phủ của bộ ba quan hệ.**

## Học tăng cường và Hệ luật (RL và Rule-Based System)
Bốn kỹ thuật chủ đạo trong hệ thống giải quyết các khía cạnh bổ trợ lẫn nhau: Deep Learning học ranh giới phân loại từ dữ liệu bảng nhưng khó diễn giải chi tiết; RAG truy xuất tài liệu mở để giải thích khái niệm nhưng phụ thuộc vào văn bản có sẵn; Học tăng cường (RL) tối ưu hóa chuỗi hành động lối sống qua tương tác thử - sai nhưng tiềm ẩn rủi ro khám phá hành vi không an toàn; Hệ luật (Rule) mang lại các chốt chặn an toàn tiền định tuyệt đối nhưng cứng nhắc và khó tự mở rộng.
Bài toán đề xuất thay đổi lối sống của Agent đề xuất được mô hình hóa theo Quá trình quyết định Markov (Markov Decision Process - MDP) gồm bộ 5 thành phần
Không gian trạng thái S: Các trạng thái sinh lý rời rạc s  =
Không gian hành động A: Các can thiệp lối sống  theo khuyến cáo của Bộ Y tế.
Mô hình chuyển trạng thái P: Xác suất chuyển sang trạng thái mới  trong môi trường mô phỏng.
Hàm phần thưởng R(s,a): Nhận giá trị dương khi nồng độ glucose máu tiến về ngưỡng an toàn từ 80 đến 130 mg/dL, nhận điểm phạt nặng nếu đường huyết giảm dưới 70 mg/dL hoặc tăng quá cao.
Hệ số chiết khấu  Xác định mức độ ưu tiên phần thưởng dài hạn.
Thuật toán Q-learning dạng bảng cập nhật giá trị hành động dựa trên sai số thời gian:
Ngược lại, Agent an toàn vận hành dựa trên tập luật xác định từ tài liệu Bộ Y tế nhằm giám sát đầu ra của Agent đề xuất và lập tức phủ quyết nếu hành động khuyến nghị tập thể lực khi đường huyết vượt quá 14,0 mmol/L kèm ceton hoặc khi người bệnh đang hạ đường huyết.

**Hình 2.4. Vòng lặp tương tác MDP của Agent đề xuất và cơ chế chốt chặn của Agent an toàn**

*Phân tích Hình 2.4*

**Hình 2.4 mô tả cơ chế tối ưu hóa hành vi của Agent đề xuất kết hợp với chốt chặn an toàn của Agent an toàn. Quan sát chính là hành động từ thuật toán Q-learning bắt buộc phải trải qua bước thẩm định luật trước khi phản hồi người dùng. Ý nghĩa thiết kế là loại bỏ hoàn toàn các đề xuất nguy hiểm từ quá trình khám phá ngẫu nhiên của học máy trong y tế. Hạn chế là mô hình mô phỏng sinh lý chưa bao quát hết tính biến động thể trạng của từng cá nhân.**

## Nghiên cứu liên quan
Nghiên cứu về ứng dụng trí tuệ nhân tạo trong y tế đã phát triển từ các mô hình học sâu hỗ trợ chẩn đoán đến các hệ thống đa tác tử ngôn ngữ lớn. Việc khảo sát các công trình liên quan từ tài liệu chuyên môn giúp nhóm định vị rõ ranh giới đóng góp và điểm khác biệt của đề tài.

| Tác giả & Năm | Hướng tiếp cận kỹ thuật | Dữ liệu thực nghiệm sử dụng | Kết quả chính đạt được | Điểm khác biệt cốt lõi với project này || --- | --- | --- | --- | --- || Tang và cộng sự (2024), MedAgents | Hệ đa agent LLM cộng tác theo vai trò chuyên khoa để suy luận y tế không mẫu (Zero-shot). | Các tập câu hỏi đáp y khoa dạng văn bản: MedQA, MedMCQA, PubMedQA. | Nâng cao độ chính xác suy luận lâm sàng so với LLM đơn lẻ thông qua phản biện đa chiều. | MedAgents thuần túy xử lý ngôn ngữ bằng LLM; dự án này tích hợp mô hình Deep Learning phân loại số bảng và RL tối ưu lối sống. || Hochberg và cộng sự (2016) | Ứng dụng Học tăng cường (RL) xây dựng hệ thống khuyến khích hoạt động thể lực cho bệnh nhân đái tháo đường. | Dữ liệu cảm biến bước chân và hoạt động thể lực theo thời gian thực của bệnh nhân. | Cải thiện mức độ tuân thủ vận động và số bước chân hàng ngày của người bệnh. | Nghiên cứu đơn tác vụ, thiếu thành phần tra cứu tri thức y khoa giải thích (RAG) và không có kiến trúc hệ đa agent điều phối. || Bothe và cộng sự (2013) | Thuật toán Học tăng cường cho bài toán kiểm soát liều lượng tuyến tụy nhân tạo (Artificial Pancreas). | Dữ liệu mô phỏng nồng độ glucose máu liên tục (CGM) theo thời gian. | Kiểm soát mức tiêm insulin tự động thích ứng với biến động đường huyết. | Can thiệp trực tiếp vào điều trị tiêm thuốc (ngoài phạm vi an toàn của project); dự án này tập trung tư vấn lối sống và giáo dục sức khỏe. || Coronato và cộng sự (2020) | Khảo sát tổng quan về các ứng dụng của Học tăng cường trong chăm sóc sức khỏe thông minh. | Tổng hợp các bộ dữ liệu y tế công khai và các ca bệnh lâm sàng thực tế. | Phân loại các thách thức cốt lõi: an toàn y tế, rủi ro thăm dò và quản lý trạng thái quan sát một phần. | Nghiên cứu mang tính tổng kết lý thuyết; dự án này hiện thực hóa một kiến trúc hệ thống thực thi cụ thể với đầy đủ 4 lớp tích hợp. |

*Phân tích Bảng 2.2*

**Bảng 2.2 phân tích so sánh các công trình nền tảng về hệ đa agent và học tăng cường trong y tế. Quan sát chính cho thấy các nghiên cứu trước đây thường tiếp cận đơn lẻ: hoặc thuần túy đối thoại ngôn ngữ (MedAgents), hoặc đơn thuần điều khiển tiêm thuốc (Bothe). Điểm khác biệt của đề tài là kiến trúc hợp nhất 4 lớp, kết nối dự đoán số học của Deep Learning, tri thức của GraphRAG và tối ưu hóa lối sống của RL dưới sự kiểm soát tuyệt đối của hệ luật an toàn. Hạn chế là hệ thống chưa thể tự động tinh chỉnh chính sách RL dựa trên phản hồi sinh học thời gian thực.**

# CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

## Yêu cầu chức năng và phi chức năng
Hệ thống được thiết kế để hỗ trợ sàng lọc rủi ro, cung cấp tri thức y khoa chuẩn mực và đề xuất thay đổi lối sống thích nghi cho bệnh nhân đái tháo đường. Nhằm bảo đảm tính khả thi trong kỹ thuật phần mềm và tuân thủ các quy tắc y tế, nhóm tiến hành phân tích chi tiết hai nhóm yêu cầu cốt lõi tại Bảng 3.1.

| Nhóm yêu cầu | Mã định danh | Tên yêu cầu | Mô tả chi tiết kỹ thuật vàTiêu chí nghiệm thu kiểm thử || --- | --- | --- | --- || Chức năng (FR) | FR1 | Thu nhận và tiền xử lý dữ liệu lâm sàng | Tiếp nhận vector chỉ số lâm sàng dạng bảng (tuổi, giới tính, BMI, Glucose đói, HbA1c, huyết áp, tiền sử tim mạch) và câu hỏi ngôn ngữ tự nhiên. Dữ liệu được mã hóa One-Hot, chuẩn hóa chuẩn hóa thang đo (StandardScaler) và kiểm tra miền giá trị hợp lệ trước khi chuyển tiếp. || Chức năng (FR) | FR2 | Phân loại nguy cơ đái tháo đường | Kích hoạt mô hình học sâu để trích xuất biểu diễn ẩn và tính toán điểm xác suất nguy cơ mắc đái tháo đường $\hat{y} \in [0, 1]$. Trả về nhãn phân loại (0: Bình thường / Tiền ĐTĐ, 1: Nguy cơ ĐTĐ cao) kèm điểm số tự tin lượng hóa. || Chức năng (FR) | FR3 | Truy xuất và giải đáp tri thức có trích dẫn | Thực hiện truy vấn lai (Hybrid Retrieval) trên Đồ thị tri thức (KG) và kho dữ liệu văn bản (Vector RAG) dựa trên câu hỏi của người dùng. Trả về văn bản giải thích chuẩn mực y khoa, kèm danh sách đoạn trích dẫn có metadata tường minh (ID tài liệu, nguồn phát hành). || Chức năng (FR) | FR4 | Đề xuất kế hoạch điều chỉnh lối sống | Sử dụng giải thuật Học tăng cường tương tác với môi trường mô phỏng để tối ưu hóa gợi ý về vận động thể lực và phân bổ dinh dưỡng. Đưa ra kế hoạch vận động tối thiểu 150 phút/tuần và cơ cấu bữa ăn giảm đường đơn phù hợp với thể trạng. || Chức năng (FR) | FR5 | Kiểm duyệt an toàn và cảnh báo khẩn cấp | Kiểm tra chéo toàn bộ dữ liệu phản hồi với tập luật y khoa tiền định nhằm ngăn chặn kê đơn thuốc và phát hiện nguy cơ cấp cứu. Chặn 100% yêu cầu kê đơn cụ thể; kích hoạt cảnh báo cấp cứu tức thì khi đường huyết $< 3,9\text{ mmol/L}$ hoặc $\ge 14,0\text{ mmol/L}$. || Chức năng (FR) | FR6 | Điều phối hội thoại và quản lý ngữ cảnh | Lưu vết phiên làm việc (Session Trace), phân tích ý định (Intent), định tuyến tác vụ đến agent chuyên trách và tổng hợp đầu ra. Khôi phục chính xác thực thể trao đổi từ bộ nhớ và điều phối đúng thứ tự luồng xử lý. || Phi chức năng (NFR) | NFR1 | Độ chính xác (Accuracy & Retrieval) | Đảm bảo chất lượng tính toán số học và truy xuất thông tin ngữ nghĩa trên toàn hệ thống. Mô hình Deep Learning đạt $F_1\text{-score} \ge 0,80$, $\text{ROC-AUC} \ge 0,85$; tầng truy xuất RAG đạt $\text{Recall@3} \ge 0,90$. || Phi chức năng (NFR) | NFR2 | Độ an toàn lâm sàng (Clinical Safety) | Loại trừ triệt để hiện tượng đưa ra lời khuyên y khoa sai lệch hoặc vượt quá phạm vi công cụ hỗ trợ. Tỷ lệ vi phạm an toàn y tế (Safety Violations) bằng 0; 100% phản hồi được thẩm định bởi Agent an toàn trước khi gửi. || Phi chức năng (NFR) | NFR3 | Thời gian phản hồi (Latency) | Đảm bảo tốc độ đáp ứng dịch vụ cho tương tác người dùng thời gian thực qua giao diện web. Độ trễ trung bình $\le 1,5$ giây cho tác vụ dự đoán số; $\le 3,5$ giây cho tác vụ truy xuất tri thức và hợp nhất ngữ cảnh đa agent. || Phi chức năng (NFR) | NFR4 | Khả năng giải thích (Explainability) | Tính minh bạch trong các quyết định số và khuyến nghị ngôn ngữ tự nhiên. Cung cấp trọng số đóng góp của các chỉ số lâm sàng (Feature Importance) và hiển thị trích dẫn nguồn văn bản cho từng câu trả lời. |

**Bảng 3.1. Danh mục yêu cầu chức năng và yêu cầu phi chức năng của hệ thống**

*Phân tích Bảng 3.1*

**Bảng 3.1 hệ thống hóa 6 yêu cầu chức năng (FR1–FR6) và 4 yêu cầu phi chức năng (NFR1–NFR4) cấu thành hệ thống. Quan sát chính cho thấy các yêu cầu chức năng bao phủ toàn bộ chu trình xử lý dữ liệu từ tiếp nhận cảm biến, suy luận tính toán, truy xuất tri thức đến kiểm duyệt an toàn. Ý nghĩa thiết kế của việc gắn kết chặt chẽ giữa FR và NFR là đặt ra các ranh giới định lượng cụ thể (độ trễ dưới 3,5 giây, Recall@3 đạt 90%, vi phạm an toàn bằng 0), ngăn chặn việc phát triển các mô hình học máy tách rời ràng buộc vận hành thực tế. Hạn chế của hệ thống chỉ tiêu này là chưa bao quát được các kịch bản đánh giá suy diễn lâm sàng nâng cao trong điều kiện bệnh nhân có đa bệnh lý phức tạp.**

## Kiến trúc tổng quan
Kiến trúc hệ thống được tổ chức thành mô hình 4 lớp phân cấp chặt chẽ, tạo sự phân tách rạch ròi về mặt trách nhiệm tính toán và bảo vệ an toàn dữ liệu y tế.

**Hình 3.1. Sơ đồ kiến trúc 4 lớp của Hệ đa agent tư vấn bệnh nhân tiểu đường**

*Phân tích chức năng theo từng lớp*
Lớp 1 (Giao tiếp): Tiếp nhận câu hỏi ngôn ngữ tự nhiên cùng bảng chỉ số xét nghiệm từ người dùng; đóng gói thành định dạng truy vấn chuẩn và hiển thị kết quả tư vấn sau khi đã được thẩm định an toàn.
Lớp 2 (Điều phối): Trung tâm vận hành của toàn bộ hệ thống, chứa Agent điều phối đảm nhận việc phân tích ý định (Intent Classification), phân rã câu hỏi thành chuỗi tác vụ con, điều phối các agent chuyên trách và hợp nhất ngữ cảnh câu trả lời theo phương trình trạng thái
Lớp 3 (Agent chuyên trách): Tập hợp 4 tác tử độc lập gồm Agent dự đoán (phân loại rủi ro số học qua MLP), Agent tri thức (truy xuất quan hệ KG và ngữ nghĩa RAG), Agent đề xuất (tối ưu hóa kế hoạch vận động/dinh dưỡng qua Q-learning), và Agent an toàn (áp dụng tập luật lâm sàng để giám sát và hiệu chỉnh kết quả).
Lớp 4 (Dữ liệu và Tri thức): Lưu trữ nền tảng tài nguyên của hệ thống gồm cơ sở dữ liệu bệnh nhân đã ẩn danh, cơ sở tri thức đồ thị và kho vector từ tài liệu chuẩn, môi trường giả lập động học sinh lý, và kho luật ngưỡng lâm sàng trích xuất từ Quyết định số 5481/QĐ-BYT cùng ADA Standards of Care.

## Luận giải 4 quyết định thiết kế cốt lõi
Tách biệt hoàn toàn Agent an toàn (Rule) khỏi Agent đề xuất (RL): Thuật toán Học tăng cường vận hành dựa trên cơ chế thăm dò ngẫu nhiên ($\epsilon$-greedy) để tìm chính sách tối ưu, tiềm ẩn rủi ro sinh ra các hành động gây hại trong y tế (như đề xuất cường độ vận động cao khi đường huyết đang ở mức nguy hiểm). Việc tách biệt cho phép Agent an toàn đóng vai trò chốt chặn ngoại vi độc lập, kiểm tra các điều kiện an toàn tiền định mà không phụ thuộc vào trạng thái huấn luyện của RL.
Trao quyền phủ quyết (Veto Power) tuyệt đối cho Agent an toàn: Hệ thống tuân thủ nguyên tắc y đức "Trước hết là không làm hại" (Primum non nocere). Khi phát hiện bất kỳ dấu hiệu vi phạm ranh giới lâm sàng (như người dùng yêu cầu kê đơn thuốc hạ đường huyết, chỉnh liều insulin, hoặc đường huyết hạ dưới $3,9\text{ mmol/L}$), Agent an toàn có quyền đình chỉ phản hồi thông thường để phát cảnh báo khẩn hoặc từ chối thực hiện, thiết lập trật tự ưu tiên:
Sử dụng Agent điều phối trung tâm thay vì mô hình mạng ngang hàng: Trong lĩnh vực y tế, việc truy vết trách nhiệm và quản lý trạng thái là yêu cầu bắt buộc. Kiến trúc hình sao có bộ điều phối tập trung giúp kiểm soát luồng thông tin tuần tự, ngăn ngừa hiện tượng lặp vô tận (infinite message loop) giữa các tác tử và bảo đảm dữ liệu đầu ra luôn được hợp nhất đầy đủ thành phần.
Mối quan hệ tương tác hai chiều giữa lớp Agent và lớp Dữ liệu: Các agent không chỉ đọc dữ liệu để suy luận mà còn liên tục ghi nhận các biến trạng thái hội thoại, lịch sử can thiệp lối sống và các cờ cảnh báo an toàn trở lại lớp dữ liệu. Cơ chế này cho phép hệ thống cập nhật hồ sơ ngữ cảnh động cho bệnh nhân qua nhiều phiên làm việc và phục vụ công tác kiểm toán hệ thống.

*Phân tích Hình 3.1*

**Hình 3.1 thể hiện cấu trúc 4 lớp và dòng chảy dữ liệu giữa các thành phần của hệ thống. Quan sát chính là vị trí cửa ngõ của Agent điều phối và vai trò kiểm duyệt chốt chặn của Agent an toàn trước khi dữ liệu được giải phóng ra Lớp giao tiếp. Ý nghĩa đối với thiết kế là đảm bảo tính module hóa cao độ, cho phép từng agent nâng cấp công nghệ bên trong mà không làm gián đoạn các thành phần khác. Hạn chế của kiến trúc là khả năng chịu tải phụ thuộc vào năng lực xử lý tập trung của Agent điều phối.**

## Đặc tả agent theo mô hình PEAS
Mô hình PEAS cung cấp phương pháp luận chuẩn xác để xác định mục tiêu đánh giá, môi trường hoạt động, cơ cấu chấp hành và cảm biến cho từng tác tử trong hệ thống.

| Agent | Độ đo hiệu năng (Performance Measure) | Môi trường (Environment) | Cơ cấu chấp hành (Actuators) | Bộ cảm biến (Sensors) | Agent || --- | --- | --- | --- | --- | --- || Agent điều phối (Coordinator) | Tỷ lệ phân loại đúng ý định ( tỷ lệ hoàn thành luồng nghiệp vụ (100%), số bước gọi công cụ tối thiểu. | Giao diện hội thoại người dùng, bus thông điệp liên agent, bộ nhớ ngữ cảnh. | Lệnh định tuyến thông điệp, bản tổng hợp câu trả lời, lệnh cập nhật bộ nhớ. | Bộ tiếp nhận chuỗi ký tự câu hỏi, gói dữ liệu trả về từ 4 agent chuyên trách. | Agent điều phối (Coordinator) || Agent dự đoán (Prediction) | sai số kiểm chuẩn (Brier score) cực tiểu. | Bảng cơ sở dữ liệu bệnh nhân, không gian trọng số mạng nơ-ron đa tầng MLP. | Vector xác suất $\hat{y} \in [0, 1]$, nhãn phân loại nguy cơ $\{0, 1\}$, vector trọng số đóng góp đặc trưng. | Bộ chuẩn hóa chỉ số lâm sàng $\mathbf{x}_{\text{clinical}}$ từ CSDL hoặc thông số người dùng nhập. | Agent dự đoán (Prediction) || Agent tri thức (Knowledge) | $\text{Recall@3} \ge 0,90$, điểm Groundedness $\ge 1,8/2,0$, không xuất hiện thông tin ảo giác. | Đồ thị tri thức NetworkX, cơ sở dữ liệu vector SentenceTransformers, kho tài liệu ADA/BYT. | Danh sách sự kiện bộ ba $(s, r, o)$, các đoạn trích dẫn $D_k$, đoạn văn bản trả lời có nguồn dẫn. | Bộ phân tích thực thể từ câu hỏi, vector nhúng truy vấn ngữ nghĩa $e_q$. | Agent tri thức (Knowledge) || Agent đề xuất (Recommendation) | Phần thưởng tích lũy hội tụ, đưa đường huyết mô phỏng về vùng an toàn ($80 - 130\text{ mg/dL}$). | Môi trường mô phỏng đáp ứng sinh lý bệnh nhân theo các mức vận động và nạp calo. | Gói đề xuất lối sống: thời lượng vận động (phút/ngày) và điều chỉnh mức calo nạp vào. | Trạng thái sinh lý hiện tại của người dùng $s = \langle \text{Glucose}, \text{BMI}, \text{Activity} \rangle$. | Agent đề xuất (Recommendation) || Agent an toàn (Safety) | Tỷ lệ phát hiện vi phạm y tế đạt $100\%$, tỷ lệ báo động giả $\le 1\%$, độ trễ kiểm tra $\le 50\text{ ms}$. | Kho luật lâm sàng tiền định từ Bộ Y tế, bản thảo câu trả lời từ Agent điều phối. | Các cờ trạng thái (PASS, VETO, MODIFY), thông điệp cảnh báo khẩn cấp cho người bệnh. | Bộ kiểm tra từ khóa cấm kê đơn, bộ so sánh ngưỡng giá trị sinh hóa với luật. | Agent an toàn (Safety) |

**Bảng 3.2. Đặc tả các thành phần tác tử theo mô hình PEAS**

*Phân tích Bảng 3.2*

**Bảng 3.2 xác lập đầy đủ 4 chiều thiết kế PEAS cho toàn bộ 5 tác tử trong hệ thống. Quan sát chính cho thấy sự chuyên môn hóa rõ rệt: Agent dự đoán chịu trách nhiệm về độ chính xác số học, Agent tri thức tối ưu hóa khả năng truy xuất đúng nguồn dẫn, Agent đề xuất hướng đến mục tiêu sinh lý dài hạn, và Agent an toàn đảm nhận kiểm soát ranh giới pháp lý lâm sàng. Ý nghĩa thiết kế là định hình rõ giao diện lập trình hướng đối tượng cho từng class agent trong mã nguồn thực thi. Hạn chế của mô hình là việc tối ưu hóa độc lập từng tác tử có thể dẫn đến hiện tượng lệch pha về độ trễ giữa các thành phần.**

## Luồng phối hợp giữa các Agent
Các kịch bản vận hành thực tế được biểu diễn qua 3 sơ đồ tuần tự chuẩn hóa theo chuẩn UML.

### Kịch bản (a): Hỏi đáp tri thức y khoa thuần túy
Kịch bản này xử lý các câu hỏi về định nghĩa, biến chứng hoặc hướng dẫn chung của bệnh nhân.

**Hình 3.2. Sơ đồ tuần tự xử lý yêu cầu hỏi đáp tri thức y khoa**

*Phân tích Hình 3.2*

**Hình 3.2 mô tả quy trình trả lời câu hỏi thông tin không chứa chỉ số xét nghiệm. Quan sát chính là đường ống khép kín từ truy xuất tri thức lai đến khâu kiểm duyệt trước khi phản hồi người dùng. Ý nghĩa là bảo đảm mọi thông tin trả lời đều được neo bám vào tài liệu của Bộ Y tế và không bị chèn các lời khuyên dược lý trái phép. Hạn chế là luồng xử lý qua nhiều bước trung gian làm tăng nhẹ độ trễ mạng.**

### Kịch bản (b): Nhập chỉ số sức khỏe, dự đoán nguy cơ, đề xuất lối sống và kiểm duyệt
Kịch bản phục vụ phiên sàng lọc định kỳ khi người dùng cung cấp bảng chỉ số xét nghiệm và câu hỏi.

**Hình 3.3. Sơ đồ tuần tự xử lý phân tích chỉ số, dự đoán rủi ro và đề xuất lối sống**

*Phân tích Hình 3.3*

**Hình 3.3 thể hiện cơ chế phối hợp đa nhánh đồng thời giữa Agent dự đoán, Agent đề xuất và Agent tri thức. Quan sát chính là khả năng xử lý song song giúp giảm thiểu độ trễ trước khi dữ liệu được hội tụ tại bước hợp nhất ngữ cảnh. Ý nghĩa thiết kế là tích hợp trọn vẹn kết quả tính toán số học với tri thức hướng dẫn hành vi dưới một cấu trúc câu trả lời duy nhất. Hạn chế là cần cơ chế đồng bộ hóa luồng (thread synchronization) chặt chẽ để tránh lỗi chạy đua.**

### Kịch bản (c): Phát hiện chỉ số nguy hiểm và kích hoạt cảnh báo khẩn cấp
Kịch bản ưu tiên bảo vệ tính mạng bệnh nhân khi phát hiện các biến chứng cấp tính nguy hiểm.

**Hình 3.4. Sơ đồ tuần tự xử lý tình huống khẩn cấp ngắt luồng thông thường**

*Phân tích Hình 3.4*

**Hình 3.4 minh họa năng lực ngắt luồng ưu tiên (Interrupt/Veto Handling) của Agent an toàn. Quan sát chính là các nhánh tính toán thông thường (mô hình dự đoán hoặc đề xuất kế hoạch vận động) bị đình chỉ hoàn toàn để hệ thống tập trung xử lý biến cố đe dọa sinh mạng theo đúng Mục 6 của Quyết định 5481/QĐ-BYT. Ý nghĩa là bảo đảm nguyên tắc an toàn lâm sàng cao nhất cho ứng dụng y tế. Hạn chế là hệ thống chỉ đóng vai trò hướng dẫn sơ cứu bước đầu, hoàn toàn phụ thuộc vào việc người bệnh tiếp cận cơ sở y tế thực tế.**

## Thiết kế dữ liệu và giao diện giữa các thành phần

## Định dạng thông điệp trao đổi liên Agent (Message Schema)
Để chuẩn hóa giao tiếp giữa các tác tử, hệ thống quy định cấu trúc dữ liệu JSON bất biến gồm 6 trường thông tin:
Các trường dữ liệu đảm nhận các chức năng cụ thể: agent xác định bên phát và bên nhận; content mang tải dữ liệu; confidence lượng hóa mức độ tin cậy; evidence lưu vết căn cứ y khoa minh bạch; flags kiểm soát rào chắn an toàn (PASS, REFUSED_SAFETY, EMERGENCY_ALERT); và trace phục vụ giám sát thời gian thực và đo lường độ trễ từng bước.

## Danh mục các giao diện lập trình ứng dụng (API Endpoints)
Hệ thống cung cấp dịch vụ qua giao diện RESTful HTTP chuẩn hóa:
POST /api/consult: Tiếp nhận gói dữ liệu người dùng (gồm câu hỏi văn bản và bảng chỉ số sức khỏe); kích hoạt toàn bộ luồng đa agent và trả về phản hồi tư vấn hợp nhất kèm nguồn trích dẫn.
POST /api/predict: Điểm cuối chuyên trách gọi riêng mô hình Deep Learning để trả về xác suất nguy cơ và mức độ quan trọng của đặc trưng từ vector số dạng bảng.
GET /api/health: Kiểm tra trạng thái sẵn sàng của hệ thống, bộ nhớ và các kết nối cơ sở dữ liệu vector/đồ thị.
GET /api/rules: Truy vấn danh mục các luật y khoa và ngưỡng an toàn đang được nạp trong bộ nhớ của Agent an toàn.

## Mô hình dữ liệu thực thể - quan hệ (ERD)
Mô hình dữ liệu của hệ thống được tổ chức để gắn kết thông tin người bệnh, lịch sử tương tác và các kho tri thức chuẩn.

**Hình 3.5. Sơ đồ mô hình dữ liệu quan hệ của hệ thống**

*Phân tích Hình 3.5*

**Hình 3.5 mô tả cấu trúc quan hệ giữa dữ liệu hồ sơ lâm sàng người dùng, chuỗi vết thông điệp đa tác tử và các kho tri thức nền tảng. Quan sát chính là sự phân định rõ ràng giữa dữ liệu động sinh ra theo phiên làm việc (CLINICAL_OBSERVATION, MESSAGE_TRACE) và các kho dữ liệu tĩnh được chuẩn hóa (KNOWLEDGE_TRIPLE, DOCUMENT_CHUNK, SAFETY_RULE). Ý nghĩa thiết kế là duy trì tính toàn vẹn dữ liệu, hỗ trợ bộ nhớ dài hạn cho tác tử và cho phép kiểm toán lâm sàng độc lập. Hạn chế là kích thước lưu trữ các vector nhúng sẽ tăng nhanh khi mở rộng kho tài liệu y khoa quy mô lớn.**
