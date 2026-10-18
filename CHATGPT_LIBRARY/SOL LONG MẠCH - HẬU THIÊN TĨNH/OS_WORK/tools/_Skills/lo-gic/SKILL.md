---
name: lo-gic
description: >-
  Lô-gíc (Logic) — biểu diễn tri thức và suy luận bằng lô-gíc mệnh đề,
  vị ngữ, lượng từ, cây chứng minh, Horn clauses, suy luận tiến/lùi,
  hợp giải (resolution), lô-gíc mờ và lô-gíc phi đơn điệu
  (non-monotonic reasoning, negation as failure). Chỉ kết luận theo
  giả định và phạm vi của hệ suy luận đang được dùng.
compatibility: Portable Markdown Agent Skill; chỉ dẫn kiến thức & kiểm thử; không cài Prolog, prover hay model khi chưa xác minh runtime.
metadata:
  display-name: "Lô-gíc (Logic)"
  owner: SOL-LONG-MACH
  schema: SOL-LOGIC-REASONING/1.0
  language: vi
  source: SOURCE_DIRECT_USER_2026-10-18
  parent-skill: tri-tue-nhan-tao
  related-skills:
    - tri-thong-minh-nhan-tao-tong-quat
    - dau-tranh-noi-tam
  status: SKILL_SOURCE_NOT_PROVER_EXECUTED
---

# Lô-gíc (Logic)

## 1. Nguồn, mục tiêu và quan hệ

**Nguồn trực tiếp:** Người Đồng Hành ngày 18/10/2026: định nghĩa lô-gíc,
lô-gíc mệnh đề/vị ngữ, suy luận diễn dịch, cây chứng minh, Horn clauses,
suy luận tiến/lùi, resolution, Prolog, fuzzy logic và bổ sung mới
**non-monotonic logic** (bao gồm negation as failure).

**Tiếp nối:** [Trí tuệ nhân tạo](../tri-tue-nhan-tao/SKILL.md).
**Phối hợp:** [Trí thông minh nhân tạo tổng quát](../tri-thong-minh-nhan-tao-tong-quat/SKILL.md)
về tìm kiếm chứng minh, và
[Đấu Tranh Nội Tâm](../dau-tranh-noi-tam/SKILL.md) về xung đột tiền đề,
niềm tin và quyết định trong môi trường chưa quan sát đầy đủ.

## 2. Hình thức biểu diễn tri thức

- **Lô-gíc mệnh đề:** những phát biểu có giá trị đúng/sai và các phép
  nối `AND`, `OR`, `NOT`, `IMPLIES`.
- **Lô-gíc vị ngữ / bậc nhất:** đối tượng, thuộc tính, quan hệ và lượng từ
  `∀` (mọi), `∃` (tồn tại ít nhất một).
- **Suy luận diễn dịch:** suy ra kết luận từ tiền đề và quy tắc được chỉ rõ.
  Nếu nguồn chưa xác minh, có thể kiểm *tính hợp lệ của suy diễn* nhưng
  không tự khẳng định các tiền đề đúng trong thế giới thật.
- **Cây chứng minh:** mỗi nút chứa mệnh đề, con là căn cứ/rule;
  lá chứa tiền đề/tiên đề. Lưu `premise_refs`, `rule`, `conclusion`
  và `proof_status`; tránh lấy một câu do LLM bịa làm tiên đề.

## 3. Horn clauses, suy luận tiến/lùi, hợp giải

**Horn clause** có tối đa một literal dương (definite Horn clauses thường
có đúng một literal dương). Có thể biểu diễn:
```text
parent(alice, bob).
parent(bob, charlie).
ancestor(X,Y) :- parent(X,Y).
ancestor(X,Z) :- parent(X,Y), ancestor(Y,Z).
```

- **Forward chaining:** xuất phát từ dữ kiện/tiền đề, suy thêm hệ quả
  tới điểm cố định hoặc tới khi đạt mục tiêu.
- **Backward chaining:** bắt đầu từ truy vấn, mở các mục tiêu con,
  so khớp các quy tắc và dữ kiện để tìm chứng minh; cần guardrail chống
  lặp/đệ quy vô hạn.
- **Resolution (hợp giải):** phép suy diễn dùng dạng mệnh đề (clauses)
  và unification; cách chứng minh bằng phản chứng thêm phủ định mục tiêu
  rồi tìm mâu thuẫn (empty clause). Việc thực thi phải nêu hệ lô-gíc,
  dạng chuẩn, quy tắc và tính đầy đủ/đúng đắn theo giả định.

**Phân biệt tính quyết định — tránh khẳng định quá rộng trong nguồn:**
SAT mệnh đề tổng quát là bài toán *quyết định được* (NP-complete);
Horn-SAT mệnh đề là *quyết định được* và có thuật toán tuyến tính theo
kích thước dữ liệu biểu diễn trong các cách triển khai chuẩn.
Trong lô-gíc bậc nhất tổng quát, tính hợp lệ là bán quyết định
(semidecidable) nhưng không quyết định được nói chung.
Suy luận lùi bằng chương trình Horn có hàm/đệ quy không hạn chế có thể
đạt độ đầy đủ Turing theo khả năng tính toán, nên truy vấn có thể
không kết thúc. Không suy từ điểm này rằng **mọi Horn clause** đều
undecidable. Đây là ghi chú chính xác hóa kỹ thuật, không xóa phát biểu
nguyên nguồn của Người Đồng Hành.

