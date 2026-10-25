# HOSPOSIK — Hostinger DNS binding

**Tên miền xác nhận:** `gambbrazil.gambbrazil.fun`.
**Zone Hostinger:** `gambbrazil.fun`.

## Đã xuất bản và đọc lại

| Owner trong zone | Type | TTL | Nội dung / mục đích |
|---|---|---:|---|
| `gambbrazil` | TXT | 3600 | `v=HOSPOSIK1; service=agent-dns-memory-router; scope=local; public_endpoint=pending` |
| `_hosposik.gambbrazil` | TXT | 300 | `v=HOSPOSIK1; role=agent-dns-memory-router; scope=local; zone=hosposik.test; public_endpoint=pending` |

Bản ghi SPF, MX, DMARC, DKIM của `gambbrazil.gambbrazil.fun` giữ nguyên khi so sánh qua Hostinger sau cập nhật. Các thay đổi đều dùng thao tác thêm bản ghi, `overwrite=false`.

## Runtime local còn giữ nguyên

- Local DNS: `hosposik.test`, UDP `127.0.0.1:15353`.
- Local HTTP agent memory/router: `http://127.0.0.1:8788`.
- Agent memory: SQLite WAL/FULL trên Termux; chương trình agent phải gọi API để ghi.

## Chưa có tuyến public

TXT là bản ghi định danh/discovery, không phải địa chỉ dịch vụ công khai. Chưa có public A/AAAA/CNAME, reverse proxy HTTPS hay tunnel tương ứng với endpoint HOSPOSIK. Cũng chưa có Hostinger VPS trong tài khoản Primary. Không trỏ FQDN tới `127.0.0.1`, không làm gián đoạn MX/TXT đang dùng.

Khi có HTTPS origin thực sự, mới gán bản ghi DNS trỏ tới origin đó và xác nhận TLS, kết nối và health response từ bên ngoài. `config/domain_binding.json` là bản ánh xạ cấu hình, chưa tự nạp vào Termux (thiết bị hiện offline).
