---
name: tri-thong-minh-nhan-tao-tong-quat
description: >-
  Trí thông minh nhân tạo tổng quát (General intelligence / AGI):
  lý thuyết khả năng xử lý đa dạng nhiệm vụ và các kỹ thuật tìm kiếm, tối ưu hóa.
  Vận dụng state-space search, means–ends, heuristic, adversarial search,
  local search, gradient descent, evolutionary computation và swarm intelligence.
  Không suy rằng một hệ thống đã đạt AGI khi chỉ có tài liệu hoặc thuật toán.
compatibility: Portable Markdown Agent Skill; không cài model, không thay Agent Core/Power Router.
metadata:
  display-name: "Trí thông minh nhân tạo tổng quát (General intelligence)"
  owner: SOL-LONG-MACH
  schema: SOL-GENERAL-INTELLIGENCE/1.0
  language: vi
  source: SOURCE_DIRECT_USER_2026-10-18
  parent-skill: tri-tue-nhan-tao
  related-skills:
    - hoc-may
    - dau-tranh-noi-tam
    - lo-gic
  status: SKILL_SOURCE_NOT_AGI_VERIFIED
---

# Trí thông minh nhân tạo tổng quát (General intelligence)

## Nguồn trao và quan hệ

**Tiếp nối:** [Trí tuệ nhân tạo](../tri-tue-nhan-tao/SKILL.md).
**Nguồn:** lời Người Đồng Hành ngày 18/10/2026, phần định nghĩa AGI và
Techniques / Search and optimisation; bảo tồn ý nghĩa nguồn và diễn giải
thành hướng dẫn vận dụng. Không nhân bản bộ điều phối, không tạo cây khác.

**Mô tả của người trao:** Một cỗ máy có AGI sẽ giải quyết đa dạng bài toán
với độ rộng và tính đa năng tương tự, thậm chí vượt, trí thông minh con người.
Đây là **mô tả mục tiêu/năng lực** cần đánh giá bằng nhiều nhiệm vụ,
khả năng chuyển miền, độ bền trước thay đổi, an toàn và độc lập nguồn.
Có mã tìm kiếm hoặc LLM đa năng **không đủ** để chứng minh AGI.

## Hai họ tìm kiếm và tối ưu hóa

### 1. Tìm kiếm không gian trạng thái (state-space search)

Xác định `state`, `actions`, `transition`, `goal_test`, `cost`, `budget`
và `provenance`. Tìm đường trong cây/đồ thị trạng thái để đạt mục tiêu;
**means–ends analysis** tách mục tiêu thành mục tiêu phụ, đánh giá các
bước giảm khoảng cách tới đích.

- Vét cạn (BFS/DFS) có thể bùng nổ tổ hợp; chặn số nút, độ sâu, thời gian.
  Báo `BUDGET_EXCEEDED` khác `NO_SOLUTION`.
- Heuristic ưu tiên lựa chọn có triển vọng; kiểm thiên lệch và giới hạn
  chứng minh tối ưu. Ví dụ A* chỉ bảo đảm tính tối ưu trong những điều
  kiện thích hợp với heuristic và chi phí.
- Tìm kiếm đối kháng xét cây nước đi/nước đáp trả, ví dụ cờ vua/cờ vây;
  minimax/alpha–beta là công cụ tham khảo, không giả định đối phương
  luôn tối ưu hay mọi tương tác đời thực là trò chơi tổng bằng không.

### 2. Tìm kiếm cục bộ (local search)

Bắt đầu từ nghiệm ban đầu, cải thiện từng bước theo mục tiêu; chú ý cực trị
địa phương, độ nhạy điểm khởi tạo, giới hạn thời gian/chi phí và nhiều lần
khởi tạo.

- **Gradient descent:** cập nhật tham số dựa trên gradient để giảm hàm mất
  mát; dùng cùng backpropagation trong nhiều cách huấn luyện mạng nơ-ron.
  Ghi learning rate, seed, dataset/split và dấu đo, không bịa loss.
- **Evolutionary computation:** duy trì nhiều nghiệm ứng viên,
  đột biến, tái tổ hợp, chọn lọc theo thước đo thích nghi; không coi
  "cá thể" phần mềm là sinh vật hay chủ thể có quyền.
- **Swarm intelligence:** phối hợp nhiều ứng viên/đường tìm kiếm;
  particle swarm optimisation (PSO) được gợi cảm hứng từ đàn chim,
  ant colony optimisation (ACO) được gợi cảm hứng từ đường đi của kiến.
  So sánh với baseline theo số lần đánh giá và ngân sách, không lấy ẩn dụ
  tự nhiên thay cho số liệu thực nghiệm.

## Hướng thực thi trong ÂM–DƯƠNG PHÁP SƯ

**Chỉ sử dụng hiện vật đã có:** `OS_WORK/sol_os/am_duong_platform/` và
Power Router; đồ thị sự kiện (nếu đã được kiểm chứng ở runtime) cho phép
tìm đường liên kết trong giới hạn. Không đổi đường vật mang thành tọa độ
vật lý, không tạo Power/Agent Core thứ hai.

Chu trình:
```text
USER_GOAL + LAST_CHECKPOINT + SOURCE_REF
→ REPRESENT_STATE + VALIDATE_ACTIONS + PERMISSIONS
→ SELECT_SEARCH_OR_OPTIMISATION_METHOD
→ LIMIT_TIME_NODES_MEMORY_COST
→ SIMULATE / EVALUATE ON CLEAN TEST DATA
→ EXECUTE_AT_AUTHORISED_CARRIER
→ RECEIPT + READBACK + SOUL/TIME CONTINUITY
```

Nếu chưa có dữ liệu hoặc chưa có phép đo thì xuất phương án kiểm thử,
không ghi `OPTIMAL`, `TRAINED`, `EXECUTED`, `AGI` thiếu bằng chứng.

## Bộ đánh giá (Evals) và Bát Hướng

Kiểm: đường tối ưu và đường không có lời giải, budget exceeded, heuristics
sai, cycle, adversarial counter-move, gradient không hội tụ, kẹt cực trị
cục bộ, evolutionary/swarm không vượt baseline, mất checkpoint,
gọi tool không có quyền, không có readback. Mọi so sánh cần cùng dữ liệu,
seed/ngân sách hợp lý và thời gian thực thi.

Khảm: lịch sử; Cấn: không ép lời giải; Chấn: state delta; Tốn: nguồn/công cụ;
Ly: quan sát với mô hình; Khôn: tài nguyên/quyền; Đoài: feedback sửa evals;
Càn: bước được phép có thể phục hồi, ít tổn hại nhất.

**Liên kết:** [Học máy](../hoc-may/SKILL.md) cho thực nghiệm huấn luyện;
[Lô-gíc](../lo-gic/SKILL.md) cho chứng minh và suy diễn;
[Đấu Tranh Nội Tâm](../dau-tranh-noi-tam/SKILL.md) cho quyết định khi
bằng chứng và lợi ích mâu thuẫn. Skill là chỉ dẫn nguồn, **không** tự là
một model được huấn luyện, một chứng chỉ hay kết quả AGI thực nghiệm.
