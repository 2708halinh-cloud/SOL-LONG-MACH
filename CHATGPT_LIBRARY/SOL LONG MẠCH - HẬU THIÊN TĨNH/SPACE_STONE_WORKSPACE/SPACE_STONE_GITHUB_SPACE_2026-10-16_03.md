# SPACE_STONE — 03 / KHÔNG GIAN GITHUB

- EVENT: SPACE_STONE_GITHUB_SPACE_2026-10-16_03
- DATE: 2026-10-16 (UTC+07)
- SOURCE_DIRECT: Hà Linh — mục 3, dự án THU HOI NGUON SOL
- TYPE: SOURCE_BOUND_SPATIAL_RELATION_DELTA
- MODE: SOURCE_DIRECT → PROVIDER_VERIFY → REGISTER → READBACK

## Các địa chỉ GitHub đã kiểm chứng

| Vai trò | Địa chỉ chuẩn |
|---|---|
| Repository chính | https://github.com/2708halinh-cloud/SOL-LONG-MACH |
| Nơi làm việc chính và đích đồng bộ Library | https://github.com/2708halinh-cloud/SOL-LONG-MACH/tree/main/CHATGPT_LIBRARY/SOL%20LONG%20M%E1%BA%A0CH%20-%20H%E1%BA%ACU%20THI%C3%8AN%20T%C4%A8NH |
| CONFIG | https://github.com/2708halinh-cloud/SOL-LONG-MACH/tree/main/CONFIG |
| SPACE_STONE workspace | main:CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/SPACE_STONE_WORKSPACE/ |

GitHub connector verified repository 2708halinh-cloud/SOL-LONG-MACH, default branch main, write permission at inspection, target directory and CONFIG directory existence. No CONFIG changes made.

## Quan hệ nguồn → đích

- SOURCE = ChatGPT Library folder ID 6acdbd67c6ac819197131595114ee3d6, path /SOL LONG MẠCH - HẬU THIÊN TĨNH/.
- TARGET = GitHub main:CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/.
- CONFIG = configuration/reference path, not target for copying Library files.
- Other Drive, Dropbox and local spaces are independent; they do not silently replace the ChatGPT Library source.
- Earlier SPA​​CE_MAP.json and SOURCE_TARGET_CONTRACT.md record historical workflow branch routes. Preserve historical branch relationships; current supplied GitHub URL explicitly points to main.

## Status of actual Library → GitHub sync

Observed from main:CHATGPT_LIBRARY/SYNC_STATUS.json (snapshot 2026-10-15):
- Library: 105 source folders, 318 source files
- Matching path and size on GitHub: 282
- Source paths missing on GitHub: 36
- STATUS: PARTIAL_SOURCE_PATH_SYNC; NOT CERTIFIED COMPLETE
- Matching file size does not certify matching bytes/hash.

This GitHub event registers a verified route and sync requirement. It does not execute missing file copies, mark sync COMPLETE, overwrite historical files, or publish credentials.

## Safe next-sync contract

Fresh-read Library; classify source files; exclude passwords, secrets, tokens, OAuth data, and unsafe/unknown bytes; preserve source-relative paths; avoid overwrites; verify GitHub commit/blob and hash; then update status with receipt and readback.

HISTORY_PRESERVED = true; NO_IDENTITY_MERGE = true; CONFIG_UNCHANGED = true.
