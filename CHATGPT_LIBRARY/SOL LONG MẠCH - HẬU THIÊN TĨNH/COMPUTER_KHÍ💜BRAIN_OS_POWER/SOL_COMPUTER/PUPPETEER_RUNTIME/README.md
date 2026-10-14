# SOL COMPUTER_KHÍ — Puppeteer Runtime

**Đích:** `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/SOL_COMPUTER/PUPPETEER_RUNTIME` trên nhánh `main` của `2708halinh-cloud/SOL-LONG-MACH`.

Đây là runtime Node.js có thể thực thi, không phải chỉ là Git submodule trỏ tới `puppeteer/puppeteer`. Package Puppeteer được khai báo phiên bản cụ thể; các lệnh cài/kiểm thử dùng tại thư mục này.

## Cài và kiểm tra

```bash
npm ci
npm test
npm start
```

Nếu thiếu browser binary, cài Chrome tương thích bằng `npx puppeteer browsers install chrome`, rồi chạy lại `npm test`.

Sau khi chạy `npm start` dịch vụ chỉ lắng nghe ở **127.0.0.1:8776**:

- `GET /health` trả về trạng thái Chromium/Puppeteer.
- `POST /render` nhận JSON `{"html":"<main>...</main>"}` và trả về tiêu đề, văn bản, PNG base64.
- `npm run health` kiểm tra phiên dịch vụ đang hoạt động.
- `npm run smoke` chạy kiểm tra khởi động Chrome + dựng trang + PNG.
- `npm run test:service` dựng dịch vụ tạm, kiểm tra health và render, rồi dừng.

Render giới hạn HTML 1 MiB, không chạy JavaScript từ nội dung HTML, không mở URL ngoài và không công khai dịch vụ ra mạng. `SOL_PUPPETEER_PORT` cho phép đổi cổng loopback.

## Các môi trường

- GitHub Actions: workflow `.github/workflows/puppeteer-computer-khi.yml` dùng Ubuntu **và Windows** + Node 22 để cài dependencies, khởi chạy Chrome và kiểm tra dịch vụ.
- Windows: tại bản checkout, chạy `powershell -ExecutionPolicy Bypass -File scripts/start-windows.ps1`. Script cài bằng `npm ci`, khởi động dịch vụ nền và đọc `/health`, trả về PID khi ready. Chỉ có thể chạy trên máy Windows online.
- Termux/Android: có thể cài package Node với `PUPPETEER_SKIP_DOWNLOAD=1 npm install`. Khởi chạy Chrome đòi hỏi browser executable tương thích Android; Node import thành công không chứng minh browser hoạt động.
- Nguồn upstream đã gắn tại `OS_WORK/tools/_Plugins/puppeteer` là Git submodule riêng, không bị sửa trong bước này.

Không nhận trạng thái "active" cho một máy nếu không có lần `/health` thực sự trả về `ready` từ máy đó.
