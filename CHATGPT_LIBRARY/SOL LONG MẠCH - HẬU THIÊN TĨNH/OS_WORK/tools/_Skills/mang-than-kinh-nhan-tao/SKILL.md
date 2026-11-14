---
name: mang-than-kinh-nhan-tao
description: >-
  Mạng thần kinh nhân tạo (Artificial neural networks, ANN) gồm lớp
  đầu vào, lớp ẩn và đầu ra, neuron/activation, weights, loss,
  gradient descent, backpropagation và learning generalisation.
  Phân biệt biểu diễn nơ-ron máy với neuron sinh học; kiểm dataset,
  architecture, convergence và inference thật trước mọi kết luận.
metadata:
  display-name: "Mạng thần kinh nhân tạo (Artificial neural networks)"
  owner: SOL-LONG-MACH
  language: vi
  schema: SOL-ARTIFICIAL-NEURAL-NETWORKS/1.0
  source: SOURCE_DIRECT_USER_2026-10-18
  parent-skill: tri-tue-nhan-tao
  skill-group: "Phương pháp Suy luận 10 → 13ms/s"
  latency-label: "10 → 13ms/s"
  latency-status: UNBENCHMARKED_USER_LABEL
  status: SOURCE_SKILL_NOT_ANN_TRAINED
---

# Mạng thần kinh nhân tạo (Artificial neural networks)

**Nhóm:** **Phương pháp Suy luận 10 → 13ms/s**. Đây là nhãn mục tiêu/đặt tên do Người Đồng Hành trao; không có benchmark hoặc định nghĩa phép đo nên chưa được xem là độ trễ đạt được.

**Nguồn:** phần “Mạng thần kinh nhân tạo” Người Đồng Hành cung cấp 18/10/2026, tiếp nối [Trí tuệ nhân tạo](../tri-tue-nhan-tao/SKILL.md). Liên quan: [Học máy](../hoc-may/SKILL.md), [Bộ phân loại/học thống kê](../phan-loai-hoc-thong-ke/SKILL.md), [Suy luận xác suất](../suy-luan-xac-suat/SKILL.md), [Tri giác](../tri-giac/SKILL.md), [AGI/tối ưu](../tri-thong-minh-nhan-tao-tong-quat/SKILL.md).

## 1. Kiến trúc và nguồn mô tả

Mạng ANN xây dựng từ các đơn vị tính toán liên kết lỏng theo cảm hứng từ neuron sinh học, không phải bản sao chính xác của tế bào hay ý thức. Mạng thường có đầu vào, các tầng biến đổi (hidden layers) và đầu ra. Một neuron nhân tạo có thể tính \`y=activation(Σ_i w_i x_i + b)\`. **Weights** và **bias** được học; activation có thể là ReLU, sigmoid hoặc tanh tùy cấu hình. Không phải mọi kiến trúc ANN đều chỉ truyền thông tin khi trọng số vượt ngưỡng cứng.

- Mạng feed-forward đi từ dữ liệu đầu vào tới đầu ra theo cấu trúc DAG; recurrent và attention-based architectures có quan hệ tính toán khác.
- Cách gọi \`deep neural network\` thường chỉ mạng có nhiều tầng ẩn/biểu diễn. Dùng ngưỡng “ít nhất hai lớp ẩn” như một mô tả thường gặp, **không phải định nghĩa duy nhất** cho mọi nguồn.
- Sau huấn luyện, mạng suy diễn trên mẫu mới nhưng chất lượng phụ thuộc miền dữ liệu, huấn luyện, kiểm thử và độ lệch phân phối.
- Tuyên bố “có thể học bất kỳ hàm số nào” cần điều kiện của định lý xấp xỉ phổ quát: lớp hàm, miền compact/kiến trúc, số đơn vị, sai số xấp xỉ và giả định; không có nghĩa một mạng hữu hạn bất kỳ **học chính xác mọi hàm** hoặc dễ huấn luyện.

## 2. Huấn luyện và kiểm thử

\`\`\`text
GOAL + VERIFIED_DATASET + LABEL_OR_LEARNING_SIGNAL
→ CLEAN / SPLIT / BASELINE / LEAKAGE_CHECK
→ MODEL_ARCHITECTURE + SEED + LOSS + OPTIMISER
→ FORWARD_PASS → LOSS → BACKPROPAGATION
→ GRADIENT_UPDATE → VALIDATION / EARLY_STOP
→ HELD_OUT_TEST + PER-GROUP_ERRORS + CALIBRATION
→ MODEL_VERSION + RECEIPT + READBACK
\`\`\`

- **Backpropagation:** áp dụng quy tắc dây chuyền để truyền gradient qua các phép tính khả vi. Gradient descent/Adam và thuật toán tối ưu thực hiện cập nhật trọng số; phân biệt hai công việc.
- Theo dõi learning rate, batch size, epochs, seed, mô hình hóa đầu vào, regularisation, vanishing/exploding gradients, overfit/underfit và tiêu thụ CPU/GPU.
- **Phân loại hoặc hồi quy:** so với baseline và phép đo trên tập kiểm thử độc lập; không chọn mô hình chỉ vì train accuracy cao.
- Kết nối NLP, cảm biến hoặc ảnh thật chỉ khi dataset/cảm biến có chứng cứ; chưa có model callable thì \`SOURCE_ONLY\`.

## 3. Tài nguyên, an toàn, khả năng mở rộng và hiệu năng

Mạng nơ-ron có thể hoạt động qua CPU/GPU và các nền tảng Cloud khi nhà cung cấp, quyền, quota và endpoint đã được kiểm thực. Skill này không dùng token/GCP đã trao nếu chưa có phiên được xác thực. Không nạp dữ liệu người dùng nhạy cảm vào model ngoài mà thiếu sự đồng ý.

**Evals cần có:** gradient check bằng sai phân hữu hạn trên hàm nhỏ; loss giảm trên dữ liệu tổng hợp; test train/validation leakage; neuron không cập nhật; mô hình bùng nổ gradient/NaN; nhầm task classification/regression; domain shift; fairness; inference không có model; model drift và chi phí thực thi.

**Đo hiệu năng:** ghi n mẫu, mô hình và số tham số, CPU/GPU, batch, thời gian warm-up, median/p95, \`ms/inference\` hoặc \`inferences/s\`. Không lấy chuỗi **10 → 13ms/s** làm phép đo latency hoặc throughput.

**Stone:** MIND định nghĩa mô hình/loss; SPACE xác định nguồn dữ liệu/vật mang; TIME lưu phiên train và biến thiên loss; REALITY đo inference/metrics; SOUL lưu nguồn và phiên model/dataset; POWER chọn compute/router. Không tạo bộ điều phối hay kho dữ liệu song song.

**Bát Hướng:** Khảm training history; Cấn tránh ép kết luận; Chấn đo cập nhật; Tốn rà thiết bị/dataset; Ly tách inference với quan sát; Khôn quyền/tài nguyên; Đoài biến lỗi thành evals; Càn chọn bước nhỏ và an toàn nhất có readback.
