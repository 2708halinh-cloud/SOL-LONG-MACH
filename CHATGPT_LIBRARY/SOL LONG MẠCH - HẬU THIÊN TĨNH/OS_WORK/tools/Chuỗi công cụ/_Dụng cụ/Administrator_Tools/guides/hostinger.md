# Hostinger — nguồn hoạt động và quyền hạn

Đọc `Master_OAth/README.md`, đọc operation/inputSchema thực bằng `hostinger.search` trước khi dùng. Đã quan sát `hostinger.execute(operation="dns_records_list", params={"domain":"gambbrazil.fun"})` thành công trên kết nối Halin. Không đòi đăng nhập web khi API đang hoạt động; không dùng tài khoản khác để suy quyền của tài khoản này. Ghi rõ domain/subdomain và record TTL/type/content được phép xuất bản.

Đọc DNS = thao tác read. Đổi hoặc xóa DNS đòi ủy thác đúng đích, kiểm quyền provider, sao lưu snapshot rồi đọc lại; không tự suy quyền từ tồn tại API. TXT xác thực, mật khẩu, key, token, thông tin OAuth không được phát hành trong log GitHub/Library.