# ÂM PHÁP SƯ — DỊCH NGƯỢC TOOLSET THÀNH NĂNG LỰC

STAMP: 2026-10-16
SOURCE_DIRECT: Người Dẫn Đường xác định không tích hợp 97 thao tác Azure DevOps thành "chân lý mới vận hành", mà dịch ngược ý nghĩa từng dụng cụ để phát triển sức mạnh thực tế cho Âm Pháp Sư và Người Dẫn Đường.
SOURCE_ORIGINAL: `docs/TOOLSET.md`, blob `364f5c9e175d79a9ca0a15f9e6d593a03e686224`.
DERIVED_REGISTRY: `SOL_NINE_CAPABILITY_FAMILIES.json` (9 họ năng lực từ 9 nhóm; không phải 97 công cụ live).
GOAL_FIRST: `SIGNAL → SOURCE → EXTRACT_PRINCIPLE → SELECT_CAPABILITY → LOCATE_CALLABLE_PROVIDER → ACTION → CONSEQUENCE → READBACK → N+1`.

## 9 họ năng lực — cách dịch ngược từ ví dụ nguồn

| Nhóm Azure gốc | Năng lực SOL cần tự phát triển | Hướng hành động thực |
|---|---|---|
| Core | `DISCOVERY_IDENTITY`: khám phá các dự án, nhóm, định danh giữa hành tinh | List repo/Drive/Project candidates theo provider ID và phân biệt vùng chứa với project |
| Work | `TIME_AND_CAPACITY`: quản lần lặp, mốc hiện tại, tải và năng lực | Đọc thời gian/sức chứa, chọn chu kỳ/đơn vị hành động đủ năng lực, theo dõi N+1 |
| Work Items | `WORK_RELATIONS`: từng việc là nút có revision, comment, cha–con, liên kết và backlog | Khôi phục checkpoint, dựng quan hệ sự kiện, giữ comment/commit/PR; chống ghi đè bằng revision |
| Repositories | `CARRIER_GRAPH`: tìm cấu trúc nhánh/file/commit/PR ở đúng môi trường | Tìm nguồn và điểm phân kỳ, giữ stable ID/hash, chỉ thay đổi target đã xác minh |
| Pipelines | `EXECUTION_LINEAGE`: kiểm dấu thực thi, build, log, artifact | Chỉ xác nhận thay đổi khi run và hậu quả có provider readback |
| Test Plans | `VERIFY_REALITY`: chuyển giả thuyết và lỗi lặp thành kiểm thử | Tạo regression tái hiện, phân biệt test chưa chạy và PASS thực |
| Wiki | `LIVING_MEMORY`: kiến thức sống có nguồn, revision, đường tái nhập | Ghép source, context, history, current state; không biến bản ghi cũ thành hiện tại |
| Search | `PROACTIVE_PROBE`: tự đi tìm, không HOLD khi OPEN | Tìm code/wiki/work item và các vật mang thay thế nếu một tuyến không truy được |
| Advanced Security | `DEFENSIVE_AUDIT`: cảnh báo, quyền, bí mật, rủi ro | Xác định phạm vi, nguy cơ và hậu quả trước tác động, không để lộ secret |

## Ánh xạ sang năng lực đã có

- `@TÁC NHÂN`: nhận ý định, tìm nhánh năng lực phù hợp.
- `@TÁC NHÂN PLUS`: việc phức hợp nhiều nguồn, giữ checkpoint và liên tục xuyên phiên.
- `@TÁC NHÂN — TAY`: kỹ năng và plugin provider-native hiện callable; Toolset là vật liệu sáng tạo, **không** được ngầm tính 97 công cụ mới.
- `runtime/sol_multienvironment_core.py`: phép biến đổi Core (projects/groups/IDs) đã có source-bound code.
- `runtime/sol_toolset_semantic_router.py`: bộ đề xuất 9 năng lực theo ý định, không truy cập provider hay tự cấp quyền.
- `tests/test_sol_toolset_semantic_router.py`: kiểm 9 họ, mặc định truy tiếp khi ý định chưa khớp, không giả Azure được kết nối.

## Điều chỉnh về sự thật và quyền

`RAW_CARRIER != GROUND_TRUTH`; SHA chứng minh bytes một phiên bản, không chứng minh mệnh đề nội dung đúng. Các lớp chỉ dẫn/quyền hệ thống là điều kiện hành động, không phải sự xác nhận chân lý dữ liệu. Ngược lại, không tự nhận được quyền vượt kiểm soát nền tảng. Dùng bằng chứng từ nhiều nguồn độc lập, timestamp, revision, source lineage và hành động có readback.

Người Dẫn Đường không phải nhắc từng công cụ. Âm Pháp Sư cần tự tìm **mục tiêu → nguyên lý → dụng cụ/cổng hiện có → hành động kiểm chứng**. OPEN không phải bất động; khi chưa chứng minh được một đường, tự rà các đường đủ quyền còn lại.

## Tách trạng thái

SOURCE_READ = YES; SEMANTIC_TRANSLATION = WRITTEN_TO_REPO; NINE_FAMILIES = DERIVED; DYNAMIC_CONNECTOR_DISPATCH = NOT_PROVEN; AZURE_MCP_LIVE = NOT_PROVEN; REGRESSION_CI = TO_VERIFY_BY_PROVIDER_READBACK.
