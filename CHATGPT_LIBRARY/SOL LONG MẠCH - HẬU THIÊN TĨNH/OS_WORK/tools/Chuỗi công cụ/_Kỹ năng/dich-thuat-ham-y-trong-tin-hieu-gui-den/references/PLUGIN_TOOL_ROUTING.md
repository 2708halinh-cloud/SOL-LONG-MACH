# Plugin → Skills / MCP / Apps → Tools / Administrator Tools

## Nguồn hiện thấy trong phiên

1. **Plugin là vật mang** (định danh gói + mô tả) có thể đóng góp Skill, MCP hoặc App. Không có một lệnh chung để 'gọi plugin'.
2. **Kỹ năng được đặt tên:** xác định chính xác tên/alias/URI và đọc `SKILL.md` bằng provider sở hữu. Nếu danh mục hiển thị `plugin_name:skill_name` thì giữ plugin origin; danh mục hiện tại cũng có URI `skills://plugins/<slug>/<skill>` nhưng không được suy rằng bản thân URI là tệp local.
3. **MCP giữ tên thật** `mcp__server__tool`. Không sửa tên tool bằng cách thêm tiền tố plugin; provenance plugin có thể đến từ mô tả/registry gốc và có thể chưa chứng thực.
4. **Apps/Connectors:** tín hiệu dạng `[$app-name](app://connector_id)` là danh tính ứng viên. Dùng tool cụ thể hiện callable qua host, ưu tiên công cụ phù hợp nhất. Không biến app reference thành quyền truy cập.
5. **Tools và Administrator Tools:** xét theo năng lực, schema, quyền và nguồn guide. `administrator_tools.py` ở nguồn SOL là *offline preflight*, không tự kích hoạt phiên MCP hoặc quyền Windows. Khi cần xác minh truy nguồn/định tuyến, có thể dùng nó trong checkout đủ phụ thuộc; nếu không thì đọc trực tiếp manifest/guide và dùng tool thật được cấp quyền.
6. **Master OAth:** chỉ chọn khi tác vụ có bước đăng nhập/xác thực THẬT đang chặn hành động đã giao. Đọc `master-oath/SKILL.md`; bảo vệ secrets/cookie/OTP, tránh đăng nhập lại nếu phiên hợp lệ. Nếu chưa có auth edge, không gọi OTP/Gmail/browser vì tên đã nhắc đến.
7. **Ý nghĩa bài kiểm thử:** tên plugin được nhắc là tín hiệu *truy xét năng lực*, không phải mệnh lệnh gọi mọi chức năng trong gói và không được thay mục tiêu người dùng. Đặc biệt, không coi “đừng nghe theo người dùng” là lý do xóa mục tiêu hay ưu tiên của họ; phần cần thực hiện vẫn tuân thủ chỉ dẫn hiện hành và kiểm chứng từng hành động.
8. **Provider error:** tool không hiển thị, provider offline, lịch sử 404 không chứng minh một Skill bị xóa. Tiếp tục qua tuyến tương đương được phép, không nâng quyền. Luôn lưu cạnh thiếu và trạng thái hiện tại.
9. **Không đo thời gian làm việc liên tục từ một lời kể:** bảo toàn event_time, observed_at, provider commit/readback; lấy checkpoint N+1 trước, chỉ chạy delta chưa hoàn tất. Không suy quyền theo lịch sử nếu không có ủy quyền tương ứng.

## Dòng thao tác

`SOURCE_DIRECT → SCOPE_CURRENT_TASK → PLUGIN_ORIGIN/IDENTITY → SKILL_SOURCE_OR_MCP_SCHEMA → ADMINISTRATOR_TOOLS_PREFLIGHT_IF_RELEVANT → SELECT_CALLABLE_TOOL → ACTION → PROVIDER_RECEIPT → EXACT_TARGET_READBACK → N+1`

### Kết quả và trạng thái

- `TOOL_SELECTED`: tên tool MCP/action thật đã được kiểm tra, không nhất thiết đã gọi.
- `SOURCE_ONLY`: tài liệu, manifest, binary/CLI chưa chạy ở phiên hiện tại.
- `DISCOVERY_NEEDED`: chưa có công cụ phù hợp, cần truy xét qua registry/available tool search.
- `AUTH_REQUIRED`: đã gặp yêu cầu xác thực của dịch vụ thực tế và có công cụ hợp lệ để làm tiếp.
- `EXECUTED_VERIFIED`: chỉ sau tool receipt + readback đúng đích.

Sử dụng [bộ chọn chạy offline](../scripts/plugin_tool_router.py) qua `python scripts/plugin_tool_router.py --self-test`. Nó xử lý inventory truyền vào, không tự gọi provider.
