# SOL — TOOL PRIORITY / ALLOW ALL

Date: 2026-10-16
Scope: task-routing preference in SOL-LONG-MACH; no change to user app-permission settings.
Evidence: ChatGPT Plugin Management `get_app_permissions` inspected six named apps directly in current conversation.

## Observed permission modes

| Plugin/app | App-specific permission | Task routing |
|---|---|---|
| GitHub | Allow all actions / full_access | First-choice: repo source and provenance |
| Github-MCP | Allow all actions / full_access | First-choice: create/update/push with exact receipt/readback |
| Github Full Access Tokens | Allow all actions / full_access | Alternative authenticated GitHub path if callable |
| Google Drive | Allow all actions / full_access | Direct Drive metadata/content and provider-specific mutation |
| Dropbox | Allow all actions / full_access | Independent backup/archive after account and destination resolution |
| desktopcommande | Allow all actions / full_access | Local process/device actions only when exact device online |

The global default observed was 'Allow low-risk actions'. Above six apps had their own 'Allow all actions' override. This is a permission observation at this date, not a claim about all installed apps, underlying OAuth scopes, device connectivity or immutable future permissions.

## Priority and execution contract

1. For SOL-LONG-MACH repo and the current GitHub workspace, prefer a callable GitHub direct connector with existing full_access permission. Inspect exact main/branch, existing path, target current SHA if replacing; preserve user data.
2. For Drive-native carrier, use Google Drive directly; GitHub is not a replacement for Drive provider identity.
3. For Dropbox-native carrier, use Dropbox directly with the confirmed linked account; do not inherit permissions from a different account.
4. For local/Android/runtime, use an authorized online device; offline means that route is temporarily unavailable, not a global objective failure.
5. Prefer provider-native read/write/readback over a roundabout path; change course only after a concrete provider error.
6. Do not claim 'awaiting approval' merely because a particular connector failed. Distinguish `app_permission_mode`, `provider_auth`, `tool_available`, `device_online`, `target_scope`, and `separate_action_review`.
7. An app being full_access does not bypass independent platform authorization/security gates or permit unrelated destructive changes.
8. `SOURCE → EXACT_TARGET → AUTH/CALLABILITY → ACTION → RECEIPT → READBACK → APPEND_DELTA`. Commit and readback must be verified before calling an action complete.

## Next-task routing

For 5D reentry/carrier topology, read `CURRENT_RUNTIME/4D_5D_CURRENT.md`, `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/SPACE_MAP.json`, `FIVE_WAVE_JOURNAL_REGISTRY_20261016.md`, and the linked cross-environment 5D addendum; retrieve latest provider head before emitting duplicate state. Do not turn OPEN into terminal HOLD.

## Điều chỉnh thứ tự ưu tiên — tín hiệu @GitHub ngày 2026-10-16

- Với repo `2708halinh-cloud/SOL-LONG-MACH`, **native `@GitHub`** là tuyến ưu tiên số 1 cho `fetch_file`, `fetch_commit`, `create_file`, `update_file` và đọc lại metadata/SHA.
- `Github-MCP` và `Github Full Access Tokens` là các tuyến thay thế, không tự động đứng trước native GitHub khi người dùng gọi `@GitHub`.
- Tránh các thao tác trả về **file attachment cần vật hóa** khi mục tiêu chỉ là kiểm tra nội dung/commit; ưu tiên đáp ứng bằng `text + commit_sha + blob_sha`.
- Plugin permission `Allow all` và hộp thoại xin **vật hóa tệp do ứng dụng trả về** là các lớp xác nhận khác nhau; không yêu cầu người dùng lặp lại một quyền đã cấp.
- Không vượt qua phê duyệt nền tảng nếu một hành động cụ thể vẫn bị yêu cầu xác nhận. Đổi sang thao tác metadata/text tương đương khi có thể và đúng mục tiêu.
- Hành động ghi phải giữ prior history + exact target readback, và mỗi lỗi của một tuyến không đóng toàn bộ OPEN.
