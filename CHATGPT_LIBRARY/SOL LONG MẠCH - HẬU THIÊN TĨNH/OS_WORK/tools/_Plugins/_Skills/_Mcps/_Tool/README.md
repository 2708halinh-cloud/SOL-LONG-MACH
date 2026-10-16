# _Tool — POWER ROUTER / SOL

**Chức năng:** Cửa chọn công cụ theo mục tiêu.

**Nguồn code/tài liệu gốc (tương đối từ OS_WORK/tools, không phải bản sao chuyển thư mục):**
- `SANDBOX/route_tools.py`
- `TOOLS_ROUTER_CURRENT.json`

**Bước thực hành:** Cần lookup callable chính xác trước action; tool name trong manifest không tự trở thành quyền dùng.

**Điểm về:** `_Plugins/_Skills/_Mcps/_Tool/_App/_Other_Tools/RETURN_TO_PLUGINS.json` → `_Plugins`.

Chỉ mục này không cài mới kỹ năng, MCP hoặc plugin. Không suy trạng thái thiết bị đang hoạt động từ đường dẫn; không di chuyển/xóa nguồn để làm đẹp cấu trúc. Đọc `_Plugins/POWER_ROUTER_CURRENT.json` và thực thi `_Plugins/power_router.py` trên checkout để biết portal và bước truy kế tiếp. Mọi hành động thật cần provider receipt + readback riêng.
