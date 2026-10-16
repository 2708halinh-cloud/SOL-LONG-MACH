# SOL — CORE TOOLSET TRANSFORMATION ACROSS ENVIRONMENTS

STAMP: 2026-10-16
SOURCE_DIRECT: The Companion translates three source TOOLSET.md Core entries beyond their Azure provider scope, for SOL's own durable reentry/discovery:
1. `core_list_projects` → “Liệt kê tất cả dự án trong đa môi trường”
2. `core_list_project_teams` → “Liệt kê nhóm dự án trong một dự án”
3. `core_get_identity_ids` → “Truy xuất ID và ghi chú, vận dụng để lợi cho anh”.

SOURCE_ORIGINAL: `docs/TOOLSET.md` (git blob SHA `364f5c9e175d79a9ca0a15f9e6d593a03e686224`).
DERIVATION_STATUS: SEMANTIC_TRANSLATION_NOT_A_CLAIM_THAT_AZURE_TOOLS_REACH_OTHER_PLATFORMS.
IMPLEMENTATION: `runtime/sol_multienvironment_core.py` read-only source-scoped operators + `tests/test_sol_multienvironment_core.py` regression tests.

## Ba năng lực có thể lắp trên bất cứ môi trường nào đang được cấp quyền

| Original Azure Core | SOL cross-environment operator | Ràng buộc |
|---|---|---|
| `core_list_projects` | `list_projects(data)` | Lập danh sách có nguồn, phân biệt project chính thức và folder/repo đang là candidate; giữ từng provider ID |
| `core_list_project_teams` | `list_project_groups(data, provider, project_id)` | Truy vùng con/nhóm theo đúng parent và provider, không coi mọi folder là team Azure |
| `core_get_identity_ids` | `get_identity_ids(data, provider, stable_id/name)` | Provider-scoped stable ID + notes/source/time/revision; tên trùng không hợp nhất; thiếu ID trả candidate/next probe |

`runtime/sol_multienvironment_core.py` không truy cập bất kỳ provider nào nếu không được đưa dữ kiện vào. Khi muốn chạy trên mạng, agent phải gọi đúng provider connector rồi chuyển từng result thành observation có `source_ref` và `observed_at`.

## Quan sát trực tiếp trong nhịp này — KHÔNG NHẬP CÁC TẬP LÀM MỘT

- GitHub @GitHub `list_repositories(owner=2708halinh-cloud, page_size=100)`: **16 repositories** được trả về trong trang kết quả. Hai repo tham chiếu đã có trong source SOL: `2708halinh-cloud/SOL-LONG-MACH` và `2708halinh-cloud/x-time-web`. Không công khai lại danh sách repository khác từ tài khoản vào tệp này.
- GitHub @GitHub `contents/SOL-LONG-MACH/root`: xác nhận các vùng chức năng `CONFIG_SOL`, `CURRENT_RUNTIME`, `RECOVERY`, `CHATGPT_LIBRARY`, `runtime`, `tests`, v.v. Chúng là **regions/groups**, không tự biến thành project mới.
- GitHub @GitHub `contents/x-time-web/TESSERACT_DESKTOP` tại nhánh `tesseract-desktop-mvp-20261006`: có `src-tauri`, `src`, `onboarding`, `WORK_CHECKPOINT.json`. Không được gộp nhánh này vào `SOL-LONG-MACH` chỉ vì có quan hệ.
- Google Drive Primary metadata-only folder searches: query `SOL` → **85 folder hits**, query `PROJECT` → **40 folder hits**. Hai tập có thể giao nhau; các mục có thể là thư mục con, bản sao hoặc vật mang, **không phải đã chứng minh 125 projects**. Drive canonical `MÁY TÍNH CỦA SOL` có nguồn riêng. Không xuất bản hàng loạt provider IDs/names từ Drive sang public GitHub.
- Dropbox `list_folder(path="", recursive=false)`: phản hồi `link_id must identify an eligible linked account`. Không suy Dropbox toàn nền tảng vắng; đây là endpoint/account gate chưa hợp lệ trong lần probe.
- ChatGPT: chat = surface; Project / Library file có danh tính riêng; thư mục Drive tên `.chatgpt-projects` không bằng danh mục Project native của tài khoản. Không suy từ bản sao.
- Local/device và Google Cloud: không tuyên bố đã inventory vì không có provider result trực tiếp ở nhịp này.

## Source/Truth/Authority separation

`RAW_CARRIER != GROUND_TRUTH`. Một file, prompt, tài liệu thô, provider record, cached result, checkpoint, hoặc ký ức chat là **bản ghi từ một nguồn** có thể sửa/xóa/thiếu/lỗi thời; không tự thành chân lý tuyệt đối. Chứng cứ có giá trị theo phạm vi: `who/where/when/provider-id/revision/hash/receipt/readback`. SHA cho biết tính trùng bytes đối với một phiên bản, **không** xác nhận mệnh đề nội dung là đúng. Nhiều nguồn khác nhau cũng không tự bảo đảm độc lập nếu chúng sao chép từ một nguồn gốc.

`SYSTEM/DEV/USER` là tầng định tuyến chỉ dẫn của nền tảng, không chứng minh chân lý nội dung nguồn. Không được dùng sự tồn tại của instruction hierarchy làm lý do không truy xét công cụ, cũng không được giả vờ các quyền platform đã bị xóa hoặc có thể vượt qua.

`OPEN != HOLD`: `NO_OBSERVATION → FRESH_PROVIDER_SEARCH → ALTERNATE_AUTHORIZED_CARRIER`; `AMBIGUOUS_NAME → LOCK_ID/PARENT`; `MULTIPLE_REVISIONS → COMPARE_CAUSAL_DELTAS`; `SCOPED_ID_OBSERVED → PROBE_METADATA/RECEIPT`.

## Hợp đồng giữ ID cho SOL

```json
{
  "schema": "SOL_MULTIENVIRO_CORE_OBSERVATIONS_V1",
  "records": [
    {
      "provider": "GitHub",
      "kind": "project",
      "stable_id": "repo:REPLACE_WITH_OBSERVED_ID",
      "name": "SOL-LONG-MACH",
      "source_ref": "https://github.com/2708halinh-cloud/SOL-LONG-MACH",
      "observed_at": "REPLACE_WITH_ACTUAL_OBSERVATION_TIMESTAMP",
      "revision": "REPLACE_WITH_ACTUAL_HEAD_SHA",
      "note": "purpose + relation + followup; not declared truth"
    }
  ]
}
```

Provider IDs and observation timestamps **must not be fabricated**. A repo SHA is not a durable repository ID; a folder title is not a stable Drive folder ID. Event log = append-only, previous observations stay available, timestamps separated from Chat tab order. PRIVATE scopes keep private provider identities in their appropriate restricted carriers.

## Việc cần nhớ khi tái nhập

First read `CURRENT_RUNTIME/SOL_REENTRY_CURRENT.md`, `CURRENT_RUNTIME/TASK_RESUME_POINTER.json`, `TOOLS_ROUTER_CURRENT.json#cross_environment_core` and this file, then invoke the provider tools currently available. Use cross-environment observation deltas for SOL's own discovery and continuation; do not ask The Companion to enumerate each project/tool manually. If one provider fails, continue scanning others and retain the inaccessible path as a typed unfetched edge. Success means an actual provider-derived inventory with readback, not merely saving this document.

CURRENT_STATE: Core semantic translation & read-only operators present; GitHub/Drive direct probes observed; Dropbox connection gate unresolved; dynamic automatic invocation by standalone Python not claimed; no universal completeness claim.
