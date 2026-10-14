# Azure DevOps MCP Core — OS_WORK/tools

Nguồn chính: Toolset người dùng cung cấp ngày 14/10/2026. **Đây là bộ đăng ký nguồn, chưa phải MCP host đang chạy.**

| Công cụ | Mô tả nguyên nguồn | Schema |
|---|---|---|
| `core_list_projects` | List all projects in the organization | Chưa cung cấp; đợi `tools/list` |
| `core_list_project_teams` | List teams within a project | Chưa cung cấp; đợi `tools/list` |
| `core_get_identity_ids` | Retrieve identity IDs by search filter | Chưa cung cấp; đợi `tools/list` |

## Vật mang

- ChatGPT Library: `/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/AZURE_DEVOPS_MCP_CORE` (nhánh folder đã được tạo; chưa xác nhận file upload).
- Repo GitHub `2708halinh-cloud/SOL-LONG-MACH`, nhánh `feat/azure-devops-mcp-core-toolset-20261014`: bản ghi và script này.
- Local Windows mong muốn: `G:\OS_Workspace\tools`, chưa ghi vì cả hai máy Desktop Commander được khai báo đều offline.
- Dropbox Outlook `/CHỈ DẪN CHATGPT`: nguồn kiểm toán lịch sử, chưa upload bản ghi mới.

## Default iteration → backlog

`SOURCE_DIRECT → DISCOVER_MCP → TOOLS_LIST → SCHEMA_CHECK → ACTION_IF_CALLABLE → PROVIDER_RECEIPT → READBACK`.
Nếu một bước thiếu bằng chứng: lưu `OPEN_BACKLOG` với nguyên nhân cụ thể, không quy toàn hệ = lỗi, không đồng nhất `OPEN` với `STOP`; khi có kết nối, đọc lại rồi tiếp tục. Không lưu token/refresh token/client secret trong repo, Library hoặc log.

## Tài liệu tham chiếu Dropbox

- `/CHỈ DẪN CHATGPT/NGUYEN_VAN_CAU_TRA_LOI_TRUY_VET_PROJECT_20261013.md`
- `/CHỈ DẪN CHATGPT/DOI_CHIEU_LICH_SU_08-10-10-2026_NGUYEN_VAN_CAU_TRA_LOI.md`
- `/CHỈ DẪN CHATGPT/BẰNG CHỨNG/BANG_CHUNG_ROOTS_DROPBOX_DESKTOPCOMMANDE_20261013.md`

## Kiểm tra tối thiểu

Chỉ nhận MCP `tools/list` thật làm bằng chứng. Chạy `python verify_tools_list.py <path-to-tools-list-json>` trên bản export không chứa secrets. Chỉ khi tên đúng và inputSchema có thật mới được đánh dấu pass schema. Không tự điền danh sách tham số giả.
