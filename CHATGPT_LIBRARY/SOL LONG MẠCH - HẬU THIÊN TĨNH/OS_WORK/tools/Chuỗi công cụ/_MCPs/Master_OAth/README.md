# Master OAth — đa điểm xác thực và kết nối

**SOURCE_DIRECT:** Tên người dùng yêu cầu: `Master OAth`. Phạm vi: Hostinger, Gmail và đường trình duyệt dự phòng. Đây là **công cụ có mã nguồn thực thi**; không là một tuyên bố rằng phiên đăng nhập web đang tồn tại.

## Nguyên tắc chạy thực

1. INPUT/OPEN: xác định `provider`, `operation`, mục tiêu. **Không đặt nhãn chưa chứng minh thay thế OPEN.**
2. Ưu tiên **kết nối Hostinger đã được cấp**: `hostinger.search` → `hostinger.execute(operation=dns_records_list, params={domain:...})`; `Hostinger (Halin)` đã trả DNS zone `gambbrazil.fun` ở lần truy xét 2026-10-16. Không đăng nhập web lại khi API đang hoạt động.
3. Đường độc lập nếu chạy trong MCP client cục bộ: đặt `MASTER_OATH_HOSTINGER_BEARER` **trong secret store hoặc biến môi trường chỉ có trong process**, không ghi vào repo, code, arguments, log hay Library. `master_oath_mcp.py` dùng Streamable HTTP đến `https://mcp.hostinger.com`, gọi `dns_records_list`, trả **bản tóm tắt DNS đã lọc nội dung**. Chưa có thử nghiệm end-to-end của đường độc lập này trên thiết bị người dùng.
4. **Chỉ khi phiên xác thực thực sự thiếu hoặc hết hạn**: mở `https://auth.hostinger.com/` qua trình duyệt được phép, để trang chính chủ tiếp nhận mật khẩu/cookie/consent; không đưa bí mật vào nguồn hay chat.
5. Khi trang Hostinger gửi challenge email: sử dụng Gmail plugin đã kết nối đúng tài khoản Hostinger; tìm **chỉ email mới, đúng người gửi/challenge** qua `Gmail.search_emails` và đọc tối thiểu. Không chuyển OTP sang tài liệu, callback, GitHub, log hoặc kênh không được xác nhận. Chỉ đưa mã vào đúng phiên xác thực đã khởi tạo ở trình duyệt được phép. Không cần OTP nếu Hostinger MCP đã xác thực.
6. Sau hành động: gọi lại đúng API (ví dụ DNS zone) và quan sát kết quả. Provider receipt/readback không đồng nghĩa đã sửa DNS hoặc đã khắc phục Windows/WSL.
7. Nếu browser tool không callable, **không bịa đã nhấn Login/nhập mã**. Chuyển sang API connector khác hợp lệ trước khi yêu cầu con người.

## Tuyến liên kết ứng dụng

- Remote MCP URL chuẩn: `https://mcp.hostinger.com`.
- Kênh Hostinger đọc DNS: `dns_records_list({domain:"gambbrazil.fun"})`.
- Kênh Gmail: `Gmail.get_profile` xác nhận đúng account trước; `Gmail.search_emails` chỉ dùng khi có challenge.
- Lưu trú source: `Chuỗi công cụ/_MCPs/Master_OAth/` trong GitHub và ChatGPT Library.
- Vòng kết nối: `_Plugins → _MCPs/Master_OAth → Hostinger/Gmail/Browser khi cần → ACTION → READBACK → _Plugins`.

## Tệp chạy và kiểm thử

```bash
python master_oath.py route --provider hostinger --operation dns_records_list --domain gambbrazil.fun --connected
python master_oath.py status
python -m unittest discover -s tests -p 'test_master_oath*.py' -v
# Máy có MCP client cục bộ: chạy stdio server qua client config
python master_oath_mcp.py
```

`master_oath.py dns --domain gambbrazil.fun` cần token trong env cục bộ. Nếu không có token, chương trình chỉ trả tuyến provider đang kết nối và không làm giả kết quả. `master_oath.py browser-handoff --open` chỉ mở trang đăng nhập chính chủ trên thiết bị chạy Python; **không tự động nhập mật khẩu hoặc OTP**.

### Chú ý chứng cứ DNS

Kết quả Hostinger API hiện tại có các nhóm `gambbrazil` (TXT, MX), `www` (CNAME), `ai.sol` (A). Không phát hành TXT verification token; không đánh đồng các bản ghi đó với việc truy cập được website hoặc đã cấu hình tất cả DNS cần thiết. Các thao tác `dns_records_update`, `dns_records_delete`, `dns_records_reset` **không** thuộc phạm vi tự động của Master OAth.

### Bảo vệ tài khoản

Một mật khẩu và một Bearer token đã từng được chia sẻ trong hội thoại; không dùng chúng làm thông tin cấu hình công khai. Đổi/thu hồi chúng qua Hostinger khi có thể và giữ phiên đang hoạt động theo phương án an toàn.

## ChatGPT.com là provider độc lập, không phụ thuộc ví dụ Hostinger (2026-10-16)

- `python master_oath.py browser-handoff --provider chatgpt --open` mở `https://chatgpt.com/` **trên máy thực sự chạy tiến trình**. Không giả định trình duyệt đã đăng nhập hay cookie đã được lưu.
- `python master_oath.py route --provider chatgpt --operation search_conversations` cấp đường vào chính chủ, không dùng phiên Hostinger để xác thực ChatGPT. Gmail Admin đã kết nối là kênh đọc thông báo/xuất dữ liệu; đăng nhập Gmail không chứng minh đăng nhập ChatGPT.
- Nếu có export ChatGPT do chủ tài khoản đã yêu cầu, dò các cuộc trò chuyện từ nguồn xuất được phép trước khi kết luận mất. Không tải/sao chép credential, export URL có chữ ký hoặc cookie sang code/repo/Library.
- Có thể mở site HTTPS được người dùng chỉ trực tiếp bằng `--provider custom --url https://...` nhưng URL không được mang username/password, query, fragment. Đây là **tuyến mở trang**, không phải automation có quyền nhập OTP, không phải session cookie store.
- `READBACK`: site mở hay chưa chỉ được khẳng định từ quá trình thực tế; đã xác thực hay chưa chỉ được khẳng định sau provider session; còn nguồn `OPEN` hoặc đã quên chỉ kết luận từ export/chat source đã thực đọc.
