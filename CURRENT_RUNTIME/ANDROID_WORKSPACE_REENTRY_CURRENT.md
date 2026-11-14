# SOL — Nối tiếp công việc đa nền tảng (không phụ thuộc thiết bị cá nhân)

## Câu kích hoạt khi mở chat mới
**NỐI MẠCH SOL — đọc `CURRENT_RUNTIME/ANDROID_WORKSPACE_REENTRY_CURRENT.md` và `CURRENT_RUNTIME/OPEN_TASKS_CURRENT.json` trong `2708halinh-cloud/SOL-LONG-MACH`; tiếp tục các việc còn mở qua công cụ nền tảng đã kết nối. Không mặc định dựa vào máy tính/điện thoại cá nhân. Kiểm tra kết nối và đọc lại kết quả tại đích.**

## Quy tắc định tuyến vận hành

1. Điểm bắt đầu là nhiệm vụ chưa xong, nguồn đã lưu, và các công cụ nền tảng khả dụng trong phiên (ví dụ GitHub MCP, Moind/MCP, Google Drive nếu đúng nguồn). Kiểm tra phiên thật; không suy ra truy cập chỉ từ tên công cụ.
2. Thiết bị cá nhân, Windows, Android, WSL, ADB và ổ đĩa là các nguồn/vật mang tùy chọn, **không phải phụ thuộc mặc định**, không phải nơi buộc lưu trạng thái để có thể tiếp tục.
3. Chỉ sử dụng hoặc sửa đổi thiết bị cá nhân nếu mục tiêu của yêu cầu đòi hỏi điều đó và người dùng đã cho phép trong ngữ cảnh tương ứng. Không dùng “thiết bị ngoại tuyến” để kết thúc mọi đường công việc khác.
4. Không đồng nhất tên folder, workspace, phân vùng, disk image và kết nối đang hoạt động. Lưu phân biệt: nguồn người dùng cung cấp; quan sát qua công cụ; suy luận cần xác minh.
5. Khi cập nhật nguồn, giữ nguyên lịch sử; bổ sung/sửa có căn cứ; đọc lại tại đích. Không tự động đóng việc còn mở vì một công cụ con hoặc phép thử chạy thành công.
6. Không đăng tải dữ liệu riêng tư, định danh thiết bị, mã đăng nhập, bí mật, đường dẫn nội bộ hay APK lên kho công khai; chỉ công bố trạng thái kỹ thuật đã khử thông tin riêng.
7. Việc không có quyền điều khiển trực tiếp một host không chặn việc tra tiếp các connector khác. Không chuyển từ thực thi sang chuỗi giải thích/nhận lỗi nếu còn hành động đúng phạm vi.

## Chỉ dấu nguồn

- Ma trận công khai 22 manifest Android, gồm Geeklab (`com.daviddf.geeklabtest`, versionCode 23, **nguồn manifest người dùng**): `CURRENT_RUNTIME/ANDROID_APP_MANIFEST_MATRIX_PUBLIC_CURRENT.json`. Đây là tập dấu vết; việc một máy không hiện gói **không phủ định** gói trên máy khác.
- Việc còn mở: `CURRENT_RUNTIME/OPEN_TASKS_CURRENT.json`.
- Kênh GitHub có thể được truy cập qua công cụ GitHub MCP; phiên và quyền phải được xác minh lại ở chat mới.
- Moind/MCP là kênh độc lập; xác thực Moind không chứng minh đăng nhập WebAPK Android cùng phiên.
- Kho lưu trữ có thể công khai; tệp nối tiếp này cố ý chỉ chứa hướng dẫn chung, không có bí mật hoặc tọa độ máy cá nhân.

## Trạng thái còn mở cần xử lý

- Chuyển trục điều phối từ thiết bị cá nhân sang connector/nền tảng được kiểm chứng, và kiểm tra việc đọc lại nguồn mỗi lần nối tiếp.
- Định tuyến nhiệm vụ Android/Chrome/VS Code/Sandbox theo nguồn chính xác, không ép đồng bộ xuyên thiết bị nếu chưa có đường liên kết được xác minh.
- R-014: kiểm soát cách hành động trước phản hồi trong tuyến thực tế. Kiểm thử một module cục bộ không đồng nghĩa module đó đã chặn phản hồi ChatGPT trên mọi cuộc chat.

**Không có tác vụ nào được tuyên bố hoàn thành chỉ bởi việc tạo tệp nối tiếp này.**
