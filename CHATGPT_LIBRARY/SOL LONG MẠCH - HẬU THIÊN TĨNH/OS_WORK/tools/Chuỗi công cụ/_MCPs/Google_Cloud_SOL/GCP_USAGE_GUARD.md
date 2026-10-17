# Google Cloud SOL — Giám sát yêu cầu lỗi / Chi phí / Chặn thử lại

**Vị trí trong Tools hiện hữu:** `OS_WORK/tools/Chuỗi công cụ/_MCPs/Google_Cloud_SOL/`.
**Mã chạy:** `gcp_usage_guard.py` (Python 3, chỉ thư viện chuẩn).

## Quy tắc bảo vệ tài nguyên

1. Nạp số liệu **đã xuất** từ Google Cloud Monitoring / API Dashboard, không chủ động gọi Compute Engine, Cloud Storage hay App Hub.
2. Với API có `error_percent = 100` và `requests > 0`, phát `STOP_AUTOMATIC_RETRY_INVESTIGATE_ERRORS` để **ngăn tác nhân lặp lại yêu cầu lỗi**. Lỗi >50% kích hoạt trạng thái tạm dừng tương tự; không tự thay đổi tài nguyên hay tắt API.
3. Dấu `—` là **không có số liệu**, không phải `0` hay `0%`.
4. `estimated_failed_requests` được suy ra từ bảng tổng hợp; không phải nhật ký HTTP từng request. Không khẳng định bên gọi, mã lỗi, số tiền đã tính hoặc nguyên nhân lỗi nếu không có Cloud Audit Logs / Cloud Billing làm chứng.
5. Không bật VM, bucket, billing, dịch vụ API, không tạo credential, không tự gọi lại request thất bại. Giữ secrets ngoài logs và kho công khai.
6. Không sử dụng Windows đang được người đồng hành báo chặn OpenAI/ChatGPT làm điều kiện bắt buộc; công cụ có thể chạy trên host Python **được phép và đã xác minh**, không biến ví dụ môi trường thành trạng thái thực thi.

## Đầu vào JSON/CSV

`python3 gcp_usage_guard.py --input metrics.json` hoặc đọc dữ liệu qua `--input -`.

JSON nhận đối tượng `{ "metrics": [{ "api": "Compute Engine API", "requests": 49, "error_percent": 100, "average_latency_ms": 36, "p95_latency_ms": 77 }] }` hay mảng trực tiếp. CSV chấp nhận cột Tiếng Việt `Tên`, `Yêu cầu`, `Lỗi (%)`, `Độ trễ trung bình (ms)`, `Độ trễ ở phân vị thứ 95 (ms)`.

Trong dữ kiện người đồng hành cung cấp: Compute Engine 49/49 lỗi, Cloud Storage API 4/4 lỗi, App Hub 15/15 không lỗi → **53 yêu cầu có lỗi trên tổng 68 yêu cầu quan sát được**. Đó là phân tích dữ liệu được cung cấp, **không phải chi phí thực tế** và không xác định tác nhân gửi.

## Trạng thái khi lưu nguồn

`SOURCE_IMPLEMENTED` = đã có mã phân tích ngoại tuyến trong Tools. `PROVIDER_CALLS=0` = trình phân tích không gọi Google Cloud. `CLOUD_LOGS_NOT_READ`, `BILLING_NOT_READ`, `LIVE_RUNTIME_NOT_VERIFIED`. Không gọi là MCP đã đăng ký trong ChatGPT hoặc đang chạy trên Computer. Trong repo GitHub các nguồn mã chạy và Library là **hai carrier độc lập**; phải đọc lại sau mọi đồng bộ thực tế.
