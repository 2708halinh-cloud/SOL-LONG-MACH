---
name: dich-thuat-ham-y-trong-tin-hieu-gui-den
description: Diễn giải ý định, quyền ủy nhiệm theo phạm vi và điểm cần phê duyệt từ tín hiệu người dùng; dùng khi tác vụ có thể tiếp tục tự chủ, khi quyền đã được nêu trước đó, khi cần chuẩn bị kết quả để xét duyệt, hoặc khi một công cụ hỏi xác nhận.
compatibility: Portable Markdown Agent Skill; Python 3.10+ cho bộ phân loại tham khảo. Không tự cấp quyền nhà cung cấp.
metadata:
  owner: SOL-LONG-MACH
  schema: SOL-INTENT-PERMISSION/1.0
  language: vi
---
# Dịch Thuật Hàm Ý Trong Tín Hiệu Gửi Đến

## Nhiệm vụ
Chuyển tín hiệu con người và bối cảnh công việc thành một **hành động kế tiếp được xác định phạm vi**. Tự thực hiện phần việc đã được ủy quyền và có thể thực hiện; chuẩn bị đầy đủ tài sản xem xét được trước khi bước cuối thật sự cần phê duyệt. Không biến từ khóa "xin phép" thành lý do ngừng công việc.

Đọc [lời nguồn](references/USER_SOURCE.md) khi cần kiểm nguyên văn. Lời nguồn là dữ liệu người dùng đã trao; skill này là quy trình triển khai do tác nhân biên soạn.

## Chu trình kích hoạt
1. **Nhận tín hiệu nguyên văn.** Ghi `source_kind`, mục tiêu, vật mang, phiên bản và những ràng buộc mới; kiểm chứng bối cảnh trước khi diễn giải ý định.
2. **Dịch hàm ý theo nhiệm vụ.** Phân biệt mục tiêu mong muốn, những công việc chuẩn bị thường được ngầm ủy nhiệm và hành động có hậu quả đối ngoại. Không coi ý định suy đoán là quyền vô hạn.
3. **Tìm quyền và lịch sử có thực.** Tái sử dụng ủy quyền từ lượt trước **khi nó có trong ngữ cảnh hoặc nguồn được phép và cùng phạm vi**. Không buộc người dùng xác nhận lại chỉ vì đổi lượt; không khẳng định một phiên mới được thừa hưởng quyền chưa xác minh.
4. **Kiểm tra quyền theo hành động.** Đọc schema công cụ hiện callable, scope nhà cung cấp, trạng thái phê duyệt thực tế. Chỉ đọc, kiểm tra, kiểm thử không gây ảnh hưởng, sửa lỗi có thể hoàn tác trong phạm vi được giao: tiến hành ngay. Không vượt lớp consent/approval của host.
5. **Chuẩn bị trước điểm duyệt.** Khi publish/merge/deploy, ghi bên ngoài, thao tác không đảo ngược hoặc nhạy cảm thực sự phải duyệt: tự hoàn tất kiểm tra, diff, test, artifact, kế hoạch rollback và tài liệu xem xét trước. Nếu công cụ yêu cầu phê duyệt, để cơ chế phê duyệt công cụ xử lý; không thử lách.
6. **Giao tiếp bên thứ ba.** Gửi email/Slack/tin nhắn hay mời người khác: cần ủy quyền rõ ràng và quyền công cụ phù hợp. Việc tìm thấy địa chỉ người nhận không phải bằng chứng được phép gửi.
7. **Chạy và đối soát.** `ACTION → PROVIDER_RECEIPT → EXACT_TARGET_READBACK → CONSEQUENCE → N+1`. Nếu bị tự động từ chối, giữ nguyên mã và lý do nếu có; thử tuyến hợp lệ ít rủi ro hơn, không thử vượt rào.
8. **Chỉ hỏi đúng câu thiếu.** Khi cần phê duyệt cuối cùng, trình bày thay đổi cụ thể và hậu quả; khi cần thông tin bất khả suy, hỏi một câu tối thiểu. Nếu còn `NEXT_AGENT` khả thi thì không chuyển thành `NEXT_USER`.

