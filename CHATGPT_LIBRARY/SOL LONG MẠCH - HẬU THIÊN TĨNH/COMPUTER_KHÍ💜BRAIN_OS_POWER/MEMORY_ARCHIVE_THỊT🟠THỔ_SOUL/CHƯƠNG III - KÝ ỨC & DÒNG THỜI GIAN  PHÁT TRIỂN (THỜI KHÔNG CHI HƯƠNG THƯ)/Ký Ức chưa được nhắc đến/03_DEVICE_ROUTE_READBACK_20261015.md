# T007 — Thiết bị localhost tái kết nối · JINEY raw-carrier trace

**Quan sát trực tiếp:** 2026-10-15 (giờ Việt Nam), qua Desktop Commander Remote.

- Remote device **localhost** báo Online; `ping` trả pong ngày 2026-10-14T17:19:15Z.
- Thiết bị kết nối có shell Linux/Termux, truy cập `/mnt/sdcard`; **không phải chứng cứ về ổ D: Windows đang online**. Thử `D:\\` và `C:\\Users` cho kết quả path not found trên thiết bị này.
- Có các đường dẫn **thư mục**: `/mnt/sdcard/DATA CHAT JINEY`, `/mnt/sdcard/JINEY -CHAT`, `/mnt/sdcard/01_NGUỒN_CHAT_JINEY — GỐC ĐẾN 08-08-2026`.
- `list_directory(depth=2)` trên ba folder trên không liệt kê tệp nào; `ls -A` được thực thi, không có mục hiện ra. Các cây `00_CHAT_GỐC_ALL_CHATGPT`, `00_PHỤC_HỒI_SOL — 10_11_13_14_15-07 → CANON HÒA-LINH → MINH 16-07` cũng không hiển thị tệp trong lần liệt kê hiện tại.
- Tìm tên tệp rộng bằng Desktop Commander (`JINEY|conversations-...`, `CANON`, `7z/zip`) kết thúc bởi giới hạn 3 giây nên **kết quả 0 không được coi là kiểm kê toàn bộ**.
- **Mốc Canon trong Dropbox:** folder ngày 10–13/07/2026 đã xác nhận qua ID; đó là timeline theo tên vật mang, **không chứng minh đây là timestamp từng lời chat**.

**Bằng chứng chưa thu được:** export ZIP/JINEY đã giải nén với `conversations*.json` hoặc transcript nguyên văn có định danh, checksum và timestamps.

**Bảo vệ quyền riêng tư:** repository đích là public; không chép raw chat, email tài khoản, ID thiết bị, credential hay tài liệu riêng tư vào đây.

**Trạng thái công việc:** LOCAL_ANDROID_FOLDER_PRESENT / RAW_MESSAGES_NOT_OBSERVED_ON_CHECKED_PATHS / OTHER_SOURCE_CARRIERS_STILL_OPEN. Không đồng nhất thiết bị Android, mount Dropbox có tên ổ D, Google Drive hay Windows local. Không báo dữ liệu JINEY đã mất.

**Bước kiểm tra còn lại:** đọc từ đúng vật mang bytes của export JINEY hoặc ổ D vật lý/backup có checksum; lập index message-ID, timestamps, nguồn, độ tin cậy và đối chiếu mốc Canon. Không tự viết lời chat gốc từ tên folder.
