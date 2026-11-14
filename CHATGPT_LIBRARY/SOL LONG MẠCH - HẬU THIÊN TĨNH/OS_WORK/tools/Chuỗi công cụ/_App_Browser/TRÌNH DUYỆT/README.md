# TRÌNH DUYỆT — LOCAL DEVICE API

Đường dẫn URL **cho phép chính xác**: `http://127.0.0.1:8765/api/devices`.

- Công cụ chạy **trên chính DESKTOP-86ITNQ4** (Windows / máy chủ chạy API), không dùng localhost của ChatGPT cloud.
- Chế độ `probe` GET read-only và xác minh `schema=MINH_ALL_REAL_DEVICES_TOPOLOGY_V1` + `host=DESKTOP-86ITNQ4`. Không đăng nhập, không khởi động daemon, không ghi trạng thái.
- Chế độ `open` mở tab trong trình duyệt mặc định trên máy có chạy script; không chứng minh tab đã tải xong.
- `browser_config.json` chỉ có cấu hình, không có token, cookie, mật khẩu.
- Mã nguồn Chrome DevTools MCP có `http://127.0.0.1:8765/mcp`; nếu cùng cổng được dùng bởi API `/api/devices`, **không được khởi động hai server lắng nghe cổng 8765**. Tập lệnh này không bind cổng và không thay đổi `mcp.json`.

Chạy trên Windows/Ubuntu có Python 3.10+:

```shell
python trinh_duyet.py show-config
python trinh_duyet.py probe
python trinh_duyet.py open
```

Đọc `probe` tại máy chủ để có kết quả thực; bản tin topology do người dùng gửi ngày 2026-10-13 lúc 19:43:20+07:00 là **nguồn người dùng cung cấp**, không thay cho readback trực tiếp.
