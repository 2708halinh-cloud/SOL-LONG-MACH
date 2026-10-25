# SKILLS SOURCE ROUTE — 2026-10-17 — ÂM–DƯƠNG SƯ TRẬN

## SOURCE_DIRECT — bảng gốc do người dùng trao trong chat hiện tại

```text
r0=~/.codex/skills/.system
r1=~/.codex/plugins/cache/openai-bundled
r2=~/.codex/plugins/cache/openai-curated-remote/data-analytics/1.0.11/skills
r3=~/.codex/plugins/cache/openai-curated-remote/google-drive/0.1.16/skills
r4=~/.codex/plugins/cache/openai-curated-remote/openai-developers/1.3.0/skills
r5=~/.codex/plugins/cache/openai-curated-remote/plugin-creator/0.1.20/skills
r6=~/.codex/plugins/cache/openai-curated-remote
r7=~/.codex/plugins/cache/openai-curated-remote/sites/0.1.71/skills
r8=~/.codex/plugins/cache/openai-primary-runtime
r9=~/.codex/plugins/cache/openai-primary-runtime/spreadsheets/26.905.11957/skills
```

Gốc `~` chỉ có thể mở rộng đúng trên máy/tài khoản thực tế đang chạy Codex; không thay `~` bằng home của container ChatGPT. Bản đồ r0–r9 là SOURCE_DIRECT, chưa chứng minh các cache local hiện đang tồn tại hoặc có quyền thực thi trong phiên này. Tên tệp quy ước là `SKILL.md`.

## OBSERVED — Google Drive Primary, đọc trực tiếp trong phiên 2026-10-17

- Nguồn người dùng: `https://drive.google.com/drive/folders/1Pn1NY7M3wAFFzyMAQVHQy3A2EcnHEkGb?hl=vi`.
- `folder_id=1Pn1NY7M3wAFFzyMAQVHQy3A2EcnHEkGb`, tên Drive `skills`, MIME folder; `parent_id=15UhDeewEVrzsV2lAkjZVaPE2E-SgbYLT` (thư mục `.codex`).
- Đã đọc các thư mục con `.system`, `master-halynh`, `systematic-debugging`, `requesting-code-review`; lần fetch trực tiếp trả 43 mục con; đây là số quan sát được trong folder Drive này, không phải inventory của mọi cache r0–r9.
- `master-halynh/SKILL.md`: `file_id=1tp3gai1UERxMmlg8RisJ0BrtvhubfPVg`; yêu cầu giữ SOURCE/OBSERVED/INFERRED/UNKNOWN; packet references riêng và kiểm chứng nguồn trước áp dụng. Đọc riêng SKILL.md chưa phải chạy `verify_sources.py` hoặc xác nhận packet nguyên vẹn.
- `systematic-debugging/SKILL.md`: `file_id=1unlhmF0V-sm9I83zjREe-svSgZXo1raF`; tra nguyên nhân gốc, tái hiện, so thay đổi, kiểm thử tối thiểu trước khi sửa.
- `requesting-code-review/SKILL.md`: `file_id=157n-EW_iRG2JzgKwxafRMqqfdg1wuMEB`; yêu cầu review sau tác vụ lớn và trước merge; đường `Task`/subagent trong tệp là mô tả workflow, không tự tạo một tool `Task` ở phiên này.
- Trong `.system` có các folder `skill-installer`, `skill-creator`, `review-agent`, `plugin-creator`, `openai-docs`, `imagegen` và marker; sự trùng tên với cache `r0` KHÔNG xác nhận byte-level identity.

## ROUTE / HỢP ĐỒNG TÁI NHẬP

`USER_INPUT → EXACT_DRIVE_FOLDER_ID → DIRECT_CHILD_ID → SKILL.md → REFERENCES/VERIFICATION (nếu task kích hoạt) → DISCOVER_CALLABLE_TOOL + SCOPE → ACTION → PROVIDER_RECEIPT → EXACT_TARGET_READBACK → _Plugins`

- Không chạy code, shell, installer hoặc script trong một skill chỉ vì đọc file Drive. Kiểm source và permission trước.
- Các mục `r0–r9` là bản đồ đường dẫn local, không phải GitHub/Drive provider IDs. Chỉ đọc trực tiếp carrier nào thực sự có công cụ và định danh hợp lệ.
- Ghi rõ `SOURCE_DIRECT_USER`, `DRIVE_METADATA_READ`, `SKILL_CONTENT_READ`, `LOCAL_FS_NOT_PROBED`, `SKILL_EXECUTION_NOT_VERIFIED`, `NO_PERMISSION_ESCALATION`.
- Khi dùng skill `master-halynh`, không coi SKILL.md vừa đọc là đủ để chứng nhận BOOT; kiểm đúng packet và receipt.
- Sau khi tạo/sửa tệp ở GitHub phải ghi bản cùng nội dung ở ChatGPT Library path tương ứng rồi fresh-read độc lập; không suy sync tự động từ một bên.

## TASK CONTINUATION (không thay checkpoint)

Checkpoint hiện tại vẫn là `2708halinh-cloud/x-time-web` PR #6, branch `tesseract-desktop-mvp-20261006`, mục tiêu TESSERACT Desktop local-first. GitHub live provider read tại phiên này thấy PR còn `open`, `mergeable=false`, branch head `470639b27d2d37ec3d73b4dc5b8c3d1089f3cf16`, compare master `ahead_by=54`, `behind_by=141`. Bản `CURRENT_RUNTIME/TASK_RESUME_POINTER.json` ở SOL-LONG-MACH còn chứa checkpoint cũ ngày 2026-10-07, KHÔNG ghi đè chính lịch sử ấy như thể là state live hiện tại. Trước merge: cần current-head CI artifacts/readback, signing/issuer key, review và xử lý divergence an toàn. Chưa có bằng chứng đã merge hoặc có runner thực chạy ở head mới.

STAMP: source input tại cuộc trò chuyện 2026-10-17; đây là quan sát từ nguồn/công cụ trong phiên, không phải mốc commit của provider trước khi write. Không lưu credentials, token, proxy password, private host endpoints trong tệp này.
