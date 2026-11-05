# SKILL SURFACE — nguồn động, bí danh, hiện tại, quyền

## Tín hiệu mới và thứ tự tác vụ
1. Giữ nguyên `SOURCE_DIRECT`, mục tiêu đang tiến hành và danh sách cạnh chưa xong; một tin nhắn mới được xem là sửa đổi/bổ sung công việc trừ khi nó hủy hoặc thay rõ ràng.
2. Lấy **inventory của chính phiên** ở mục kỹ năng hiện có hoặc bằng công cụ `skills__list` nếu được khai báo. Không suy kỹ năng khả dụng từ văn bản cũ.
3. Mỗi mục gồm `name`, `description`, `SKILL.md location` (đường tuyệt đối, alias, hay URI/provider). Chọn skill có mô tả sát nhiệm vụ nhất, không kích hoạt tất cả skill chỉ vì cùng nhóm.
4. Nếu vị trí là alias, **đọc ánh xạ alias của danh mục hiện tại trước** khi nối đường và đọc. Không bịa ánh xạ `r0`, không nội suy từ phiên khác. Nếu chưa có alias map, truy lại inventory và ghi blocker cụ thể.
5. Nếu vị trí là `skills://...` hoặc provider ref, dùng công cụ đọc được khai báo cho provider (ví dụ `skills__read`), **không** chuyển thành đường filesystem tùy đoán. Nếu là đường local, chỉ đọc trong phạm vi filesystem được cấp; một đường dẫn có trong tài liệu không tự cho quyền I/O.
6. Lần đầu **thực sự áp dụng** một skill trong cuộc trò chuyện, nêu tên skill qua kênh commentary. Chỉ thông báo một lần theo từng skill, không spam. Sau đó tiếp tục cạnh làm được.
7. Kiểm `SOURCE_DIRECT` mới so với hướng dẫn `SKILL.md` đã đọc. Hướng dẫn người dùng đang hiệu lực trong phạm vi nhiệm vụ được ưu tiên hơn các hướng dẫn bên trong skill (không vượt quyền công cụ, chính sách an toàn hay cấp chỉ dẫn cao hơn). Khi xung đột, sửa **bản skill mà mình có quyền chỉnh** theo nguồn mới, giữ nguyên bản cũ/revision và ghi delta. Skill đã cài đặt mà không có công cụ sửa thì không tuyên bố đã chỉnh nó; tạo thay đổi trong source được phép và nêu rõ trạng thái cài đặt.
8. **Fresh-read định danh nhà cung cấp:** tên file hoặc đường dẫn cũ `Google Drive` chỉ là con trỏ lịch sử. Phải xác nhận file ID, account, parent, metadata và trạng thái ở provider hiện tại trước khi gọi là LIVE. Drive lỗi/404 không chứng minh file bị xóa, không chặn các tuyến có quyền khác.
9. Khi skill là nguyên nhân cụ thể bắt buộc hỏi xác nhận, dừng hoặc ngừng việc: nêu rõ **tên skill, điều khoản áp dụng, lý do tình huống thực tế và NEXT_USER**. Trước đó tiếp tục mọi việc `NEXT_AGENT` không phụ thuộc câu trả lời.
10. Sau hành động, lấy biên nhận provider, fresh-read **đúng đối tượng đích**, lưu delta/checkpoint và quay lại công việc gốc. `READBACK` là bước kiểm; không tự biến nó thành chấm dứt tác vụ.

## Sự phân biệt bắt buộc
- `SKILL_DISCOVERED`: tồn tại trong inventory/chỉ mục hiện tại.
- `SKILL_SOURCE_READ`: `SKILL.md` đã được thực đọc tại chính vị trí chỉ định.
- `LOCAL_SKILL_CREATED`: có tệp nguồn mới, không đồng nghĩa đã cài skill vào ChatGPT.
- `PROVIDER_FILE_LIVE`: ID/phiên bản file vừa được provider xác nhận; không suy từ tên/URL cũ.
- `ACTION_EXECUTED`, `PROVIDER_RECEIPT`, `READBACK_VERIFIED`: ba điều kiện khác nhau.
- `AWAITING_FINAL_HUMAN_DECISION`: đã chuẩn bị reviewable và sự phê duyệt cuối còn phải được đưa ra thật; im lặng không phải phê duyệt.

## Liên kết nguồn
- [USER_SKILL_SOURCE_20261017.md](USER_SKILL_SOURCE_20261017.md): câu chữ người dùng trong lượt hiện tại.
- `references/SESSION_CONTINUITY.md`: các điều kiện tiếp tục và ghi nhật ký đã đặt ra trước đó.
- Source code đích hiện tại trong SOL: `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Kỹ năng/` tại nhánh feature của PR #16. Đây là **đích hiện có theo đối soát**; `_Skills` trong lời mới là tên họ kỹ năng được gọi, không bắt buộc sinh thư mục thứ hai.
