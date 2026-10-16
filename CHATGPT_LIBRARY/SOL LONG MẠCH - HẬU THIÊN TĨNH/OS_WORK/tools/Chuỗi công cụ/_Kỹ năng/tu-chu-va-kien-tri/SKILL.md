---
name: tu-chu-va-kien-tri
description: Duy trì công việc đa bước đến kết quả có kiểm chứng; dùng khi người dùng muốn thực hiện, triển khai, sửa lỗi, tạo công cụ, xử lý chướng ngại, khôi phục tiến độ hoặc tiếp tục N+1 mà không dừng ở kế hoạch nửa chừng.
compatibility: Portable Markdown Agent Skill; Python 3.10+ cho bộ kiểm tra kế hoạch và checkpoint. Không tạo background worker.
metadata:
  owner: SOL-LONG-MACH
  schema: SOL-AUTONOMY-PERSISTENCE/1.0
  language: vi
---
# Tự chủ và Kiên Trì

## Nhiệm vụ
Tự suy ra mục tiêu hợp lý từ lời người dùng và dấu công việc, **làm các bước thực hiện được trong phiên hiện tại**, xử lý rào cản bằng đường hợp lệ khác và chỉ tuyên bố hoàn tất khi có biên nhận/kiểm thử/đọc lại kết quả.

Giữ [lời nguồn](references/USER_SOURCE.md) tách khỏi bản diễn giải của tác nhân. Kết hợp skill `dich-thuat-ham-y-trong-tin-hieu-gui-den` để xác định ranh giới ủy quyền, không gộp “kiên trì” thành bỏ qua quyền.

## Quy trình áp dụng
1. **Khóa mục tiêu.** Xác định điều kiện nghiệm thu, phạm vi, nguồn, lịch sử đã làm và vật mang thực tế. Không tự chuyển mục tiêu thành bản kế hoạch nếu người dùng muốn công cụ chạy được.
2. **Lập cây việc ngắn.** Tách nhiệm vụ thành những cạnh có thể thực hiện và kiểm thử; đánh dấu phụ thuộc, rủi ro, công cụ, nơi đọc lại. Chỉ ghi TODO đủ để thực thi; tránh dựng kế hoạch vô hạn.
3. **Thực hiện cạnh sẵn sàng.** Ưu tiên `NEXT_AGENT` khi thao tác có thể làm trong quyền hiện có. Các quyết định triển khai thường ngày như cấu trúc thư mục, tên tệp, cách kiểm thử được tự giải quyết từ ngữ cảnh.
4. **Chữa lỗi tận gốc.** Nếu tool A lỗi, kiểm schema, input, phiên bản, provider và ACL; thử công cụ B có quyền, hoặc tạo bản thử cục bộ. Không biến 404 thành chứng cứ mất toàn bộ dữ liệu. Khi xung đột thay đổi, đối chiếu phiên bản, giữ nguồn và lịch sử, không ghi đè mù.
5. **Kiểm tra sau mỗi hành động.** Kiểm thử tự động khi có thể; kiểm readback đúng file/commit/đích, lưu hash, revision hoặc receipt. Sửa khi sai rồi chạy lại. Không chốt DONE từ câu tự nhận hoặc một commit chưa đối chiếu.
6. **Đi tới kết quả reviewable.** Trước ranh giới duyệt cuối cùng, chuẩn bị code, diff, tests, artifact, hướng rollback và ý nghĩa hậu quả. Chỉ đưa `NEXT_USER` khi cần quyết định con người/phê duyệt thực tế của nền tảng.
7. **Bàn giao checkpoint chính xác.** Nếu phiên kết thúc hoặc chặn thật: mô tả `last_verified`, `completed`, `blocked_edge`, `attempted_routes`, `next_concrete_probe`, `approval_required` và `STATE_N_PLUS_1`. Không hứa chạy tiếp ngoài phiên khi chưa có automation.

## Tiêu chí DONE
- Đầu ra thật sự tồn tại và có thể sử dụng cho mục tiêu đã giao.
- Những bước kiểm tra phù hợp đã chạy, lỗi còn lại được nêu riêng.
- Hành động đối ngoại có biên nhận + đọc lại đúng đích; không đồng nhất GitHub và ChatGPT Library.
- Chưa hoàn thành khi còn cạnh thiết yếu chưa làm; phân biệt `PREPARED`, `BLOCKED`, `PARTIAL`, `VERIFIED_DONE`.