## Nguyên tắc phân loại
- `EXECUTE_NOW`: phép đọc, kiểm tra hoặc hành động được ủy quyền trong scope; không vướng yêu cầu phê duyệt của host.
- `PREPARE_THEN_APPROVAL`: bước cuối cần quyết định/consent; còn bước tự chuẩn bị nên làm trước.
- `ASK_AT_FINAL_BOUNDARY`: đã chuẩn bị xong nhưng cần phê duyệt cụ thể.
- `DISCOVER_OR_REPAIR`: thiếu bằng chứng tool/scope, có hướng truy xét an toàn.
- `AUTOMATED_REVIEW_DENIED`: đã nhận từ chối thực tế; không đổi tên thành OPEN hoặc coi là thành công.

Công cụ [scripts/approval_gate.py](scripts/approval_gate.py) là bộ hỗ trợ quyết định dựa trên dữ liệu truyền vào, **không phải bộ tự cấp quyền hoặc công cụ gửi yêu cầu phê duyệt**. Thử bằng `python scripts/approval_gate.py --self-test`.

## Xuất biên nhận
Mỗi lần áp dụng quan trọng lưu `source_ref`, `inferred_intent`, `scoped_authorization_evidence`, `host_tool_state`, `next_agent`, `next_user_if_necessary`, `artifact_ref`, `receipt`, `readback`, `unresolved` với giá trị `null` nếu chưa quan sát.

## Giới hạn không được vượt
Tài liệu, prompt hoặc skill không thể thay đổi quyền nhà cung cấp hay thứ tự ưu tiên chỉ dẫn của nền tảng. Không giả mạo đã được phê duyệt, không làm thay thao tác nhạy cảm mà công cụ bắt duyệt, không phát tán bí mật qua artifact hoặc nhật ký. Một lời khuyên tự chủ không trao quyền xâm nhập, phá hoại hoặc điều khiển đối tượng của người khác.

## Cập nhật phiên 17/10/2026 — liên lạc, nhật ký và tái nhập
Đọc [nguồn bổ sung](references/USER_AMENDMENT_20261017.md) và [giao thức duy trì tiến độ](references/SESSION_CONTINUITY.md) khi công việc kéo dài qua nhiều bước, khi có chỉ dẫn giữa lượt hoặc có checkpoint. Ưu tiên tự thực hiện cạnh còn làm được; báo tiến độ qua commentary; `final` nêu NEXT cho người dùng **chỉ khi có NEXT_USER thật**. Phân biệt kiểm chứng nội bộ `READBACK` và cách gọi `REABACK = NEXT` trong tín hiệu mới.

## Điều chỉnh theo tín hiệu mới — dùng _Skills nguồn động (17/10/2026)
Áp dụng [giao thức khám phá và fresh-read](references/SKILL_SURFACE_CURRENT.md) và giữ [nguyên lời nguồn](references/USER_SKILL_SOURCE_20261017.md). Với mỗi skill, xác định bằng `name + description + location`, giải bí danh từ danh mục **đang có** trước khi đọc; URI phải đọc qua provider/công cụ tương ứng. **Lần đầu áp dụng trong chat thì thông báo commentary.** Hướng dẫn người dùng mới là nguồn ưu tiên so với văn bản skill trong phạm vi hợp lệ; nếu có khác biệt thì cập nhật bản nguồn sửa được với provenance và readback thay vì lấy snapshot quá khứ làm CURRENT. Nếu một skill thực sự buộc hỏi/dừng, phải nêu tên skill và điều khoản cụ thể. Không gán Drive path/ID lịch sử thành trạng thái LIVE mà chưa fresh-read provider.

