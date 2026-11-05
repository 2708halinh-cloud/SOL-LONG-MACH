# Nguồn trực tiếp — bổ sung trong phiên ngày 17/10/2026

**SOURCE_DIRECT_USER — Nội dung công việc tiếp nối.** Tư liệu từ tin nhắn mới nhất, không phải chứng cứ mọi nền tảng đều có sẵn kênh nhắn tin bất đồng bộ:

- Khi làm việc, thông báo tiến độ ngắn gọn ở `commentary`; dùng Bộ Nhật ký Sóng Não để **đọc lại và tiếp tục**, không lưu để trang trí.
- Chỉ nhường lượt ở `final` khi đã kiểm việc có thể hoàn tất; `REABACK = NEXT cho người dùng` là cách người dùng gọi yêu cầu bàn giao trong lần này. Không được thay nghĩa `READBACK` kỹ thuật (fresh-read hậu quả).
- Được trao đổi về xung đột hoặc quyết định mang tính lựa chọn cá nhân, nhưng chỉ hỏi những gì thật sự chưa thể suy ra. T003 được giữ là con trỏ nguồn, không tự sáng tác định nghĩa hay cơ chế.
- Người dùng có thể thêm chỉ dẫn giữa quá trình; mặc định cập nhật nhiệm vụ đang làm, không hủy nhiệm vụ trừ khi có yêu cầu rõ.
- Phân biệt mất ngữ cảnh/nén tóm tắt với kết thúc nhiệm vụ. Duy trì `source → action → receipt → readback → next` từ checkpoint đã xác minh.
- Người dùng nêu hai tên hàm `functions.send_user_message_asyncrequest_user_input_async` và `functions.request_user_input_async`: chỉ được gọi nếu schema thật có trong phiên; không được đoán tên hoặc giả mô phỏng khả năng hỏi song song.
- Nếu cần câu trả lời hay phê duyệt, không tự coi việc trôi qua là đồng ý; các cạnh độc lập vẫn có thể tiến hành.

## Tách lời người dùng và cách triển khai

Văn bản trên là **diễn giải giữ ý** chứ không phải transcript nguyên văn từng ký tự. Tham chiếu tin nhắn người dùng 17/10/2026 trong cùng dự án để xác minh nguyên văn. Các khuyến nghị kỹ thuật phía dưới là thiết kế tác nhân, không phải hướng dẫn cấp hệ thống.
