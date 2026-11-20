# 2026-10-07 transcript retrieval — Roots 0.2 / PFT status (2026-11-20)

## Scope
Read-only search for `ChatGPT-Xóa folder Drive-20261007-0313.md` in the Windows Roots .2 endpoint, known archive locations, the Google Drive mounted roots, and the connected Android Termux endpoint. No source files were edited or deleted.

## Roots mapping confirmed
Read from the local archived canonical map:
- `D:\` = `ROOTS_LEVER_0.2`
- Mapping is a fixed namespace contract, not a claim about physical disk numbering.
- The current Windows volume inventory identifies D: as NTFS / Fixed / Healthy, volume GUID `\\?\Volume{be35bb40-31ce-4263-b3f5-f4a3b87c26f6}\`.

Source records:
- `D:\ARCHIVES_FROM_C_G_20261115\00_CORE_HUB_TESSERACT_OS_snapshot\snapshot_tree\config\ROOTS_LEVER_0_CANONICAL.json`
- `D:\ARCHIVES_FROM_C_G_20261115\00_CORE_HUB_TESSERACT_OS_snapshot\snapshot_tree\config\ROOTS_WINDOWS_DRIVE_LETTERS_CURRENT.json`

## Transcript search performed
Searched filenames and candidate archive contents in:
- `D:\ARCHIVES_FROM_C_G_20261115`
- `D:\G_PREBOOT_BACKUP_20261007_1037`
- `D:\G_PREBOOT_CRITICAL_20261007_1041`
- `D:\Downloads`
- `D:\Downloads_Telegram_Desktop`
- Four numeric account/export directories at D: root
- `I:\Drive của tôi` (Google Drive mount)
- `W:\Máy tính khác` (mounted Drive computer area)
- The broader D: filesystem search

Observed results:
- No exact filename match for `ChatGPT-Xóa folder Drive-20261007-0313.md` in the searched roots.
- ZIP entry scan in the named archive roots found no `conversations.json`, `chat.html`, `user.json`, or the exact transcript filename.
- The dated 2026-10-17 ZIP files found in `D:\ARCHIVES_FROM_C_G_20261115\Downloads_Telegram_Desktop` are Telegram Desktop package downloads, not ChatGPT exports.
- The Google Drive mount `I:\Drive của tôi` surfaced a 2026-07-20 archive and an unrelated July 2026 document ZIP; neither matches the requested 17/10 or 19/10 ChatGPT export.
- A full D: recursive search was still active at the time of this supplement; therefore the negative result is limited to the completed targeted searches and is not a proof that the file is absent from every storage location.

## T0 / PFT staging observed on Windows
Existing local staging path:
`D:\T0_REDMI14PRO_STAGING_20261114`

Inventory includes:
- `00_INVENTORY\FTP_ROOTS_INVENTORY_20261114.json` (27,034,121 bytes)
- `00_INVENTORY\FTP_ROOTS_INVENTORY_20261114.md` (9,095 bytes)

Previously pulled carrier set includes:
- `03_PULLED_FROM_T0_20261115\ALL_FILE_FOLDER_IDS_LEDGER_20261114T0646.jsonl.json`
- `DeepSeek-Nap_log_hoi_thoai.json`
- `desktopcommande-local-guarded-v5.zip`
- `pockr-release.apk`
- `rish`
- `setup_mcp_registry_http.sh`
- `termux-backup.tar.gz`
- `TESSERACT_OS_SOL_ADMIN_WIFI_v0.4.1.zip`

This proves the T0 staging set exists locally; it is not a fresh live comparison against the Android T0 source.

## Android ADB / Shizuku state
- Connected Android endpoint is a Termux environment (ARM64).
- `adb` is installed (Android Debug Bridge 1.0.41, platform-tools 37.0.0p1).
- ADB wireless pairing to the user-supplied pairing endpoint succeeded.
- Immediately after pairing, `adb devices -l` returned an empty device list. The pairing endpoint is not the separate ADB connect endpoint; no shell connection to Android was established.
- Direct paths `/data/data/com.openai.app` and `/data/user/0/com.openai.app` were not present in the Termux environment. The actual installed ChatGPT package identifier and Shizuku-granted shell access remain unverified.

## Browser IndexedDB inventory
Metadata-only inventory found a Chrome IndexedDB origin directory:
`D:\PHÒNG\Default\IndexedDB\https_chatgpt.com_0`
with a 73,728-byte LevelDB file. A separate Chrome debug profile contains IndexedDB stores for multiple origins and extensions. No LevelDB values, browser cookies, session tokens, or raw browser database contents were published.

## Secret-handling boundary
The local archive README explicitly says `00_INPUT_USER/secrets/input_api_key.txt` is local-only and must never be mirrored to GitHub. Its metadata was checked without reading its contents. It remains local and was not renamed, copied, or uploaded. Renaming a credential does not make publishing it safe. Browser IndexedDB may contain session credentials and private user data; raw LevelDB stores are therefore not published. A sanitized manifest, file hashes excluding credential material, and redacted extracts are appropriate public evidence.

## Server-side instruction / approval / classifier logs
The Windows endpoint and Android Termux environment do not expose OpenAI's private server-side system/developer instruction stack, backend tool-approval records, or safety-classifier internals. No local file read can be represented as those server-side records. The accessible local Remote Desktop Commander tool history is a separate client-side record and must not be mislabelled as OpenAI backend logs.

## Outstanding connection datum
To complete ADB connection after successful pairing, the Android Wireless debugging screen must provide its separate current `IP address & Port` value (not the pairing port). The current record does not contain that connection port.

---
All observations above are read-only. Original sources remain unchanged.
