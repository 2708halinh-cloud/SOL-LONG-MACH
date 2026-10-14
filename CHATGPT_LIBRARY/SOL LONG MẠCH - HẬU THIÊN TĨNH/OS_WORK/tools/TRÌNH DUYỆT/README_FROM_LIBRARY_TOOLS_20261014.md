# Tools / TRÌNH DUYỆT — source-bound sync

Nguồn chính: plugin cá nhân [Chorme-Dev-Toolkit v0.1.3](https://chatgpt.com/plugins/plugins_6acd7510b08481919e0eee7ea085c62e), current release `pluginrel_6ace61260eb88191880b609b87934a58`.

Đây là **gói đồng bộ cấu hình và skills (OVERLAY)**, không phải bản đầy đủ `scripts/http_bridge.py`, `scripts/crux_probe.mjs` và các bài kiểm thử của plugin chính. Để dùng đủ chức năng Chrome, cần plugin gốc và host browser đang chạy.

## Đã có
- 14 URL GitHub và cấu hình `ACCESS_GITHUB=TRUE; ACCESS_CHATGPT=FLASE` dưới dạng *routing preferences*, không phải quyền OAuth thực tế.
- Apify remote MCP `https://mcp.apify.com/`; OAuth phải được hoàn tất theo client. Smithery Apify được xác nhận có tools riêng nhưng không chứng minh Browser plugin đã OAuth.
- Chrome MCP local bridge `http://127.0.0.1:8765/mcp`; loopback không dùng được từ ChatGPT cloud khi host ở máy khác.
- 4 tệp Library HTML snapshot làm provenance, được nhận diện qua đường dẫn và SHA-256; giữ nguồn nguyên vẹn ở Library.
- Dropbox folder chính xác do người dùng cung cấp đã liệt kê trực tiếp (25 mục, không thay đổi gì).

## Cookie/session
Dùng profile Chrome đã đăng nhập trên máy người dùng khi browser client được cho phép; KHÔNG chép cookie thô, refresh token, bearer token, storage state hoặc mật khẩu vào plugin, Dropbox, Git, ZIP hay nhật ký. Dữ liệu snapshot HTML **không** tạo phiên đăng nhập. Hiện Desktop Commander remote quota = 0% nên chưa xác minh browser Windows.

## Quy trình
1. Xem `SOL_BROWSER_PROJECT.toml` (TOML hợp lệ).
2. Xem `CHORME_DEV_TOOLKIT_SYNC/mcp.json` và `.mcp.json` đã đồng bộ trong gói này.
3. Nếu đã có browser host, xác thực bằng trình duyệt đang đăng nhập; đọc URL, title, phiên hiện tại (không đọc cookie raw).
4. Khi sửa plugin thật, kiểm tra `get_plugin_files` để so sánh. Trong lần readback v0.1.3 plugin trên server, `mcp.json` có Apify nhưng `.mcp.json` **chưa** có Apify; gói export này đã chuẩn hóa cả hai. Không gọi cấu hình cloud là đã đồng bộ đến khi server readback khớp.

## Nguồn liên quan
- Library `/SOL LONG MẠCH - HẬU THIÊN TĨNH/` (4 tài liệu nguồn, metadata SHA-256 ở `references/SOURCE_LIBRARY_VIEWS_20261013.json`).
- Dropbox `/Linh Hà/OLD NGUỒN DỰ ÁN THU HOI NGUON SOL - CHATGPT`.
