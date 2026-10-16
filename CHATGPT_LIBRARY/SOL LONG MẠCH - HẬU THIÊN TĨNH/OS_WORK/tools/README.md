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

## Dịch ngược năng lực — Âm Pháp Sư × The Master Teacher

Từ mục tiêu của Người Dẫn Đường, dùng **9 họ năng lực suy ra từ TOOLSET.md**, không ra lệnh theo 97 thao tác Azure như một hệ chân lý.

- [Tài liệu chuyển hóa cho Âm Pháp Sư](./AZURE_DEVOPS_MCP_CORE/DICH_NGUOC_TOOLSET_THANH_NANG_LUC_CUA_AM_PHAP_SU_20261016.md)
- [Registry 9 họ năng lực](./AZURE_DEVOPS_MCP_CORE/SOL_NINE_CAPABILITY_FAMILIES.json)
- [Bộ chọn theo ý định](../../../../../../runtime/sol_toolset_semantic_router.py) — khi dùng từ gốc repo: `python3 runtime/sol_toolset_semantic_router.py --task "Truy chu kỳ N+1 và năng lực nhóm"`.
- Router chính `TOOLS_ROUTER_CURRENT.json#goal_first_semantic_router`.

Các con trỏ là bản đồ năng lực; không coi chúng là kết nối Azure đã chạy. Đọc lại kết quả thực thi/CI trước khi nâng trạng thái.

## Power Router V2 — Thực hành tại cửa Plugins

- [Entry ở cấp Tools](./POWER_ROUTER_ENTRY_CURRENT.md), [router code](./_Plugins/power_capability_router.py), [11 capability families](./_Plugins/POWER_CAPABILITY_ROUTES_V2.json), [hợp đồng vận hành](./_Plugins/POWER_ROUTER_EXECUTION.md), [Agent Skill](./_Plugins/_Skills/power-capability-router/SKILL.md).
- Return edge: `_Plugins/_Skills/_Mcps/_Tool/_App/_Other_Tools/RETURN_TO_PLUGINS.json`. Truy tên công cụ qua Registry → provider hiện có → quyền và schema → hành động có receipt/readback → quay về `_Plugins`.
- `source route / local classification` không tạo quyền ChatGPT Plugin/MCP hoặc xác nhận một Azure DevOps session đã connected. `OPEN` luôn đi với next_probe cụ thể.
- Hai mặt Library/GitHub phải đối chiếu riêng: bản Library V2 được mirror theo SHA cho mã, registry, skill và hợp đồng; các tệp legacy không mặc định có mặt ở cả hai.