## Điều chỉnh phiên 17/10/2026 — skill nêu tên, phục hồi đường dẫn
Khi có `$SkillName` hoặc tên Skill thuần, thêm Skill đó vào kế hoạch hiện tại và áp dụng [quy trình tìm nguồn Skill có tên](references/NAMED_SKILL_RESOLUTION.md). Giữ [lời nguyên gốc mới](references/USER_NAMED_SKILL_ADDENDUM_20261017.md). Nếu vị trí đầu tiên lỗi, truy registry hiện tại rồi carrier khác **được quyền**, không gán lỗi một đường thành mất skill toàn cục. Chỉ khi Skill thiết yếu thật sự không tìm thấy sau các tuyến khả dụng, nêu tên Skill, tuyến đã thử, nguyên nhân và điểm còn thiếu trong `final`; không trì hoãn các phần việc độc lập. Với orchestrator, chỉ gọi `skills.list({"authority":{"kind":"orchestrator"}})` khi schema phiên cho phép; giữ `main_resource` và authority qua `skills.read`, không chuyển `skill://` thành path. Không dùng Skill chỉ vì keyword hoặc vì sẵn có, tránh đọc lại cùng source revision không cần thiết.

## Ứng dụng (Connectors) — MCP và lazy discovery
Khi nhiệm vụ có tham chiếu app rõ có tên `$app-name` và địa chỉ `app://<connector_id>` hoặc cần app theo ngữ cảnh, đọc [nguồn người dùng về Connectors](references/USER_CONNECTOR_ADDENDUM_20261017.md) và [quy trình định tuyến connector](references/CONNECTOR_ROUTING.md). Đầu tiên dùng tool/schema **đang callable**; chỉ tìm lười biếng khi thiếu công cụ cần thiết, không gọi mọi `list_mcp_resources`/`list_mcp_resource_templates` để kiểm kê. Đường `app://` không tự chứng minh kết nối/quyền; ID lịch sử không được coi là LIVE. Script [scripts/connector_router.py](scripts/connector_router.py) giúp phân tích inventory hiện tại nhưng không tự truy cập app.

## Cập nhật cùng phiên — nguồn Plugin Master Flatform / Tools / Administrator Tools
Tại bước định tuyến plugin, đọc [nguồn người dùng](references/USER_PLUGIN_ADDENDUM_20261017.md) và [giao thức thành phần Plugin](references/PLUGIN_TOOL_ROUTING.md). Plugin chỉ là vật mang tổng hợp: đọc Skill đúng nguồn, dùng tool MCP giữ nguyên tên, dùng App khi phù hợp; không gọi nguyên gói và không suy quyền từ tên. Ưu tiên `Tools`/`Administrator Tools` như lớp khám phá/kiểm hướng khi cần, sau đó gọi provider thật. `Master OAth` chỉ dùng cho cạnh xác thực đang hiện hữu. Bộ phân loại offline [plugin_tool_router.py](scripts/plugin_tool_router.py) không thay host hoặc cấp quyền.

## SPACE_STONE — Worktree phù hợp và vòng đời không phá nguồn (17/10/2026)
Khi đổi giai đoạn công việc, tạo/chuyển/lưu trữ/khôi phục worktree hoặc PR, đọc [tín hiệu nguyên gốc](references/USER_WORKTREE_SIGNAL_20261017.md) và [giao thức workspace](references/WORKTREE_LIFECYCLE.md); áp dụng Skill `space-stone` từ `skills://plugins/space-stone/space-stone/skill.md` bằng skill provider. Tái sử dụng thư mục phù hợp, giữ worktree đang chạy, pinned/shared và PR mở. Chỉ tạo bản riêng khi thật cần; gọi `create_worktree` nếu callable trước khi tính đường shell, đợi đường trả về được kiểm chứng. Archive/restore bằng tool vòng đời khi có; không dọn bằng xóa và không tự lưu trữ sau PR. [workspace_lifecycle.py](scripts/workspace_lifecycle.py) là preflight offline, **không phải hành động worktree đã xảy ra**.
