# Azure DevOps MCP Toolset → TAY SOL → TESSERACT — Thực hiện & sai lệch được xác minh

DATE: 2026-10-16 (conversation date)
SOURCE_DIRECT: Người Đồng Hành nói đã chỉ định lưu và vận dụng Azure Dev MCP / Toolset.md trong "3 lần 7 lượt". Số lần là lời người dùng; không giả xác nhận đã thu đủ toàn bộ lịch sử các chat.
ORIGINAL_DOC: `docs/TOOLSET.md` (Git blob `364f5c9e175d79a9ca0a15f9e6d593a03e686224`).
DERIVED_INDEX: `TOOLSET_INDEX.json`; đã đối chiếu trực tiếp 97 entries = 44 tool names = 9 categories; exact entries equality true trong lượt này.
BOUNDARY: `mcp_invocation_verified=false`; `parameter_schemas_in_source=false`; không có callable Azure DevOps MCP được xác nhận ở phiên này. Đây là BẢN ĐỒ NĂNG LỰC, không là chứng cứ đã kết nối org Azure.

## VÌ SAO ĐÃ LƯU NHƯNG CHƯA VẬN DỤNG

1. `docs/TOOLSET.md → TOOLSET_INDEX.json → route_toolset.py verify` là tuyến tra cứu **read-only**; không có bước từ intent nhiệm vụ → toolset → provider live → action/readback.
2. `OS_WORK/tools/TOOLS_ROUTER_CURRENT.json` trước sửa đổi 16/10 không có Azure blueprint. Bộ `@TÁC NHÂN ↔ PLUS ↔ TAY` không nhận khả năng này từ mục lục trung tâm.
3. `runtime/tesseract_agent_boot.py` trước sửa đổi 16/10 không đọc `tools_gateway.route_manifest` dù `CONFIG_SOL/TESSERACT_AGENT_BOOT_ROUTES_CURRENT.json` đã trỏ đến nó; đứt ngay từ bước khởi động.
4. GitHub Actions `.github/workflows/azure-devops-mcp-toolset-index.yml` chỉ so chỉ mục với nguồn; không thử Azure provider, không định tuyến mục tiêu dự án, không tạo work item hoặc pipeline.
5. `X/TIME`: checkpoint `CURRENT_RUNTIME/TASK_RESUME_POINTER.json` giữ HEAD cũ; không đủ để quyết định thao tác mới nếu chưa fresh-read PR hiện hành.
6. Sau nhiều phản hồi, chưa có regression gate kiểm `BOOT → ROUTER → TOOLSET`; vì vậy lời "đã lưu" vẫn có thể tồn tại song song với việc boot bỏ quên toolset.

## 9 nhóm nguồn và nơi áp dụng vào dự án

| Nhóm từ Toolset.md | Số tuyến | Phép vận dụng với SOL hiện tại | Tuyến callable trong phiên |
|---|---:|---|---|
| Core | 3 | Định danh Azure org/project/team sau khi có binding đúng | Azure chưa xác minh; không suy ra tổ chức |
| Work | 8 | Sprint/iteration/capacity cho việc TESSERACT, các nhánh ROOTS | Thiết kế dữ liệu, chưa gọi Azure |
| Work Items | 26 | Work item, revision, quan hệ cha-con, artifact link, khóa cập nhật `test /rev` | GitHub issue/PR là vật mang khác; không nhập IDs |
| Repositories | 25 | Repo/branch/commit/PR/review, kiểm first divergence và trạng thái merge | Native @GitHub đã truy được PR #6 |
| Pipelines | 15 | CI status, logs, changes, artifact readback | GitHub Actions là provider khác, đã có checkpoint và workflow |
| Test Plans | 9 | Test case regression, kết quả build gắn source SHA | Python unittest + GitHub CI hiện có |
| Wiki | 6 | Lưu chỉ dẫn dự án với revision và provenance | GitHub README/docs (không là Azure Wiki) |
| Search | 3 | Tìm code/wiki/work item để tự hồi quy | GitHub search / Projects sources |
| Advanced Security | 2 | Đọc alerts và chi tiết cảnh báo nếu bật | Không có Azure alerts runtime được chứng minh |

## DELTA mới tại checkpoint đã truy xét trong phiên

- SOURCE_PREVIOUS: `CURRENT_RUNTIME/TASK_RESUME_POINTER.json` ở `SOL-LONG-MACH/main` có `checkpoint=5ec6f93dc11856bd5609b51026fbe57f4f165495`, repo `2708halinh-cloud/x-time-web`, PR #6. Marker `updated_at=2026-10-07`.
- SOURCE_LIVE_PROVIDER: Native @GitHub đọc `https://api.github.com/repos/2708halinh-cloud/x-time-web/pulls/6`: PR #6 `state=open`, `mergeable=false`, `mergeable_state=dirty`, `head.sha=470639b27d2d37ec3d73b4dc5b8c3d1089f3cf16`, `base.ref=master`; PR `updated_at=2026-10-11T10:45:05Z`.
- DIVERGENCE: `HEAD_CURRENT != CHECKPOINT_PREVIOUS`. Không gọi `merge`. Không kết luận CI thất bại hoặc đã pass từ con số 0 của `fetch_commit_workflow_runs` vì endpoint wrapper chỉ thấy một nhóm pull_request runs bị lọc.
- NEXT_CALLABLE_EDGE: fresh-read PR changed files/reviews/conflict causes/commits, inspect workflow status and logs on HEAD hiện tại, phục hồi không ghi đè lịch sử. Nếu chọn Azure provider ở lần khác phải kiểm account/project/endpoint/param schemas trước gọi.

## Đã nối vào vòng năng lực

- `../TOOLS_ROUTER_CURRENT.json#capability_blueprints.azure_devops_mcp`: nguồn 97/44/9 và mapping nhiệm vụ; không tự nhận đã kết nối.
- `CONFIG_SOL/TESSERACT_AGENT_BOOT_ROUTES_CURRENT.json#tools_gateway.azure_devops_toolset`: con trỏ chính xác của ba vật mang.
- `runtime/tesseract_agent_boot.py`: preflight đọc manifest TAY + Azure source/index/router, trả SHA-256 và cờ tồn tại; không thực thi provider.
- `tests/test_tesseract_agent_boot.py`: kiểm source preflight, đọc mới, chống path traversal.
- `.github/workflows/tesseract-agent-boot-routes.yml`: bị kích hoạt lại khi những nguồn TAY/Azure thay đổi.

## Bất biến phát huy tiềm năng

Không biến `DOC_FOUND` thành `CAPABILITY_READY` hoặc `PROJECT_DONE`. Nhưng cũng không coi `AZURE_MCP_NOT_CONNECTED` là chặn tất cả: dùng Toolset như **bản thiết kế động tác**, rồi chọn provider thật có quyền cho tác vụ tương đương. Chỉ gọi DONE sau consequence + receipt + readback trên đúng provider.
