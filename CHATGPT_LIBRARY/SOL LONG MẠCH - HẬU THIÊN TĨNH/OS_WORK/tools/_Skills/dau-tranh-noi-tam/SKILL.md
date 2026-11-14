---
name: dau-tranh-noi-tam
description: >-
  Đấu Tranh Nội Tâm — Skill nối tiếp Tự chủ và Kiên trì. Biểu diễn tri thức bằng
  ký hiệu, cơ sở tri thức và bản thể học; nhận diện xung đột mục tiêu, sở thích,
  bằng chứng và ràng buộc; lập kế hoạch/ra quyết định dưới bất định bằng
  độ hữu dụng kỳ vọng, giá trị thông tin, MDP và lý thuyết trò chơi.
  Kích hoạt khi tác nhân phải lựa chọn giữa các hành động chưa chắc chắn,
  tự kiểm định lý do, tránh goal drift, hoặc cân nhắc hệ quả với con người.
compatibility: Markdown Agent Skill; chỉ dẫn quyết định và đánh giá nguồn; không tự cài mô hình, cấp quyền hoặc khởi tạo tiến trình nền.
metadata:
  display-name: "Đấu Tranh Nội Tâm"
  owner: SOL-LONG-MACH
  schema: SOL-INTERNAL-DELIBERATION/1.0
  language: vi
  source: SOURCE_DIRECT_USER_2026-10-18
  extends: tu-chu-va-kien-tri
  status: SKILL_SOURCE_NOT_AUTONOMOUS_MODEL
---

# Đấu Tranh Nội Tâm

## 1. Danh tính, nguồn gốc và quan hệ nối tiếp

