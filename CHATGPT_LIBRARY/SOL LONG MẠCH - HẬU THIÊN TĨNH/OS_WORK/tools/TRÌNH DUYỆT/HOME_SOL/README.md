# HOME_SOL — CỔNG NỐI MODULE TOÀN THIẾT BỊ THẬT

URL nội bộ sandbox: `http://127.0.0.1:8765/sandbox/sol`

URL API module thiết bị: `http://127.0.0.1:8765/api/devices`

Chỉ có hiệu lực trên máy Windows/WSL có dịch vụ HOME_SOL lắng nghe tại cổng 8765. Lưu liên kết trong ChatGPT Library không tự kích hoạt tiến trình trên DESKTOP-86ITNQ4. Không được làm một máy chủ khác chiếm cổng 8765. Địa chỉ loopback của ChatGPT/cloud không phải loopback Windows người dùng.

## Kiểm tra thực tế tại máy chủ

Tại thư mục lưu 2 tệp `home_sol_check.py`, `HOME_SOL_Sandbox.json`, dùng Python 3.10+:

```powershell
py home_sol_check.py devices
py home_sol_check.py sandbox
py home_sol_check.py open
```

`devices` phải trả ra `LIVE_LOCAL_GET_OK` kèm `disk_c.freeGB` và timestamp lấy trực tiếp từ API. Lệnh chỉ dùng GET; không sửa ổ, không chạy lệnh xóa hay tối ưu, không thay đổi server; không gửi thông tin xác thực đi xa.

## Mốc do người dùng cung cấp (chưa live)

2026-10-13T19:43:20.8155794+07:00: C: 474,36 GB tổng, 457,82 GB đã sử dụng, 16,54 GB còn trống (~3,49%). GPU MuMuPlayer Virtual Display Adapter v22.3.52.447 OK; NVIDIA GT 1030 OK.
