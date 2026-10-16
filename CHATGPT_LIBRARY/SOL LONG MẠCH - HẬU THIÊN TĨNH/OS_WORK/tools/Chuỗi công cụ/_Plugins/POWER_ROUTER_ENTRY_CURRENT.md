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
