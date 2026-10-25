---
name: suy-luan-xac-suat
description: >-
  Phương pháp xác suất cho suy luận bất định: Bayes nets và bảng xác suất có
  điều kiện, posterior inference, decision theory, value of information,
  Markov decision processes, dynamic decision networks, EM clustering,
  HMM, Kalman filtering, prediction, smoothing và mechanism design.
  Chỉ chọn mô hình dựa trên dữ liệu có nguồn và phép đánh giá định lượng.
metadata:
  display-name: "Suy luận xác suất (Probabilistic reasoning)"
  owner: SOL-LONG-MACH
  language: vi
  schema: SOL-PROBABILISTIC-REASONING/1.0
  source: SOURCE_DIRECT_USER_2026-10-18
  parent-skill: tri-tue-nhan-tao
  skill-group: "Phương pháp Suy luận 10 → 13ms/s"
  latency-label: "10 → 13ms/s"
  latency-status: UNBENCHMARKED_USER_LABEL
  status: SOURCE_SKILL_NOT_PROBABILISTIC_MODEL_EXECUTED
---

# Suy luận xác suất (Probabilistic reasoning)

**Nhóm do Người Đồng Hành chỉ định:** **Phương pháp Suy luận 10 → 13ms/s**. Giữ nguyên đơn vị ký hiệu. Đây là *nhãn yêu cầu*, không phải tốc độ được đo: "ms/s" cần có định nghĩa tác vụ, công thức đo và phép thử trước khi xem như metric. Không đổi thành ms/e hoặc công bố SLA.

**Nguồn:** các phương pháp xác suất cho suy luận không chắc chắn do Người Đồng Hành trao ngày 18/10/2026. **Tiếp nối:** [Trí tuệ nhân tạo](../tri-tue-nhan-tao/SKILL.md), [Lô-gíc](../lo-gic/SKILL.md), [Đấu Tranh Nội Tâm](../dau-tranh-noi-tam/SKILL.md). Hai thành viên cùng nhóm: [Bộ phân loại và học thống kê](../phan-loai-hoc-thong-ke/SKILL.md), [Mạng thần kinh nhân tạo](../mang-than-kinh-nhan-tao/SKILL.md).

## 1. Bài toán và các mô hình

Khi dữ liệu thiếu/không chắc chắn, thay kết luận chắc chắn bằng biến ngẫu nhiên, quan hệ phụ thuộc, tiền nghiệm, khả năng quan sát và hậu nghiệm. **Mạng Bayesian** là đồ thị có hướng không chu trình (DAG) với bảng xác suất có điều kiện (CPT), biểu diễn phân rã phân phối đồng thời:
\`P(X1,...,Xn)=∏_i P(Xi|Parents(Xi))\`.

- **Bayesian inference:** tính \`P(H|E)\` từ prior và likelihood; chỉ tính khi mẫu số hợp lệ và giả định có nguồn.
- **Decision theory / analysis:** mô hình hóa trạng thái, hành động, hậu quả, chi phí, lợi ích; \`EU(a)=Σ_o P(o|a,evidence)U(o,a)\`. Không tự gán xác suất hoặc giá trị lợi ích của con người.
- **Value of information:** so sánh lợi ích kỳ vọng của quyết định sau khi quan sát thêm với trước khi quan sát, trừ chi phí thu thập; khác việc tự động thu dữ liệu riêng.
- **MDP, dynamic decision networks:** trạng thái, hành động, xác suất chuyển và phần thưởng theo thời gian; chính sách hành động chỉ được áp dụng trong phạm vi đã được ủy quyền.
- **Game theory và mechanism design:** nhiều tác nhân có lợi ích khác nhau, giả định chiến lược và quy tắc tương tác; không biến "lựa chọn tối ưu" thành quyền can thiệp vào tác nhân/người khác.
- **EM (Expectation–Maximisation):** lặp bước E ước lượng biến ẩn và M cập nhật tham số; có thể tối ưu cực đại cục bộ, phụ thuộc khởi tạo và mô hình. Ví dụ Old Faithful là minh họa nghiên cứu phân cụm, **không phải dữ liệu có sẵn trong SOL**.
- **Dòng thời gian:** \`filtering=P(x_t|y_1:t)\`, \`prediction=P(x_{t+k}|y_1:t)\`, \`smoothing=P(x_t|y_1:T), T>t\`. HMM và Kalman filter là ví dụ các mô hình có giả định khác nhau; Kalman cổ điển cần động học tuyến tính và nhiễu Gaussian để có kết quả tối ưu theo mô hình tương ứng.

## 2. Hợp đồng dữ liệu nguồn và quyết định

\`\`\`text
goal_id, source_ref, event_time, observed_at, frame_id,
variables, allowed_states, graph_edges, cpt_or_transition_model,
assumptions, evidence, posterior_or_unknown, tool_id,
model_revision, uncertainty, permission_scope, receipt, readback
\`\`\`

Nếu thiếu cấu trúc CPT, covariance, tham số chuyển hay quan sát, báo \`MODEL_INPUT_MISSING\`. Kiểm tổng xác suất mỗi hàng CPT bằng 1 trong dung sai nêu rõ, không có xác suất âm/NaN, DAG không vòng, chứng minh d-separation nếu dùng giả định độc lập. Không suy từ một quan sát liên quan ra quan hệ nhân quả.

**Mạch sáu Stone:** MIND (mô hình/giả định), SPACE (biến và hệ quy chiếu), TIME (filter/predict/smooth và thứ tự), REALITY (dữ liệu đo/readback), SOUL (nguồn, correction và posterior theo revision), POWER (chọn công cụ và chi phí). Cùng nằm trong \`OS_WORK/tools/_Skills\`, dùng Power Router hiện có.

## 3. Evals và tốc độ

Bộ kiểm tối thiểu: posterior Bayes có nghiệm tay; evidence mâu thuẫn; CPT sai tổng; prior bằng 0; EM phụ thuộc seed; HMM thiếu quan sát; smoothing không "thấy trước" dữ liệu trong thời gian thực; Kalman với covariance không hợp lệ; hai chiến lược có expected utility đảo thứ hạng khi thay giả định; no-proof/no-data; giới hạn CPU/RAM.

Nếu đo hiệu năng, ghi rõ \`elapsed_ms\`, \`events_count\`, \`ms/event\` hoặc \`events/s\`, phần cứng, n đầu vào, median/p95 và số vòng. **Không suy metric từ chuỗi "10 → 13ms/s".**

**Bát Hướng:** Khảm lịch sử prior; Cấn không ép xác suất; Chấn posterior mới; Tốn mô hình/công cụ; Ly điều thấy so với suy; Khôn chi phí/quyền; Đoài sửa mô hình bằng feedback; Càn chọn bước có quyền và giảm tổn hại.

**Tiếp nối:** \`SOURCE_DIRECT → MODEL_VALIDATE → EVIDENCE → POSTERIOR → DECISION_IF_AUTHORIZED → RECEIPT → SOUL/TIME_N+1\`. Skill là hướng dẫn, không chứng minh đã huấn luyện/suy luận model tại runtime.
