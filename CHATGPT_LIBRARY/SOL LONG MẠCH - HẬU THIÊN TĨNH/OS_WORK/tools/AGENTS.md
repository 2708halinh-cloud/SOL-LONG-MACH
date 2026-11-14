# AGENTS.md — SOL Toolchain

Áp dụng R-000: phân biệt danh mục khai báo với quyền thực thi. SOURCE → AUTH → ACTION → RECEIPT → READBACK → N+1.

1. Bề mặt `tools/` chỉ giữ `Chuỗi công cụ/`, `AGENTS.md`, `POWER_ROUTER.md`, `README.md` (Git còn các tệp di sản cho tới khi được di chuyển xong).
2. Trong `Chuỗi công cụ/`: _Plugins, _Kỹ năng, _MCPs, _Dụng cụ, _Ứng dụng, _App_Browser, _Bảo_mật, _Di_sản, _Sổ_đăng_ký.
3. Mọi thông tin plugin/skill/MCP chỉ là con trỏ tài liệu; không tự cài hoặc cấp quyền. Quét và xác minh trạng thái từng phiên.
4. Tách SOURCE_PRESENT, CONNECTED, CALLABLE, ACTIVE, RECEIPT_VERIFIED, BLOCKED, UNAVAILABLE_THIS_SESSION.
5. GitHub public: không commit khóa API, proxy credentials, cookies, client secrets, .env hoặc bearer tokens. Tệp bí mật nguồn không tái xuất bản. Không tự chuyển secrets từ Library.
6. Không xóa hiện vật gốc khi chưa có readback nội dung và số lượng ở cả hai mặt. Giữ lịch sử Git; khi chưa an toàn, đánh dấu OPEN.
7. Power Router chọn tuyến nhỏ nhất phù hợp; quay lại _Plugins sau mỗi nhiệm vụ; không phát minh tên công cụ hoặc tuyên bố Cloud Browser đang active.