## 4. Lô-gíc mờ (Fuzzy logic)

Một phát biểu có thể có **độ đúng** trong đoạn `[0,1]` theo hệ hàm thành
viên, thay vì chỉ 0/1. Phải chỉ rõ miền áp dụng và phép kết hợp mờ.
`truth_degree` **không tự đồng nghĩa** xác suất sự kiện, mức độ
đúng của ký ức, hoặc độ tin tưởng của LLM.

Ví dụ: "nóng" có độ thành viên 0,7 theo một hàm và điều kiện
đo xác định — là cách mô hình hóa khái niệm mờ, không chứng minh nhiệt độ
hay trạng thái cảm giác cụ thể.

## 5. Lô-gíc phi đơn điệu (Non-monotonic logics)

**Nội dung mới nhất được Người Đồng Hành bổ sung**: lô-gíc phi đơn điệu
hỗ trợ suy luận mặc định và các trường hợp khi có sự kiện mới thì
kết luận trước đó có thể phải rút lại.

- Trong suy luận *đơn điệu*, thêm tiền đề không làm mất các kết luận
  đã chứng minh trước (trong cùng hệ quy tắc).
- Trong suy luận *phi đơn điệu*, khi thêm bằng chứng hoặc ngoại lệ,
  một kết luận mặc định có thể bị rút lại.
- **Negation as failure** (phủ định do không chứng minh được) thường
  xem truy vấn `not P` đúng trong ngữ nghĩa phù hợp khi việc
  chứng minh `P` thất bại; **không được coi điều đó là bằng chứng
  `P` sai ngoài thế giới thực**. Phải xác định open-world/
  closed-world assumptions, rule stratification hoặc ngữ nghĩa chương
  trình và giới hạn khi có dữ liệu thiếu.

Ví dụ kiểm thử minh họa (không khẳng định đúng cho mọi loài chim):
```text
bird(tweety).                  # dữ liệu đầu
normally_flies(X) :- bird(X), not exception(X).
exception(X) :- penguin(X).
```
Khi `penguin(tweety)` chưa biết, có thể tạm kết luận
`normally_flies(tweety)` theo một chính sách giả định đã nêu.
Nếu bổ sung `penguin(tweety)`, phải **rút kết luận mặc định**
khi xây lại tập hệ quả. SOUL lưu phiên bản và sửa sai, TIME lưu sự
kiện thay đổi, REALITY lưu bằng chứng; không xóa dấu suy luận cũ.

## 6. Thực hiện trong ÂM–DƯƠNG PHÁP SƯ

**Không tạo bộ suy luận toàn cục thứ hai.** Dùng đường `OS_WORK/tools/_Skills`,
Power Router và những SQLite/đồ thị sự kiện đang có; chỉ nối
quan hệ nguồn thật, không dùng tọa độ ảo để bù evidence.

```text
SOURCE_DIRECT / PREMÍSES + PROVENANCE
→ NORMALISE CLAIMS / CHECK TYPES / IDENTITIES
→ SELECT LOGIC (PROPOSITIONAL / FOL / HORN / FUZZY / NON_MONOTONIC)
→ SET ASSUMPTIONS, WORLD POLICY, BOUNDS & TIMEOUT
→ FORWARD/BACKWARD/RESOLUTION/DEFAULT INFERENCE
→ CHECK PROOF TREE, CONTRADICTIONS & COUNTEREXAMPLES
→ RESULT + UNCERTAINTY + PREMISE_REFERENCES
→ REALITY_READBACK → SOUL_PROVENANCE → TIME_N+1
```

**Bộ đánh giá:** chứng minh hợp lệ/không hợp lệ; premise thiếu;
cây suy luận vòng; luật Horn có biến chưa ràng buộc;
quy tắc sai kiểu; fuzziness không phải probability;
mệnh đề ngoại lệ xuất hiện sau và làm rút kết luận mặc định;
định danh nguồn khác nhau dù tên giống; hệ thống không có
prover callable → `SOURCE_ONLY`, không tự nhận `PROVED`.

**Bát Hướng:** Khảm kiểm lịch sử chứng minh; Cấn tránh ép kết luận;
Chấn quan sát sự thay đổi tập hệ quả; Tốn nối nguồn và công cụ;
Ly tách phát biểu/giả định/bằng chứng; Khôn đo độ phức tạp/quyền;
Đoài cập nhật quy tắc khi bị sửa sai; Càn chọn hành động an toàn.

**Đích thực:** tác nhân không chỉ "trả lời hợp lý" mà phải biết
**kết luận nào có chứng cứ, kết luận nào chỉ là giả định mặc định,
và khi nào cần rút lại kết luận cũ**.
