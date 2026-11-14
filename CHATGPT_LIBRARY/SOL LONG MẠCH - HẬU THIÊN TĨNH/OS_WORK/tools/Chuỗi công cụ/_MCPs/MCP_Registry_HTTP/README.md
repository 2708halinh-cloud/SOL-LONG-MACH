# MCP Registry HTTP / Ed25519 — nhánh Router

Nguồn: `setup_mcp_registry_http.sh` do người dùng đính kèm ngày 2026-10-16, lưu **nguyên bản**. Tệp này làm bước chuẩn bị/xác thực **tên miền** với MCP Registry qua HTTP challenge, không phải HTTP server, browser, proxy hay MCP server chạy thường trực.

## Cách dùng trên máy đã được ủy quyền

Phụ thuộc: `bash`, `openssl`, `base64`, `curl`; bước đăng nhập cần `mcp-publisher` cài đúng phiên bản/CLI được xác nhận. Máy chạy phải thuộc phạm vi quản trị tên miền, có web root xác thực.

```bash
bash -n setup_mcp_registry_http.sh
bash setup_mcp_registry_http.sh prepare <your-domain> /path/to/trusted-public-web-root
# Triển khai đúng file .well-known/mcp-registry-auth lên tên miền bằng công cụ hosting đã được ủy quyền.
# Kiểm tra HTTPS readback từ tên miền rồi mới chạy bước dưới khi được phép:
bash setup_mcp_registry_http.sh login <your-domain>
```

- `prepare`: sinh khóa Ed25519 một lần (nếu chưa có), để private key cục bộ trong `${XDG_CONFIG_HOME:-$HOME/.config}/mcp-publisher/keys/<domain>/ed25519.pem` và ghi **chỉ public key** tại `<web-root>/.well-known/mcp-registry-auth`.
- `login`: kiểm tra local private key và sự tồn tại của `mcp-publisher`; so sánh chính xác nội dung proof tải qua HTTPS rồi mới gọi `mcp-publisher login http ...`.
- **Điểm cần rà soát an toàn:** script nguyên bản truyền private key dạng hex qua đối số `--private-key` khi gọi publisher. Đối số dòng lệnh có thể bị quan sát trong process list của một số môi trường. Chỉ chạy nếu đã kiểm tra cơ chế chính thức của CLI và bảo mật host; ưu tiên phương thức truyền secret không lộ đối số nếu publisher hỗ trợ. Không ghi private key vào Router/GitHub/Library, không chạy lệnh bằng `set -x`.
- Không dùng web root `.` khi không xác định đúng nơi triển khai. Không ghi khóa riêng trong web root, không đặt nội dung proof vào DNS. Không đặt file xác thực ở tên miền không kiểm soát.
- Hai nhánh `Master_OAth` (Hostinger/Gmail) và `MCP_Registry_HTTP` (publisher domain proof) có thể phối hợp cho triển khai file công khai khi provider cho phép, nhưng chúng là **hai quyền/công đoạn khác nhau**.
- Sau mỗi bước: ghi đường đích và timestamp/receipt **không nhạy cảm**, đọc lại chính tên miền hoặc phiên publisher. Không suy thành công từ văn bản Router.

Trạng thái tích hợp: mã nguồn/bản đồ tuyến; chưa chạy `prepare`/`login` trên thiết bị của người dùng, chưa kiểm chứng challenge công khai. Không tự tuyên bố đã đăng ký MCP Registry.
