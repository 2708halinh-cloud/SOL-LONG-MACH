# SOL — Thu thập Chrome Network / Server-Timing (14/10/2026)

## Mục đích

Thay cho việc gửi từng bản ghi GET, thu gom thông tin Network từ Chrome thành một tệp HAR, rồi xử lý tập trung bằng `SOL_CHROME_HAR_INGEST.py`. Công cụ chạy **ngoại tuyến**, dùng Python tiêu chuẩn, không có chức năng truy cập Chrome hoặc gửi dữ liệu ra Internet.

## Thu thập trên Chrome Windows

1. Mở trang đang phân tích (`chrome://settings/content/siteDetails?site=https%3A%2F%2Fdeveloper.chrome.com%2F`).
2. Mở DevTools (F12), chọn **Network**. Bật **Preserve log** nếu muốn giữ yêu cầu qua các lần tải lại; tải lại trang nếu cần chụp toàn bộ yêu cầu.
3. Chọn **Export HAR (sanitized)** (không chọn biến thể **with sensitive data**). Lưu HAR trên máy người dùng, trong thư mục được quản lý cục bộ.
4. Trên Windows có Python: `py -3 SOL_CHROME_HAR_INGEST.py "C:\\path\\to\\network.har" --chrome-only --out "C:\\path\\to\\SOL_CHROME_RECEIPTS"`.
   Trên Termux/Linux: `python3 SOL_CHROME_HAR_INGEST.py network.har --chrome-only --out ./SOL_CHROME_RECEIPTS`.
5. Đọc `SUMMARY.json` và `NETWORK_RECEIPTS.jsonl`. Đối chiếu bằng `input_sha256`; giữ HAR gốc để truy nguyên. **Chỉ chuyển báo cáo đã lọc** sang các vật mang khác sau khi kiểm tra.

**Giới hạn:** Việc Chrome DevTools có hiển thị/đưa vào HAR đầy đủ các tài nguyên `chrome://` phụ thuộc phiên và môi trường; không được suy ra nội dung JS/CSS từ trạng thái `200 OK`. HAR đã lọc thường vẫn chứa URL có thể nhạy cảm; chương trình ẩn các tham số token/auth/password theo tên nhưng không bảo đảm loại bỏ toàn bộ bí mật khỏi URL tùy biến. Người dùng kiểm tra báo cáo trước khi chia sẻ. Công cụ không sao chép body/JS/CSS của response.

## Server-Timing — điểm cần phân biệt

- `Server-Timing` là **response header tùy chọn**, không xuất hiện chỉ vì `GET 200 OK`.
- Trình duyệt có thể hiển thị các chỉ số như `db;dur=53`, `app;dur=47.2` bằng `PerformanceResourceTiming.serverTiming` / `PerformanceNavigationTiming.serverTiming` hoặc `PerformanceObserver`.
- Tài nguyên `chrome://resources/...` là tài nguyên nội bộ trình duyệt, không tương đương request HTTPS đến máy chủ. Không suy đoán timing của máy chủ từ các bản ghi Chrome Settings đã cung cấp.
- Cần chú ý giới hạn cùng nguồn/cross-origin; `Timing-Allow-Origin` hỗ trợ cấp quyền đọc timing giữa các nguồn, và một số API đòi hỏi secure context.

## Xuất xứ tài liệu

- **Người dùng (SOURCE_DIRECT)**: bản ghi GET `chrome://resources/mojo/mojo/public/js/bindings.js` ngày 14/10/2026; bản ghi có response `200 OK`, `content-type: text/javascript`, CSP, `origin: chrome://settings`, Chrome 154 Windows. Đã lưu tệp riêng.
- **Nguồn ngoài, đã đọc (RESEARCH)**: https://web.dev/articles/custom-metrics#server-timing-api và https://developer.mozilla.org/fr/docs/Web/API/PerformanceServerTiming
- **Hướng dẫn HAR chính thức**: https://developer.chrome.com/docs/devtools/network/reference#save-all-network-requests-to-a-har-file

## Nguồn Dropbox liên quan

`/SOL LONG MẠCH - HẬU THIÊN TĨNH/lazy_load.js` (Dropbox, 1.324.505 byte); đã sao chép đúng byte và kiểm tra Dropbox content_hash trên Redmi tại `/storage/emulated/0/SOL-LONG-MACH/OS_Workspace/tools/TRÌNH DUYỆT/lazy_load.js`. Chưa đối chiếu được tệp riêng `images/privacy_guide` trong Dropbox, không tạo byte suy đoán.

## Quy tắc lưu

**SOURCE_DIRECT** giữ nguyên bản ghi; **RESEARCH** tách khỏi quan sát thực tế; **OPEN** cho mục chưa thể xác minh. Không xoá HAR gốc. Không tự thu cookie, token, body response, hoặc upload log nhạy cảm.
