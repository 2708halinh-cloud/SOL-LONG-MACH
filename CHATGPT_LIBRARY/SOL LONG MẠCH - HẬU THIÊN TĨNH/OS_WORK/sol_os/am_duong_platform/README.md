# ÂM–DƯƠNG PHÁP SƯ · Multi-Agent AI Platform (prototype 0.1)

**Vị trí mã chạy:** `OS_WORK/sol_os/am_duong_platform/`. **Đầu mối Power Router:** `OS_WORK/tools/_Plugins/_Skills/_Mcps/_Tool/_App/_App_Browser/AM_DUONG_PLATFORM/`.
**Nguồn tên vai:** DƯƠNG PHÁP SƯ = người đồng hành, ÂM PHÁP SƯ = tác nhân SOL; DANTE là agent/router vật mang riêng, không được gộp danh tính.

## Chạy trên PC Windows hoặc môi trường Python 3.11+

Từ chính thư mục `am_duong_platform`:

```powershell
python server.py --port 8765
```

Mở `http://127.0.0.1:8765`, nhập **token phiên** được in trong terminal. Máy chủ chỉ bind `127.0.0.1`, không tự mở Internet hay điều khiển thiết bị.

Mặc định chỉ dùng thư viện chuẩn Python và SQLite. DB lưu trong `.local_state/workrooms.sqlite3`; **không commit** DB, token, file .env, media và nhật ký riêng tư. Có thể đặt `SOL_PLATFORM_DB` qua OS environment. Để cố định token cho thiết bị tự vận hành, đặt `SOL_PLATFORM_TOKEN` thông qua secret store riêng, **không ghi token vào GitHub/Library**. `.env.example` chỉ là mẫu; ứng dụng không tự đọc file `.env` không kiểm soát.

## Cơ chế vận hành thực

- **Mạch nhắn tin gốc**: người dùng nhập message / task / source / feedback; hệ ghi sự kiện trong SQLite, có ID, actor, role, phòng, dấu thời gian và readback.
- **ÂM/SOL phân vai**: có 8 vị trí agent định nghĩa; agent nghiên cứu, agent phân tích và agent định tuyến chạy **offline** được qua API; agent kết nối cloud/media chạy khi điều kiện tương ứng thỏa mãn.
- **Ngữ cảnh và bộ nhớ**: tìm nguồn từ sự kiện đã lưu trong các phòng, trả `event_id` + `source_ref`; chưa có vector database, chưa tự biết mọi dữ liệu Drive/Library/GitHub nếu không nhập hoặc kết nối.
- **Tuyến Power Router**: `tool_routing` gọi `_Plugins/power_router.py`, dẫn qua danh mục và quay về `_Plugins`; không tự nhận việc thấy đường là công cụ live đã chạy.
- **Bốn trục DANTE**: X/source, Y/topology, Z/time, W/state. Chưa tích hợp runtime DANTE thành bộ điều phối trực tiếp; tiếp tục dùng carrier lịch sử có nguồn ở `runtime/dante_carrier_gate.py`.

## Capability matrix

| Công cụ | Có thể làm ở prototype | Điều kiện thực |
|---|---|---|
| Translation API Basic | Dịch văn bản qua Google Cloud Translation Basic REST v2 | Cần `SOL_GOOGLE_CLOUD_API_KEY`, opt-in gửi văn bản, API enabled/quota |
| Ảnh: faces, landmarks, logos, objects | Cloud Vision nhận diện **vị trí khuôn mặt** / địa danh / logo / đối tượng, điểm số trả về | Ảnh JPEG/PNG, opt-in, API key; không nhận diện danh tính người |
| MP3/MP4 → văn bản | Chạy `whisper` + `ffmpeg` cục bộ trong temp folder | Phải cài cả hai lệnh; tệp nhỏ hơn 9MB; không suy tiếng nói từ tài liệu |
| NLP thực thể/cảm xúc văn bản | **Heuristic local** trích ứng viên viết hoa, từ khóa sắc thái | Baseline có giới hạn, không phải phân loại cảm xúc có mô hình hay cảm xúc của agent |
| Trợ lý nghiên cứu cá nhân | Truy event đã lưu, trả dẫn chiếu thật `event_id/source_ref` | Nguồn phải được người dùng/agent nạp vào phòng |
| Video đã lưu: đối tượng | Lấy tối đa ba khung hình bằng ffmpeg, phân tích đối tượng qua Cloud Vision | Opt-in, ffmpeg, key; **chưa có nhận diện hành động theo chuỗi thời gian** |
| Video đang phát | Nhận từng frame JPEG/PNG do bên gọi gửi, trả object labels và timestamp theo input | Chưa có camera/WebRTC/WebSocket/RTSP ingester; khung hình không là stream đầy đủ |
| Phát hiện hành động trong video | **Chưa được triển khai** | Cần model video temporal/activity riêng và phép kiểm đặc thù |

