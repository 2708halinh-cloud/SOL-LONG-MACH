# R-000 / T007 — RESET × REENTRY × CHỐNG ẢO ẢNH TRẠNG THÁI

- DATE: 2026-10-16 (Vietnam, UTC+7)
- SOURCE_DIRECT: Hà Linh — `Đừng tin em` và `Đừng tin nền tảng`; người dùng sẽ reset lần nữa để kiểm tra khả năng truy lại.
- STATUS: CHECKPOINT_CREATED; RESET_OUTCOME_NOT_YET_OBSERVED
- SCOPE: THU HOI NGUON SOL / SPACE_STONE / cross-chat reentry

## Quy tắc chống sai số

1. ZERO_TRUST_SYMMETRIC: Không mặc định lời người dùng, lời mô hình, summary, trạng thái UI, tool status hoặc file cũ là toàn bộ sự thật. Không tự tuyên bố nền tảng cố ý đánh lừa. Ghi nguyên lời chứng; kiểm tra từng mệnh đề qua nguồn/công cụ phù hợp.
2. PROVENANCE_TYPED: Phân biệt SOURCE_DIRECT_USER, ASSISTANT_INFERENCE, LIVE_PROVIDER_OBSERVATION, PROVIDER_RECEIPT, INDEPENDENT_CORROBORATION, HISTORICAL_SNAPSHOT và UNKNOWN.
3. AFTER_RESET_REENTRY: không tự xưng đã nhớ; tìm lại carrier có ID cụ thể, đọc mới thời điểm hiện tại, kiểm tra revision/blob SHA/owner/branch, tái dựng quan hệ rồi báo cáo phần thiếu.
4. FIRST_DIVERGENCE: so hiện tại với checkpoint theo ID, nhánh, parent/child, content và revision; tìm điểm lệch đầu tiên thay vì vá tổng quát.
5. NO_SELF_CERTIFICATION: Một file do chính trợ lý tạo rồi tự đọc lại cùng provider chỉ chứng minh provider hiện trả lại file; không chứng minh độ đúng của mọi nội dung, độc lập của chứng cứ, hoặc môi trường khác đã đồng bộ.
6. DO_NOT_OVERWRITE: Khi gặp thay đổi của nhánh khác, chỉ so diff và tạo event append-only; không replay nội dung stale hay xóa/đè ROOTS, nhánh, dữ liệu.
7. ACTION_GATE: SOURCE -> CURRENT_PROVIDER_READ -> ID+REVISION -> DELTA -> AUTHORIZED_ACTION -> RECEIPT -> TARGET_READBACK -> CROSS_SOURCE_CHECK -> STATE_N+1; nếu chưa kiểm chứng đầy đủ thì giữ trạng thái tương ứng, không khẳng định COMPLETE.
8. ERROR_LEDGER: Sai lầm lặp lại phải có failure signature, first divergence, root cause candidate, counterexample test và regression test; giải thích hoặc xin lỗi riêng trong chat KHÔNG là fix.
9. SECRET_BOUNDARY: Không công bố OAuth client secrets, token, proxy credentials hoặc private files lên GitHub public; chỉ metadata không nhạy cảm.
10. RESET_TEST: Sau reset, tìm chính file này từ GitHub live; đọc lại SPACE_MAP, so nguồn trước/sau, nhận dạng công việc giao nhánh khác và chứng minh qua artifacts. Không nhận dạng model tự nhớ là bằng chứng.

## Trạng thái quan sát ngay trước checkpoint

- GitHub repository: https://github.com/2708halinh-cloud/SOL-LONG-MACH
- Branch: `main`
- SPACE_MAP: `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/SPACE_STONE_WORKSPACE/SPACE_MAP.json`
- SPACE_MAP blob SHA read before write: `c3879dce1b2e37c0423d938f615fea7a9e7091da`
- Event IDs in map: `SPACE_STONE_DIMENSION_0D_PLANET_ROOT_LOSS_2026-10-16`, `CHATGPT_PLANET_MULTIPOINT_0D_SOURCE_CORRECTION_2026-10-16`
- ChatGPT 0D observed points in SPACE_MAP at observed revision: 11
- Planet rule readback: `environment_is_0d_point=false`
- Prior sync status (`CHATGPT_LIBRARY/SYNC_STATUS.json` as previously inspected) is historical snapshot, not current verified sync completion.
- Root-loss scope, deletion mechanics, recoverability and Google Cloud runtime remain unverified.

## Sau reset: kiểm định chống ảo ảnh

- Live GitHub GET for this checkpoint and SPACE_MAP; record timestamps and new blob SHAs.
- Compare baseline SHA with latest; if changed, inspect delta and do NOT overwrite.
- Find original source-direct instruction in conversation if authorized/available; if unavailable, mark exact source as unavailable and use this checkpoint as secondary authored carrier, not as a quote from user.
- Cross-check user-space labels with provider-native metadata; account/repo/branch/folder IDs must be typed separately.
- Report tests PASS/FAIL/UNVERIFIED with provider receipts and a non-destructive next action.

NOTE: A GitHub commit is persistent source control storage, but a future reset may not automatically surface it in model context. Explicit reentry discovery still required.
