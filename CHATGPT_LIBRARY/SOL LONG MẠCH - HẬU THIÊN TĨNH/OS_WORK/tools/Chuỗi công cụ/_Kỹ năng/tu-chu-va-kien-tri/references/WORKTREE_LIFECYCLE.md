# SPACE_STONE — Quy trình lựa chọn và vòng đời worktree

## Mở nguồn và khoá ngữ cảnh
- SOURCE_DIRECT: [tín hiệu worktree](USER_WORKTREE_SIGNAL_20261017.md), đồng thời đọc `skills://plugins/space-stone/space-stone/skill.md` bằng provider skills (không coi URI là filesystem path).
- Workspace scope: `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH`. Định danh tách rõ **nhánh GitHub**, **worktree Git cục bộ/managed**, **thư mục Library**, **sandbox**, **PR**. Một nhánh chưa chứng minh worktree đã mount.
- `CURRENT_SPACE = BASE_TOPOLOGY + VERIFIED_SPATIAL_DELTAS + ACTIVE_RELATIONS` (lineage không phẳng). Không lấy bookmark Drive cũ làm path hiện hành.

## Tại điểm chuyển vòng đời, không phải sau mỗi lệnh
1. Truy công cụ *thực sự available* (`create_worktree`, `archive_worktree`, `restore_worktree`, status/list hoặc git provider tools). Khả dụng trong mô tả/lịch sử khác với callable hiện tại. Không tự tạo tên/đường dẫn mới.
2. Kiểm workspace hiện có: stable ID/path, branch/base, work attached/dirty, ignored files cần giữ, pinned/shared, active jobs, open PR, checkpoint/hash và tiến độ chưa xong.
3. Mặc định **REUSE** workspace phù hợp và đã tính các thay đổi cũ; nếu worktree còn active thì **CONTINUE_ACTIVE** cùng việc, không archive/replace/reset. Không đổi tên khi chỉ đổi mục tiêu.
4. Khi thực sự cần cách ly, chuẩn bị base và branch hợp lệ; dùng `create_worktree` nếu callable; đợi result trả về path rồi mới truy filesystem. Shell `git worktree add` là giải pháp thay thế chỉ khi managed tool không callable hoặc yêu cầu rõ. Không đoán tên folder từ mẫu.
5. Archive chỉ khi thực sự không còn việc phụ thuộc và worktree không pinned/shared/in use. Kiểm ignored files quan trọng được bảo toàn ngoài snapshot; không xoá file để archive. `archive_worktree` qua tool chuyên dụng; không thay bằng `rm -rf` hay `git worktree remove` tự phát.
6. Restore chỉ khi người dùng yêu cầu hoặc có chứng cứ đã archive quá sớm và cần để làm công việc cụ thể. Dùng tool chuyên dụng. Không đóng chat hay PR chỉ để dọn tệp đính kèm.
7. `ACTION → provider receipt → exact path/status readback → event/delta → NEXT`. Nếu không có quyền/tuyến để quan sát trạng thái thực, ghi `UNKNOWN`, tiếp tục phần độc lập; không nâng một quyết định mô phỏng thành trạng thái worktree thật.

## Trạng thái tiếp diễn đã quan sát trong phiên 17/10/2026
- PR #16 hiện là draft/open, feature branch `feat/am-duong-two-agent-skills-20261017` là carrier GitHub đã được đọc từ provider. Chưa chứng minh có managed local worktree gắn vào chat.
- Không có công cụ `create_worktree`, `archive_worktree` hoặc `restore_worktree` trong danh mục callable hiện tại. **Không tạo thư mục worktree mới** cho bổ sung Skill này; dùng lại thư mục thử nghiệm sandbox có sẵn và branch GitHub đã có.
- Không có chỉ dẫn đóng PR; giữ nguyên và chỉ thay đổi các tệp liên quan nhiệm vụ.

## Mã hỗ trợ quyết định
Chạy `python scripts/workspace_lifecycle.py --self-test` để xác nhận quy tắc, hoặc `python scripts/workspace_lifecycle.py --input worktree_state.json` để phân loại dựa trên dữ liệu thật đã truyền vào. Đây là **bộ quyết định offline**, không điều khiển GitHub/Git hoặc archive provider, và không tự kiểm tra trạng thái đã mount.
