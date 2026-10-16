# SOL OS_WORK/tools — POWER ROUTER V2 ENTRY

**SOURCE:** `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/`
**CANONICAL ENTRY:** `_Plugins/`
**Capability registry:** `_Plugins/POWER_CAPABILITY_ROUTES_V2.json`
**Runnable local source:** `_Plugins/power_capability_router.py`
**Working contract:** `_Plugins/POWER_ROUTER_EXECUTION.md`
**Reusable skill source:** `_Plugins/_Skills/power-capability-router/SKILL.md`

## Vòng quay về PLUGINS

`_Plugins → _Skills → _Mcps → _Tool → _App → _Other_Tools → _Plugins`.

Đây là vòng quan hệ kết thúc mỗi lượt bằng biên nhận hoặc cạnh tiếp theo, **không** phải lặp vô hạn không điều kiện. DƯƠNG PHÁP SƯ xác lập đích và nguồn; ÂM PHÁP SƯ tìm công cụ, phân định provider/ID/permission, thực hiện trong phạm vi khả dụng, readback rồi quay về Plugins. Giữ 8 Đại nguyện ở lớp quyết định hành động; không lấy tên skill hoặc dấu OPEN làm kết quả.

Các họ: The Master Flatform Agent Skills; GGDV Template Creator; X-TiMe Multi-Agent; Generative AI; Azure DevOps; Call_Tools; Smithery MPC; Bright Data; GitHub; Tomorrow.io Weather; Dropbox/Drive/Library/local sync. Những nơi chỉ có blueprint chưa phải kết nối live. Nếu Azure DevOps không callable, truy nguồn/tool schema hoặc thử GitHub adapter đúng phạm vi, không bịa lệnh Azure.

**PORTABLE READBACK:** `power_capability_router.py` + JSON registry có thể định tuyến tại một checkout tối giản. Khi thiếu bộ source router cũ và RETURN_TO_PLUGINS.json, trường `back_edge_observed_in_checkout` là `false`. Giá trị `return_to: _Plugins` là đường logic, không phải kết quả thực thi từ provider.

**SOURCE BOUNDARY:** GitHub và ChatGPT Library là hai carrier độc lập. Giữ `.env` thật ngoài kho công khai; chỉ dùng tên biến và bí mật do môi trường quản lý. `Call_Tools` được phép tìm provider khác, không được vượt quyền truy cập hoặc sự cho phép cần thiết. Một lượt `OPEN` phải kèm hành động truy cụ thể tiếp theo.

## MCP Registry HTTP / Ed25519 — tuyến mới

- Route ID: `mcp-registry-http-ed25519`; danh mục: `MCP_REGISTRY_HTTP_ROUTE.json`; lớp MCP: `../_MCPs/MCP_Registry_HTTP/`.
- Nhận yêu cầu quản trị tên miền MCP Registry → nhận diện provider/thiết bị/miền/web root → kiểm tra quyền quản trị và khả năng chạy bash/openssl/mcp-publisher → `prepare` chỉ khi được yêu cầu → triển khai chứng thực public với provider có quyền → HTTPS readback → `login` riêng khi có yêu cầu → ghi receipt → quay lại `_Plugins`.
- Không tự gọi `prepare` hoặc `login` chỉ vì có chỉ mục. Không ghi private key hay token vào bất kỳ tệp đồng bộ nào. Mã nguồn được nhận từ file đính kèm, không phải bằng chứng dịch vụ đã thực chạy.

## ROUTER V2 — ĐƯỜNG CHẠY PHÙ HỢP CẤU TRÚC HIỆN TẠI (2026-10-16)

Lưu riêng `Chuỗi công cụ/_Plugins/Power_Router_V2/{power_capability_router.py,POWER_CAPABILITY_ROUTES_V2.json}` tại cả GitHub và ChatGPT Library. Bản mã nạp registry theo chính cây `Chuỗi công cụ`, phát hiện repo root từ vị trí source và trả ra lựa chọn `mcp-registry-http-ed25519`. Các trỏ `_Plugins/power_capability_router.py` trong tài liệu lịch sử giữ làm tham chiếu STAMP_OLD, **không còn là vị trí file thực thi trong cây hiện hành**.

Lệnh tại thư mục gốc checkout: `python "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Plugins/Power_Router_V2/power_capability_router.py" --task "MCP Registry HTTP Ed25519 xác thực tên miền"`. Kết quả ROUTE là phân loại ý định, **không** tự tạo private key, public HTTPS proof, DNS record hay phiên đăng nhập. Khi cần tác động provider phải gọi riêng công cụ đúng quyền và thực hiện exact-target readback.
