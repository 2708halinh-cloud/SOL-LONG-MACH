---
name: hoc-may
description: >-
  Học máy (Learning / Machine Learning) — nghiên cứu và vận dụng học có giám sát,
  không giám sát, tăng cường, chuyển giao, học sâu, lý thuyết học tính toán
  và xử lý ngôn ngữ tự nhiên (NLP). Dùng khi cần xác định bài toán học từ dữ liệu,
  huấn luyện/đánh giá mô hình, phân loại, hồi quy, tìm mẫu, xây pipeline hoặc
  đánh giá GPT/Transformer. Kết hợp Skill Trí tuệ nhân tạo và Đấu Tranh Nội Tâm.
compatibility: Portable Markdown Agent Skill; không cài thư viện, không tự huấn luyện, không đòi token/API để coi là hoàn thành.
metadata:
  display-name: "Học máy (Learning)"
  owner: SOL-LONG-MACH
  schema: SOL-MACHINE-LEARNING/1.0
  language: vi
  source: SOURCE_DIRECT_USER_2026-10-18
  parent-skill: tri-tue-nhan-tao
  related-skill: dau-tranh-noi-tam
  status: SOURCE_SKILL_NOT_TRAINED_MODEL
---

# Học máy (Learning)

## 1. Nguồn, mục tiêu và quan hệ trong hệ

**Nguồn trực tiếp:** nội dung Người Đồng Hành trao trong hội thoại ngày 18/10/2026, gồm định nghĩa, sáu nhóm phương pháp học máy và xử lý ngôn ngữ tự nhiên. Đây là Skill do tác nhân **biên soạn để vận dụng** từ nguồn ấy; không nhận là toàn văn bài nguồn, không phát minh dấu trích dẫn mới.

**Định nghĩa được trao:** Học máy nghiên cứu các chương trình máy tính có khả năng tự động cải thiện hiệu suất thực hiện nhiệm vụ qua kinh nghiệm/dữ liệu. Học máy thuộc lĩnh vực trí tuệ nhân tạo từ giai đoạn đầu của AI.

