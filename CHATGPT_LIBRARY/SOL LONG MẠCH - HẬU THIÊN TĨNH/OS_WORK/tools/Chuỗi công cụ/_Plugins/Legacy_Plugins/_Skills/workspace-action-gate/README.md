# Workspace Action Gate — cấu hình OS_WORK

- Trạng thái plugin: đã đọc hướng dẫn Skill đang cài; Google Drive search trả phản hồi từ connector thực.
- Đã xác minh **đúng tên** tệp OAuth do người dùng nêu ở ROOT của `SOL LONG MẠCH - HẬU THIÊN TĨNH`. Đây là tài liệu nhạy cảm: chỉ ghi **đường dẫn tham chiếu**, không sao chép hoặc đọc khóa vào Skill.
- Sự hiện diện tệp **không chứng minh** Google đã liên kết OAuth bằng client này: trạng thái `SOURCE_PRESENT_AUTH_UNBOUND`.
- Không trộn client OAuth khác, không ghi `client_secret`, `refresh_token`, `access_token` vào Library/config/log.
- Khi chạy trong Workspace: dùng các connector Google đã kết nối; kiểm tra scope và receipts bằng provider tools trước khi kết luận kết nối mới đã được thực hiện.

Chạy `python3 scripts/healthcheck.py config.json` để kiểm tra file cấu hình. Đây không phải phép thử xác thực Google.
