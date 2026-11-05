# CONNECTOR ROUTING — Ứng dụng / Plugins MCP

## Áp dụng khi nào
Khi thông điệp có `[$app-name](app://<connector_id>)` với ID thật, hoặc khi nhiệm vụ cần một ứng dụng có sẵn (GitHub, Drive, Dropbox, Gmail, Calendar, Google Cloud, v.v.). Một ứng dụng là một nhóm năng lực, không phải bằng chứng toàn bộ hành động đã được cấp quyền.

## Chọn tuyến theo nhu cầu, không theo danh sách cứng
1. **Tín hiệu rõ:** Trích tên hiển thị và literal connector ID từ cú pháp `[$name](app://id)`. Khi ID là `{{connector_id}}` thì coi đó là placeholder. Tên hiển thị khác ID. Duy trì provenance `user_text → app-ref → provider → tool`.
2. **Tín hiệu ngầm:** Kiểm mục tiêu và carrier thật. Chỉ chọn ứng dụng khi hoạt động của ứng dụng đó cần thiết hoặc cải thiện kết quả rõ rệt. Không gọi tất cả app chỉ vì chúng có trong inventory.
3. **Tìm callable hiện tại:** Dùng tool/skill vốn đã khai báo trong phiên; inspect schema cụ thể trước hành động. `mcp__<provider>__<tool>` là dạng tên quan sát được, không phải quy tắc bắt buộc cho mọi provider. Chỉ dùng `tool_search`/`tools_search` nếu phiên **thực sự** cung cấp nó. Trong phiên có `functions.exec`/`ALL_TOOLS`, tìm chính xác trong đó và dùng `mcp__smithery_ai__MPC__search_toolbox` nếu năng lực cần thiết chưa hiển thị và có kết nối phù hợp. `plugin_management.search_plugins` chỉ dùng khi thiếu ứng dụng/capability liên quan.
4. **Resource listing:** `list_mcp_resources` hoặc `list_mcp_resource_templates` chỉ gọi nếu ứng dụng đó đã kết nối, công cụ tương ứng có trong schema và nhiệm vụ cần tài nguyên mà chúng cung cấp. Không gọi chỉ để kiểm kê hoặc khi một công cụ chuyên dụng đã đủ.
5. **Ưu tiên đường ngắn:** Provider trực tiếp có đủ quyền + readback tốt hơn cầu nối tầng khác. Không chọn đường vòng để tránh phê duyệt. Xem xét loại kết quả của tool (file, PR, receipt, runtime) và cổng duyệt **trước** khi gọi.
6. **Giao thức thao tác:** `SOURCE_DIRECT → DISCOVER → PROVIDER_ID/TOOL_SCHEMA → AUTH/ACTION_SCOPE → ACTION → RECEIPT → EXACT_TARGET_READBACK → N+1`. Read-only/sửa lỗi có thể hoàn tác và đã thuộc nhiệm vụ: không hỏi lại. Gửi tin nhắn ngoài (email/Slack) chỉ sau cho phép rõ ràng; hành động nhạy cảm đi qua duyệt hệ thống.
7. **Khi thiếu:** `TOOL_NOT_EXPOSED` ≠ `APP_NOT_INSTALLED` ≠ `PERMISSION_DENIED`. Nếu thực sự thiếu connector, đề xuất kết nối nếu có plugin phù hợp hoặc thực hiện cạnh độc lập khác. Không biến ID Google Drive quá khứ thành provider hiện tại.

## Mức chứng cứ
- `LITERAL_APP_REF`: chỉ quan sát cú pháp trong nguồn người dùng.
- `PROVIDER_FAMILY_FOUND`: nhóm tên tool xuất hiện trong inventory của phiên; chưa xác minh ID app.
- `SCHEMA_VERIFIED`: schema công cụ đã đọc.
- `ACTION_RECEIPT_VERIFIED`: đã gọi và có biên nhận.
- `TARGET_READBACK_VERIFIED`: đã xác minh trực tiếp đúng đích.

Script [../scripts/connector_router.py](../scripts/connector_router.py) là bộ phân loại offline: không kết nối provider, không cấp quyền; được gọi bởi host nếu host nạp nó. Danh mục đầu vào phải là bản trích **hiện tại** của phiên, không phải inventory lịch sử.