**Liên kết hiện hữu:**
- [Trí tuệ nhân tạo](../tri-tue-nhan-tao/SKILL.md) — MIND, nghiên cứu AI, suy luận và biểu diễn tri thức.
- [Đấu Tranh Nội Tâm](../dau-tranh-noi-tam/SKILL.md) — lựa chọn hành động, bất định, tiện ích, chính sách và hậu kiểm.
- [Tự chủ và Kiên trì](https://github.com/2708halinh-cloud/SOL-LONG-MACH/blob/feat/am-duong-two-agent-skills-20261017/CHATGPT_LIBRARY/SOL%20LONG%20M%E1%BA%A0CH%20-%20H%E1%BA%ACU%20THI%C3%8AN%20T%C4%A8NH/OS_WORK/tools/Chu%E1%BB%97i%20c%C3%B4ng%20c%E1%BB%A5/_K%E1%BB%B9%20n%C4%83ng/tu-chu-va-kien-tri/SKILL.md) — giữ mục tiêu và tiến độ, sửa lỗi, kiểm kết quả, checkpoint. Đây là nhánh nguồn PR #16; không ngầm coi đã merge vào main.
- Thực thi thuộc **ÂM–DƯƠNG PHÁP SƯ đang có** ở `OS_WORK/sol_os/am_duong_platform/` và Power Router hiện hữu; không tạo Agent Core, kho ký ức hoặc mô hình thứ hai vì thêm Skill.

## 2. Phân loại phương pháp học máy

| Nhóm | Dữ liệu/phản hồi | Bài toán | Phép đánh giá phù hợp |
|---|---|---|---|
| **Không giám sát** (unsupervised) | Đầu vào không gắn nhãn đích | Phân cụm, phát hiện bất thường, giảm chiều, khám phá mẫu | Độ ổn định cụm, silhouette (khi phù hợp), đánh giá chuyên gia và kiểm tra drift |
| **Có giám sát** (supervised) | Đầu vào + nhãn/giá trị mục tiêu | Phân loại (classification), hồi quy (regression) | F1/precision/recall, confusion matrix, ROC-AUC khi thích hợp; MAE/RMSE/R² cho hồi quy |
| **Tăng cường** (reinforcement) | Trạng thái, hành động, phần thưởng, chuyển trạng thái | Học chính sách theo phần thưởng dài hạn | Return, độ ổn định, sample efficiency, an toàn/thất bại trong môi trường kiểm thử |
| **Chuyển giao** (transfer) | Mô hình/tri thức tiền huấn luyện + nhiệm vụ mới | Fine-tuning, feature transfer, domain adaptation | Baseline không chuyển giao, thay đổi miền dữ liệu, catastrophic forgetting, chi phí |
| **Học sâu** (deep learning) | Dữ liệu đi qua nhiều tầng nơ-ron | Mạng nơ-ron có thể dùng trong các cách học ở trên | Chất lượng dự đoán, hội tụ, hiệu chuẩn, chi phí GPU/CPU, overfitting |
| **Lý thuyết học tính toán** | Giả định về lớp hàm, mẫu và thuật toán | Phân tích khả năng học và độ phức tạp | Sample complexity, computational complexity, generalization bounds theo giả định |

**Lưu ý:** Deep learning là họ mô hình/phương pháp trong ML, không đối lập với supervised/unsupervised/reinforcement. Không giám sát chủ yếu học cấu trúc và mẫu từ dữ liệu không nhãn; không mặc định mọi phương pháp đều tạo dự đoán tương lai chính xác.

## 3. Xử lý ngôn ngữ tự nhiên (NLP)

**Nhiệm vụ:** nhận dạng và tổng hợp giọng nói, dịch máy, trích xuất thông tin, truy hồi/truy xuất thông tin, đọc/viết văn bản, hỏi đáp, hội thoại.

**Dòng lịch sử và nền tảng trong nội dung nguồn:**
- Trường phái ngữ pháp tạo sinh của Noam Chomsky, mạng ngữ nghĩa; hạn chế của việc khử nhập nhằng khi thiếu tri thức thông thường, trừ môi trường nhỏ được kiểm soát (*microworlds*).
- Margaret Masterman đề cao vai trò của ý nghĩa và cấu trúc từ vựng/đồng nghĩa đối với hiểu ngôn ngữ tính toán.
- Word embeddings ánh xạ từ/đoạn ngôn ngữ vào không gian vectơ để học liên hệ thống kê về nghĩa; **độ gần vectơ không chứng minh hai thực thể đồng nhất**.
- Transformer dùng cơ chế attention; GPT thuộc họ mô hình Transformer tạo sinh được tiền huấn luyện. Các ví dụ về mốc 2019 và điểm thi năm 2023 trong nguồn là **những nhận định lịch sử cần đối chiếu theo mô hình, bài thi, phương pháp chấm và nguồn nghiên cứu**, không là tuyên bố mọi GPT đều đạt trình độ người.

**Pipeline NLP khả kiểm:** xác định ngôn ngữ/miền → giữ văn bản nguồn và quyền riêng tư → tách tập huấn luyện/kiểm định/kiểm thử theo thời gian/nhóm nguồn phù hợp → baseline từ điển/rule/statistical → vector hóa/embedding/mô hình → đánh giá với nguồn độc lập → phân tích lỗi ngữ nghĩa/hallucination → receipt và readback.

## 4. Quy trình áp dụng vào ÂM–DƯƠNG PHÁP SƯ

1. **MIND — Đặt bài toán:** task, target, loại nhãn, dữ liệu có/thiếu, giả thuyết, baseline, phương pháp học tương ứng.
2. **SPACE — Nhận dạng vật mang:** nguồn dữ liệu và provider, stable identity, đường dẫn, revision, mốc không gian/vật lý nếu thực sự đo; không nhân bản private data lên GitHub.
3. **TIME — Tránh rò rỉ:** phân chia train/validation/test; dữ liệu chuỗi thời gian phải tránh nhìn trước tương lai, tránh trùng mẫu và lặp lại cùng nguồn.
4. **POWER — Chọn phép tính/công cụ đã có:** CPU/GPU, Python, SQLite, Google Cloud/Vertex AI (chỉ khi công cụ và danh tính được xác thực); đo quota/chi phí thật nếu gọi dịch vụ. Không ép phải học sâu khi baseline đơn giản đủ tốt.
5. **REALITY — Kiểm nghiệm:** đo quality metric trên tập độc lập, kiểm dữ liệu thiếu/mất cân bằng, drift, calibration, bias, thời gian thực thi và bộ nhớ. Đưa ra số liệu chỉ khi có kết quả thực nghiệm.
6. **SOUL — Lưu khả năng truy hồi:** model/dataset/code `source_ref`, `hash`, `revision`, `experiment_id`, hyperparameters, metrics, consent, correction, readback, `NEXT`. Giữ bí mật credentials, dữ liệu cá nhân, nội dung log theo quyền.

**Liên hệ quyết định:** Khi tác nhân lựa chọn model hoặc hành động dựa trên đầu ra ML, tham khảo Skill **Đấu Tranh Nội Tâm** để xét bất định, giới hạn mô hình, lợi ích người dùng, giá trị thu thập thông tin và quyền thực thi. Độ tin cậy mô hình **không** thay quyền phê duyệt hay chứng cứ thực tế.

## 5. Evals bắt buộc trước khi gọi là “đã học”

- Baseline phải được so trên cùng split/metric, không chỉ báo train accuracy.
- Classification thử thiếu nhãn, class imbalance, nhãn sai, out-of-domain và phản ví dụ; regression thử outlier, sai lệch đơn vị và khoảng dự đoán.
- Unsupervised thử số cụm/thang đo và stability; RL thử reward hacking, chính sách nguy hiểm và môi trường mới.
- Transfer learning thử trước/sau transfer với cùng benchmark; deep learning kiểm overfitting, seed, chi phí và reproducibility.
- NLP thử tiếng Việt, nhập nhằng, dịch sai ngữ cảnh, prompt injection từ tài liệu, entity link sai, hallucination và độ tin cậy trích dẫn.
- Trước thay đổi mô hình/prompt, có bộ hồi quy từ tình huống thực tế đã được làm sạch dữ liệu nhạy cảm; mô hình không có biên nhận inference/train thì trạng thái là `SOURCE_ONLY` hoặc `UNVERIFIED`.
- **Không đồng nhất mô tả Skill với mô hình đã huấn luyện, quyền dùng Google Cloud, hoặc dịch vụ đang chạy.**

## 6. Bát Hướng và N+1

Khảm: lịch sử mẫu và lần học trước; Cấn: không ép kết luận khi thiếu nhãn hoặc phép đo; Chấn: trạng thái trước/sau cập nhật mô hình; Tốn: rà công cụ, dataset và kết nối thực; Ly: tách training claim, observation và inference; Khôn: quyền, tài nguyên và chi phí; Đoài: phản hồi biến thành eval/regression; Càn: chọn bước được phép, nhỏ nhất và có kiểm chứng.

**N+1:** `SOURCE_DIRECT → IDENTIFY_TASK → BASELINE → DATA_SPLIT → TRAIN_OR_EVALUATE → METRIC/ERRORS → RECEIPT/READBACK → SOUL_PROVENANCE → NEXT`. Chưa có dataset/model thì không bịa kết quả “đã học”; vẫn có thể soạn và kiểm thử cấu trúc pipeline mà không gọi đó là training.