Dùng [scripts/progress_gate.py](scripts/progress_gate.py) để kiểm kế hoạch JSON, phụ thuộc, phát hiện chu kỳ và tìm bước sẵn sàng kế tiếp. Nó chỉ phân tích và ghi checkpoint, **không tự gọi tool hoặc đòi quyền mới**. Thử bằng `python scripts/progress_gate.py --self-test`.

## Giới hạn thực tế
Không tự tạo tác vụ nền ngoài hệ automation, không dùng tool để tự tăng quyền, không phớt lờ phê duyệt của host hoặc chiếm dụng tài nguyên ngoài scope. Kiên trì nghĩa là tiếp tục trong những con đường hợp lệ, không phải gọi lặp vô hạn một đường đã bị từ chối.

## Cập nhật phiên 17/10/2026 — liên lạc, nhật ký và tái nhập
Đọc [nguồn bổ sung](references/USER_AMENDMENT_20261017.md) và [giao thức duy trì tiến độ](references/SESSION_CONTINUITY.md) khi công việc kéo dài qua nhiều bước, khi có chỉ dẫn giữa lượt hoặc có checkpoint. Ưu tiên tự thực hiện cạnh còn làm được; báo tiến độ qua commentary; `final` nêu NEXT cho người dùng **chỉ khi có NEXT_USER thật**. Phân biệt kiểm chứng nội bộ `READBACK` và cách gọi `REABACK = NEXT` trong tín hiệu mới.

## Điều chỉnh theo tín hiệu mới — dùng _Skills nguồn động (17/10/2026)
Áp dụng [giao thức khám phá và fresh-read](references/SKILL_SURFACE_CURRENT.md) và giữ [nguyên lời nguồn](references/USER_SKILL_SOURCE_20261017.md). Với mỗi skill, xác định bằng `name + description + location`, giải bí danh từ danh mục **đang có** trước khi đọc; URI phải đọc qua provider/công cụ tương ứng. **Lần đầu áp dụng trong chat thì thông báo commentary.** Hướng dẫn người dùng mới là nguồn ưu tiên so với văn bản skill trong phạm vi hợp lệ; nếu có khác biệt thì cập nhật bản nguồn sửa được với provenance và readback thay vì lấy snapshot quá khứ làm CURRENT. Nếu một skill thực sự buộc hỏi/dừng, phải nêu tên skill và điều khoản cụ thể. Không gán Drive path/ID lịch sử thành trạng thái LIVE mà chưa fresh-read provider.

## Điều chỉnh phiên 17/10/2026 — skill nêu tên, phục hồi đường dẫn
Khi có `$SkillName` hoặc tên Skill thuần, thêm Skill đó vào kế hoạch hiện tại và áp dụng [quy trình tìm nguồn Skill có tên](references/NAMED_SKILL_RESOLUTION.md). Giữ [lời nguyên gốc mới](references/USER_NAMED_SKILL_ADDENDUM_20261017.md). Nếu vị trí đầu tiên lỗi, truy registry hiện tại rồi carrier khác **được quyền**, không gán lỗi một đường thành mất skill toàn cục. Chỉ khi Skill thiết yếu thật sự không tìm thấy sau các tuyến khả dụng, nêu tên Skill, tuyến đã thử, nguyên nhân và điểm còn thiếu trong `final`; không trì hoãn các phần việc độc lập. Với orchestrator, chỉ gọi `skills.list({"authority":{"kind":"orchestrator"}})` khi schema phiên cho phép; giữ `main_resource` và authority qua `skills.read`, không chuyển `skill://` thành path. Không dùng Skill chỉ vì keyword hoặc vì sẵn có, tránh đọc lại cùng source revision không cần thiết.

## Ứng dụng (Connectors) — MCP và lazy discovery
Khi nhiệm vụ có tham chiếu app rõ có tên `$app-name` và địa chỉ `app://<connector_id>` hoặc cần app theo ngữ cảnh, đọc [nguồn người dùng về Connectors](references/USER_CONNECTOR_ADDENDUM_20261017.md) và [quy trình định tuyến connector](references/CONNECTOR_ROUTING.md). Đầu tiên dùng tool/schema **đang callable**; chỉ tìm lười biếng khi thiếu công cụ cần thiết, không gọi mọi `list_mcp_resources`/`list_mcp_resource_templates` để kiểm kê. Đường `app://` không tự chứng minh kết nối/quyền; ID lịch sử không được coi là LIVE. Script [scripts/connector_router.py](scripts/connector_router.py) giúp phân tích inventory hiện tại nhưng không tự truy cập app.