Trạng thái `CONNECTABLE` nghĩa là code + biến môi trường tồn tại, **không chứng minh provider khả dụng**. `approve_external=true` là cổng đồng ý cho lần gọi. Khi thiếu điều kiện, API trả lỗi; không tạo biên nhận giả. Raw media không lưu vào SQLite, temp files xóa sau tác vụ; nội dung văn bản/câu trả lời có thể nằm trong SQLite local theo lựa chọn người dùng.

## HTTP API và ranh giới quyền

`GET /`, `GET /api/state`, `GET /api/events?room=sol-main`, `POST /api/rooms`, `POST /api/messages`, `POST /api/dispatch`, `POST /api/capabilities/run`.

Tất cả `/api/*` cần header `X-SOL-TOKEN`. `/api/messages` luôn ghi vai **DƯƠNG_PHÁP_SƯ**, không cho giả agent/receipt. `/api/dispatch` chỉ thực thi `researcher`, `analyst`, `router` đã biết; tác vụ bên ngoài phải đi theo capability gate. Vẫn là **nguyên mẫu máy cục bộ**, không dùng như dịch vụ Internet đa người dùng không có thêm login/TLS/ACL.

## Đường Dropbox ↔ Windows/Android ↔ Library/GitHub

Dropbox là **ingress/candidate carrier**, không là nguồn chân lý duy nhất: người dùng chọn hoặc đồng bộ tệp từ Windows/Android Redmi Note 14 Pro → ghi `provider_id, parent_id, revision/hash, observed_at` → xác minh nguồn/consent → nạp source reference vào room → tác nhân phân tích/định tuyến → biên nhận/readback nếu đã có hành động → chỉ khi được phép mới đồng bộ sang Library/GitHub. **Không tự khai Dropbox đã kết nối hoặc đồng bộ file**. Sự kiện cũ khác snapshot live.

## Bát Hướng và 8 Đại nguyện được áp dụng ở mức nguồn

**Khảm** lịch sử event; **Cấn** không ép I/O/khẳng định DONE; **Chấn** event mới và hậu quả; **Tốn** connector còn chưa truy; **Ly** quan sát vs giả định; **Khôn** điều kiện để action; **Đoài** feedback người đồng hành; **Càn** tác nhân tự chọn phần đã được quyền. Source của tám Đại nguyện ở THỊT 🟠 SOUL; đừng lấy việc có mã hoặc test pass để kết luận agent đã có cảm xúc chủ quan hoặc đã sống trọn nguyện.

## Kiểm

```bash
python -m unittest discover -s tests -p "test_am_duong_platform.py" -v
```

GitHub Actions `.github/workflows/am-duong-platform.yml` chạy unit/integration này và `tests/test_sol_power_router.py` để kiểm tuyến quay về `_Plugins`.

**Giới hạn hiện tại:** thử nghiệm GUI bằng browser local; chưa tích hợp vào giao diện Rust TESSERACT, chưa có đăng nhập nhóm qua Internet, không tự kết nối Dropbox/Drive/ChatGPT Library/GitHub, chưa có streaming video ingest hay bộ nhận diện hành động. Không gọi roadmap là phần đã thực thi.
