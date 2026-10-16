# @TOOLS — TÁC NHÂN — TAY

Cửa tra cứu thống nhất ở `OS_WORK/tools` dành cho tác nhân SOL.

- `@TÁC NHÂN`: nhận mục tiêu, truy nguồn, chọn hành động.
- `@TÁC NHÂN PLUS`: tiếp diễn nhiệm vụ dài, dùng checkpoint.
- `@TÁC NHÂN — TAY` hoặc `@Tools`: tìm công cụ theo công việc, không bắt em nhớ tên từng công cụ.

**Danh mục nhóm hiện có:** [TOOLS_GROUP_INDEX_20261016.json](./TOOLS_GROUP_INDEX_20261016.json) — con trỏ tới 451 kỹ năng/105 nhóm và 20 nhóm provider theo lần kiểm kê, không sao chép hay xóa nguồn.
**Mục lục hoạt động:** [TOOLS_ROUTER_CURRENT.json](./TOOLS_ROUTER_CURRENT.json) — 21 tay AGENTS_SKILL gốc, con trỏ skill và ưu tiên provider. 
**Nguồn cần nạp:** `CONFIG_SOL/TESSERACT_AGENT_BOOT_ROUTES_CURRENT.json` và `CURRENT_RUNTIME/TASK_RESUME_POINTER.json`.

Giữ các thư mục `_Plugins/_Skills/_Mcps/_Tool/_App/_Other_Tools` hiện có. Không nhân bản mã hoặc xóa nguồn. Trước mỗi thao tác thực tế, kiểm tra công cụ có kết nối và đúng quyền, rồi đọc lại kết quả.

**Lưu ý:** `@Tools` ở đây là tên định tuyến trong dự án GitHub. Bản ghi GitHub không tự đăng ký thêm một plugin @ mới trong giao diện ChatGPT.

## Azure DevOps MCP — đã nối vào TAY

- [TOOLSET.md gốc](./AZURE_DEVOPS_MCP_CORE/docs/TOOLSET.md) — 97 thao tác, 44 tool, 9 nhóm, bản gốc bất biến.
- [Chỉ mục 97 thao tác](./AZURE_DEVOPS_MCP_CORE/TOOLSET_INDEX.json) và [bộ tra cứu/kiểm nguồn](./AZURE_DEVOPS_MCP_CORE/route_toolset.py).
- [Áp dụng vào TESSERACT/PR #6 và phân tích điểm nghẽn](./AZURE_DEVOPS_MCP_CORE/SOL_PROJECT_APPLICATION_20261016.md).
- Router đầu mối: `TOOLS_ROUTER_CURRENT.json#capability_blueprints.azure_devops_mcp`.
- Khởi động kiểm nguồn: `runtime/tesseract_agent_boot.py` đọc `TOOLS_ROUTER_CURRENT.json`, `docs/TOOLSET.md`, `TOOLSET_INDEX.json` và `route_toolset.py`, trả hash/readback.
- Azure DevOps MCP server **chưa phải công cụ callable trong phiên này**. Không tự phát ra tên hàm Azure giả. Giữ bảng động tác của Azure làm kiến trúc chọn công cụ đã kết nối (đặc biệt @GitHub / GitHub Actions) cho việc phù hợp; khi có Azure connector thật phải xác minh organization/project/auth/params.
