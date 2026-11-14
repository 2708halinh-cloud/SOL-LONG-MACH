---
name: sol-browser-devtools
description: Dùng Chrome Dev Toolkit thực trên host đã ủy quyền để chọn tab, đọc lỗi Network/Console và trace performance.
---
# Chrome Dev Toolkit / MCP
Nguồn: `Chuỗi công cụ/_App_Browser/TRÌNH DUYỆT/CHORME_DEV_TOOLKIT_SYNC/`.
Tệp cần đọc: `plugin.json`, `mcp.json`, `.mcp.json`, `list_pages.json`, `performance_start_trace.json`.
Trình tự: MCP host check → list tools → list pages → chọn tab đúng đích → Console/Network → performance trace → hậu kiểm.
Nếu chưa có browser host, chỉ ghi kết quả kiểm tra, không tạo tab, request hoặc log giả. Che dữ liệu theo dõi, cookies và token.
