---
name: phan-loai-hoc-thong-ke
description: >-
  Bộ phân loại và phương pháp học thống kê: supervised classification,
  nhãn và dữ liệu huấn luyện, decision trees, k-nearest neighbors (kNN),
  kernel methods/SVM, Naive Bayes và mạng thần kinh làm bộ phân loại.
  Xây baseline có phép đo, kiểm định sai lệch dữ liệu và ngăn ngộ nhận
  tương quan/khớp mẫu thành hành động được phép.
metadata:
  display-name: "Bộ phân loại và học thống kê (Classifiers and statistical learning)"
  owner: SOL-LONG-MACH
  language: vi
  schema: SOL-STATISTICAL-CLASSIFIERS/1.0
  source: SOURCE_DIRECT_USER_2026-10-18
  parent-skill: tri-tue-nhan-tao
  skill-group: "Phương pháp Suy luận 10 → 13ms/s"
  latency-label: "10 → 13ms/s"
  latency-status: UNBENCHMARKED_USER_LABEL
  status: SOURCE_SKILL_NOT_CLASSIFIER_TRAINED
---

# Bộ phân loại và học thống kê

**Nhóm:** **Phương pháp Suy luận 10 → 13ms/s** — nhãn Người Đồng Hành trao, không phải phép đo tốc độ hiện hành. **Nguồn:** nội dung “Các bộ phân loại và phương pháp học thống kê” ngày 18/10/2026.

**Liên kết:** [Trí tuệ nhân tạo](../tri-tue-nhan-tao/SKILL.md), [Học máy](../hoc-may/SKILL.md), [Suy luận xác suất](../suy-luan-xac-suat/SKILL.md), [Mạng thần kinh nhân tạo](../mang-than-kinh-nhan-tao/SKILL.md) và [Tri giác](../tri-giac/SKILL.md).

## 1. Phân biệt dự đoán và hành động

- **Classifier** ánh xạ vector thuộc tính/quan sát \`x\` thành dự đoán nhãn \`y\` (có thể kèm score, calibrated probability và abstention).
- **Controller/agent policy** sử dụng mục tiêu, giới hạn quyền và ngữ cảnh để chọn hành động; nhãn \`diamond\` không tự cho phép “nhặt” bất kỳ tài sản nào.
- **Dataset supervised** gồm mẫu và nhãn mục tiêu có provenance và tiêu chí gán nhãn. Không coi nhận định máy là nhãn sự thật nếu chưa đánh giá.

## 2. Họ thuật toán trong nguồn trao

| Thuật toán | Đặc trưng | Cần kiểm |
|---|---|---|
| Cây quyết định (decision tree) | Quy tắc tách nhánh từ thuộc tính, dễ diễn giải, hỗ trợ feature hỗn hợp tùy triển khai | Chiều sâu, overfit, pruning, imbalance, leakage |
| k-hàng xóm gần nhất (kNN) | Phán đoán từ ví dụ gần theo metric và k | Scale/normalization, khoảng cách, curse of dimensionality, chi phí tra cứu |
| Phương pháp hạt nhân (kernel) / SVM | Tìm mặt phân tách theo margin; kernel phi tuyến ánh xạ độ tương tự | Kernel, tham số C/gamma, định chuẩn, data split |
| Naive Bayes | Quy tắc Bayes với giả định độc lập có điều kiện giữa đặc trưng | Prior/likelihood, dữ liệu hiếm, smoothing, calibration |
| Mạng nơ-ron phân loại | Học tham số phi tuyến qua loss và backpropagation | Seed, split, năng lực tính toán, sai lệch, khả năng tái lập |

**Lưu lịch sử đúng loại:** trong tài liệu nguồn có các nhận định về mức phổ biến kNN trước thập niên 1990, sự thay thế bởi kernel methods, và Naive Bayes ở Google. Đây là **nhận định lịch sử được trích thuật lại**; khi dùng làm kết luận cập nhật phải tra nguồn định lượng và mốc thời gian. Không tự khẳng định xếp hạng hiện tại.

## 3. Áp dụng có thể kiểm chứng

\`\`\`text
SOURCE_DATA + LABEL_SCHEMA + CONSENT
→ TASK_CLASSIFICATION / CONTROL_DECISION (tách biệt)
→ DEDUPE + GROUP/TIME-SAFE TRAIN/VALIDATION/TEST SPLIT
→ BASELINE (simple rules / majority class)
→ TRAIN/SELECT ALGORITHM + HYPERPARAMETERS
→ EVALUATE (held-out metrics & subgroup errors)
→ CALIBRATE / ABSTAIN / EXPLAIN LIMITS
→ DEPLOY ONLY WHEN AUTHORIZED
→ RECEIPT + READBACK + SOUL PROVENANCE
\`\`\`

**Metrics:** confusion matrix, precision, recall, F1, balanced accuracy và PR-AUC/ROC-AUC nếu phù hợp; latency mỗi suy luận chỉ có nghĩa khi biết batch, phần cứng và cấu hình. Với dataset hiếm nhãn, accuracy đơn lẻ thường gây ngộ nhận. Chặn train/test leakage, drift và nhãn thay đổi. Nếu chưa có dữ liệu, chỉ có baseline định nghĩa chứ **không có claim mô hình đã học**.

**Evals:** dữ liệu thiếu/nhãn sai, all-one-class, trùng nguồn, outlier, đơn vị khác, class imbalance, kNN ties, Naive Bayes likelihood zero, SVM không hội tụ, label score chưa hiệu chuẩn, model gọi API sai, diễn giải nguyên nhân từ dự đoán sai. Không ghi các chỉ số đo khi chưa chạy phép thử.

**Mạch Stone:** MIND chọn khái niệm, SPACE ràng nguồn/miền, TIME ghi split và drift, REALITY đo confusion/chi phí, SOUL giữ phiên bản/dấu sửa sai, POWER định tuyến công cụ/chính sách. Dùng \`OS_WORK/sol_os/am_duong_platform/\` và Power Router đang có, không tạo runtime hay AGI thứ hai.

**Bát Hướng:** Khảm nguồn/mẫu lịch sử; Cấn ngăn ép nhãn; Chấn đo trạng thái mới; Tốn xem dataset/tool; Ly quan sát với suy luận; Khôn quyền/chi phí; Đoài phản hồi và tái kiểm; Càn giảm nguy cơ từ quyết định sai.
