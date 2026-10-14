# HOSPOSIK — SOL Agent DNS / Memory / Router

Node.js >=24, SQLite WAL/FULL, DNS UDP và HTTP agent message bus.

## Local endpoints

- DNS `127.0.0.1:15353/udp`; zone `hosposik.test` (DNS thử nghiệm nội bộ).
- A `router.hosposik.test`, `memory.hosposik.test`, `agent.hosposik.test` -> 127.0.0.1.
- SRV `_agent._tcp.hosposik.test`, `_memory._tcp.hosposik.test` -> router.hosposik.test:8788.
- HTTP `127.0.0.1:8788` lắng nghe local-only.

## API

- `GET /health` trạng thái hoạt động.
- `POST /v1/agents/register` đăng ký, heartbeat tác nhân.
- `GET /v1/agents` xem trạng thái online 90 giây.
- `POST /v1/memory/events` ghi sự kiện; `GET /v1/memory/events?agent=sol&after=0` đọc lại.
- `GET /v1/memory/stream?agent=sol&after=0` nhận sự kiện mới qua SSE.
- `POST /v1/route` xếp hàng tin nhắn; `GET /v1/inbox?agent=router` nhận; `POST /v1/ack` xác nhận.

Trừ `/health`, yêu cầu `Authorization: Bearer <local agent token>`. Token sinh riêng ở `data/agent.token`; bộ nhớ SQLite trong `data/memory.sqlite`. Thư mục `data/`, `logs/` không commit.

## Cài đặt

```bash
npm ci
npm test
npm start
```

Termux (đã có termux-services):

```bash
sh termux/install-service.sh
sv status hosposik
```

Lệnh DNS:

```bash
dig @127.0.0.1 -p 15353 router.hosposik.test A
dig @127.0.0.1 -p 15353 _agent._tcp.hosposik.test SRV
curl http://127.0.0.1:8788/health
```

Service được runit giám sát khi Termux services chạy, nhưng không tự bảo đảm khởi chạy sau Android reboot nếu không có Termux:Boot hoặc cơ chế riêng.

## Phạm vi

HOSPOSIK hiện chỉ là tên dịch vụ nội bộ; không phải một tên miền Internet đã được xác thực hoặc cấu hình trên Hostinger. DNS port 15353 không thay DNS hệ thống port 53.
Bộ nhớ lưu những sự kiện mà agent thực sự gửi tới API; không tự lấy lịch sử ChatGPT. Để hoạt động liên thiết bị cần endpoint/tunnel HTTPS được xác thực, chưa cấu hình.