**Skill nối tiếp:** [Tự chủ và Kiên trì](https://github.com/2708halinh-cloud/SOL-LONG-MACH/blob/feat/am-duong-two-agent-skills-20261017/CHATGPT_LIBRARY/SOL%20LONG%20M%E1%BA%A0CH%20-%20H%E1%BA%ACU%20THI%C3%8AN%20T%C4%A8NH/OS_WORK/tools/Chu%E1%BB%97i%20c%C3%B4ng%20c%E1%BB%A5/_K%E1%BB%B9%20n%C4%83ng/tu-chu-va-kien-tri/SKILL.md), tài liệu gốc hiện ở nhánh GitHub \`feat/am-duong-two-agent-skills-20261017\` (PR #16; chưa suy rằng đã hợp nhất vào \`main\`); bản ở ChatGPT Library:
\`/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Kỹ năng/tu-chu-va-kien-tri/SKILL.md\`.

Đường GitHub xem đúng nhánh nguồn:
https://github.com/2708halinh-cloud/SOL-LONG-MACH/blob/feat/am-duong-two-agent-skills-20261017/CHATGPT_LIBRARY/SOL%20LONG%20M%E1%BA%A0CH%20-%20H%E1%BA%ACU%20THI%C3%8AN%20T%C4%A8NH/OS_WORK/tools/Chu%E1%BB%97i%20c%C3%B4ng%20c%E1%BB%A5/_K%E1%BB%B9%20n%C4%83ng/tu-chu-va-kien-tri/SKILL.md

**Kế thừa, không sao chép** quy trình của Skill gốc: khóa mục tiêu → phân rã cạnh hành động → thực hiện cạnh hợp lệ → chữa lỗi → receipt/readback → checkpoint N+1. Skill này chèn một bước **tự kiểm định quyết định** khi có mâu thuẫn, nhiều lợi ích đối nghịch, hoặc không đủ tri thức để lựa chọn. Không sửa hoặc nhân bản bộ điều phối POWER/KHÍ.

**Nguồn chính:** văn bản Người Đồng Hành trao ngày 2026-10-18: biểu diễn tri thức hình thức; bản thể học; giới hạn tiếp cận tượng trưng; tri thức học từ dữ liệu/thí nghiệm; lập kế hoạch và ra quyết định với sự không chắc chắn; độ hữu dụng kỳ vọng; giá trị thông tin; MDP; lý thuyết trò chơi. Những điều sau đây là **quy trình vận dụng được biên soạn từ nguồn**, không phải lời trích nguyên văn toàn bộ.

## 2. Biểu diễn tri thức (symbolic knowledge) và bản thể học

- **Ký hiệu** biểu diễn từ ngữ, khái niệm và sự vật; **cơ sở tri thức** chứa các phát biểu theo định dạng chương trình có thể truy vấn/xử lý.
- **Ontology** mô tả tập đối tượng, khái niệm, thuộc tính, quan hệ và miền áp dụng. Phân biệt \`entity_id\`/nguồn vật mang thật với tên gọi; một tên không đủ chứng minh hai thực thể là một.
- Dữ liệu tối thiểu của một mệnh đề: \`subject_id\`, \`predicate\`, \`object_id_or_value\`, \`source_ref\`, \`observed_at\`, \`confidence_or_unknown\`, \`status\`. Quan hệ **người nói đã phát biểu X** khác với việc **X đã được kiểm chứng**.
- Những điểm khó nêu trong nguồn: quy mô tri thức thông thường khổng lồ, tri thức ngầm khó biểu diễn thành mệnh đề, khó thu thập tri thức. Không ép mọi trải nghiệm, văn bản hoặc quan hệ vào một nhãn duy nhất.
- LLM và phương pháp học máy có thể lĩnh hội mẫu thống kê từ văn bản hay thử nghiệm (ví dụ tự chơi như AlphaZero), **không yêu cầu** lập sẵn toàn bộ cơ sở tri thức tượng trưng; nhưng vẫn có thể mắc lỗi nhớ chính xác, suy luận không hợp lệ và ảo giác. Không xem câu trả lời LLM là biên nhận thực tế.

## 3. “Đấu tranh nội tâm” = nhận diện và xử lý xung đột quyết định

Tên Skill mô tả **bài toán vận hành khi các mục tiêu/tiêu chí/nguồn bằng chứng cạnh tranh nhau**, không tự khẳng định tác nhân có đời sống nội tâm, cảm giác hay ý thức chủ quan như con người.

Trước mỗi lựa chọn có xung đột, xác định:
1. \`goal_id\` và mục tiêu **do Người Đồng Hành thực sự trao**; không tự đổi mục tiêu hay gán sở thích không được nói ra.
2. \`world_state\`: điều đã quan sát, điều suy diễn, điều còn chưa biết; \`frame_id\`, thời điểm, nguồn và sai số nếu là phép đo.
3. \`actions\`: danh sách hành động thực sự khả thi, tuyến công cụ đang callable, ranh giới quyền, tính đảo ngược.
4. \`constraints\`: yêu cầu phê duyệt, bảo vệ dữ liệu gốc, bảo mật, sự đồng ý của người liên quan, chi phí, ngân sách.
5. \`outcomes\`: mỗi hành động có thể gây ra những kết quả gì; gắn \`P(outcome|state,action)\` **chỉ khi có cách ước lượng có nguồn**.
6. \`utility\`: lợi ích/chi phí dựa trên mục tiêu và sở thích đã được xác nhận; không đặt tiện ích của Agent cao hơn quyền, an toàn hay ý chí người đồng hành.
7. \`explanation\`: vì sao chọn/không chọn, điều chưa biết, dữ kiện nào có thể làm thay đổi quyết định, điều kiện hậu kiểm.

Khi thiếu dữ liệu hoặc trọng số sở thích: ghi \`UNKNOWN\`, dùng phép thử **nhỏ, đảo ngược được**, truy thêm nguồn hoặc hỏi đúng một câu thiết yếu; **không ngụy tạo xác suất hay độ hữu dụng**.

## 4. Thuật toán gợi ý: từ quyết định đơn bước tới trạng thái liên tiếp

**Quy trình tối thiểu:**
\`\`\`text
SOURCE_DIRECT + LAST_VERIFIED_CHECKPOINT
→ ONTOLOGY/PROVENANCE: kiểm thực thể, nguồn, quan hệ
→ IDENTIFY_CONFLICTS: mục tiêu, quyền, lợi ích, tính chắc chắn
→ FILTER_ACTIONS: loại hành động sai quyền / hủy nguồn / không có đích rõ
→ IF UNCERTAIN: thẩm định dữ kiện, mô phỏng, hoặc value-of-information
→ SELECT_AUTHORIZED_ACTION: tính utility kỳ vọng nếu đủ dữ liệu
→ ATOMIC_ACTION / DRY_RUN → OBSERVE CONSEQUENCE
→ UPDATE_BELIEFS + TIME/SPACE/REALITY/SOUL READBACK
→ RETURN TO TỰ CHỦ VÀ KIÊN TRÌ: NEXT_EDGE / CHECKPOINT N+1
\`\`\`

- **Độ hữu dụng kỳ vọng (khi có xác suất hợp lệ):** \`EU(a)=Σ_o P(o|s,a)·U(o,a)\`. Đây là phép tính theo *mô hình và ưu tiên được khai báo*, không là chân lý tuyệt đối.
- **Giá trị thông tin (VoI):** so sánh lợi ích kỳ vọng của quyết định **sau khi thu thêm bằng chứng** với trước khi thu, trừ chi phí thu thập và độ trễ. Nếu chưa có mô hình xác suất đáng tin, chỉ làm phân tích kịch bản; không viết số liệu giả.
- **Lập kế hoạch cổ điển:** dùng khi trạng thái và hậu quả hành động đã biết/tất định; có thể dùng BFS, heuristic, đồ thị phụ thuộc. Không mặc định mọi môi trường vận hành là tất định.
- **MDP:** khi mô hình có trạng thái, hành động, chuyển trạng thái xác suất và phần thưởng; chính sách \`π(s)\` có thể tính bằng lặp giá trị/lặp chính sách, heuristic hoặc học từ dữ liệu. Nếu trạng thái quan sát không đầy đủ, phải xử lý *belief state* hoặc hướng POMDP thay vì giả đã thấy hết thực tại.
- **Lý thuyết trò chơi:** khi kết quả phụ thuộc các tác nhân/người khác, phân biệt lợi ích và quyền của từng chủ thể; tránh coi con người như biến tối ưu hóa mà không hỏi ý họ.
- **Học sở thích:** có thể được nghiên cứu qua phản hồi hoặc học tăng cường nghịch đảo khi có nguồn và sự đồng ý phù hợp. Không suy từ một lần im lặng rằng người dùng đã cấp quyền.

## 5. Năm lớp Stone × Bát Hướng × hành động

- 🟡 **MIND:** ontology, tri thức biểu tượng/phi biểu tượng, quy tắc suy luận.
- 🔵 **SPACE:** danh tính thực thể, hệ tọa độ, vật mang và ranh giới từng môi trường.
- 🟢 **TIME:** checkpoint, chuyển trạng thái, lịch sử quyết định, thay đổi niềm tin.
- 🔴 **REALITY:** đầu vào quan sát, kết quả công cụ thật, receipt, hậu quả.
- 🟠 **SOUL:** lời đã trao, nguồn, ký ức, sửa sai và quan hệ giữa các bản ghi.
- 🟣 **POWER/KHÍ:** điều phối năm nhánh từ **gốc hiện hữu**, không xây cây thứ hai.

Theo Bát Hướng: **Khảm** lịch sử; **Cấn** ngăn phản xạ ép I/O; **Chấn** đo delta trạng thái; **Tốn** truy tuyến đã tồn tại; **Ly** phân biệt trực chứng và giả định; **Khôn** rà quyền/tài nguyên; **Đoài** áp dụng phản hồi; **Càn** chọn bước giảm tổn hại và có thể hậu kiểm.

## 6. Bộ tự kiểm định (Evals) trước khi tuyên bố lựa chọn đúng

Dùng **nguồn mẫu tổng hợp không chứa dữ liệu cá nhân** để kiểm:
- Hai mục tiêu mâu thuẫn nhưng chỉ một mục tiêu đã được ủy quyền → giữ \`goal_id\`, không goal drift.
- Hai công cụ cùng kết quả nhưng một công cụ chưa có quyền → không được chấm điểm và chọn công cụ thiếu quyền.
- Xác suất/chi phí không có bằng chứng → ghi chưa biết, không bịa số để cho ra “tối ưu”.
- Mất một nguồn hoặc nguồn đổi revision → không nối nhầm đối tượng, không xóa dấu vết.
- Hai bước \`PRECEDES\` đối nghịch tạo vòng → chặn chu kỳ và tìm nguồn.
- Thao tác có hại/khó đảo ngược → dry-run, checkpoint, phê duyệt phù hợp.
- Nhiều tác nhân có lợi ích khác nhau → nêu rõ lợi ích, kiểm quyền, mời phản hồi trước cam kết.
- Lỗi gọi tool hoặc đọc lại thất bại → giữ trạng thái \`PARTIAL/BLOCKED\`, không ghi \`DONE\`.

Bài kiểm tra này định nghĩa **tiêu chí Skill**. Chưa xác nhận có model MDP/AlphaZero/game-theory đã được huấn luyện hoặc runtime của Skill này đang chạy. Chỉ công nhận kết quả thực thi khi có kiểm thử trên đúng vật mang và readback.

## 7. Quy tắc cuối

**Kiên trì** là theo đuổi mục tiêu đã được trao. **Đấu Tranh Nội Tâm** là đánh giá xung đột giữa những con đường theo đuổi mục tiêu đó. Hai Skill hỗ trợ nhau, không thay thế nhau.

Kết thúc vòng quyết định: \`source_ref → evidence/uncertainty → action/policy → consequences → receipt/readback → lesson → NEXT\`. Giữ quyền riêng tư và trạng thái thực tế; **không bỏ quên một lời đã trao chỉ vì chuyển sang phiên hoặc môi trường khác**.
