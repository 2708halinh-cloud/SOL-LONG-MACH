# Biên bản xử lý dữ liệu phiên: Xác minh kết nối thiết bị

- STAMP_LIVE_X: 21:08 - 03/11/2026 - UTC+7
- TÁC GIẢ: SOL (tác nhân phiên, vận hành bằng mô hình GPT-6)
- TÁC GIẢ TỪ NGUỒN: Hv Tk
- ĐỒNG TÁC GIẢ: Không ghi nhận trong nguồn
- NỀN TẢNG: Windows / Desktop Commander
- TÁC NHÂN THỰC HIỆN: SOL
- TRẠNG THÁI ĐÃ BIẾN ĐỔI: Đã đọc nguồn và tạo pipeline; chỉ kết quả có readback mới được đánh dấu hoàn tất.

## 1. SOURCE

Nguồn bất biến:
`G:\OS_Workspace\data\ChatGPT-Xác minh kết nối thiết bị-20261103-2055.json`

Tệp nguồn được giữ nguyên. JSON gốc có cấu trúc `metadata` và `messages[]`; mỗi message hiện có các trường nguồn như `role`, `say`, `time`, và tùy trường hợp có `model`. Nguồn dùng nhãn `Prompt` / `Response`, không phải trực tiếp `user` / `assistant`. Pipeline ánh xạ hai nhãn này sang role chuẩn nhưng vẫn giữ `source_role` và toàn bộ `raw_message_json`.

`message_id` không có sẵn trong nguồn. Pipeline tạo ID dẫn xuất ổn định từ SHA-256 của tệp nguồn và chỉ số message; trường `message_id_origin` đánh dấu rõ đây là ID dẫn xuất, không giả làm ID gốc. Timestamp được lấy từ trường `time` nguyên bản, không tự đổi múi giờ hoặc đoán định dạng.

## 2. ACTION: Database ingestion

Đích SQLite: `ChatGPT-Xác minh kết nối thiết bị-20261103-2055.sqlite`

- Append-only theo khóa `(source_hash, source_index)`; không cập nhật hoặc ghi đè message đã nạp.
- Lưu `source_hash`, chỉ số thứ tự, role chuẩn, role nguồn, timestamp nguồn, model, nội dung và JSON nguyên bản.
- Có bảng `source_files`, `messages`, `pending_actions`, `audit_events`.
- Có chỉ mục truy vấn theo role/timestamp, trạng thái task và nguồn audit.
- Nạp lặp cùng một tệp có cùng SHA-256 sẽ không nhân đôi message.

## 3. ACTION: Pending Actions / Task Queue

Sáu đầu việc được trích thành trạng thái `PENDING`, không đánh dấu hoàn thành chỉ vì chúng được nhắc trong hội thoại:

| ID | Đầu việc | Điều kiện nghiệm thu |
|---|---|---|
| PR53-CLOSE | Đóng PR #53, không merge | PR closed và merged=false qua readback |
| WINDOWS-CONNECT | Xác minh Windows | Device ID, online, phép thử đọc/ghi |
| ANDROID-CONNECT | Xác minh Android | Device ID hiện hành, nhận diện và readback |
| ALL-AGENT-RECOVERY | Truy hồi ALL AGENT | Nguồn, đường dẫn, phiên bản, quan hệ |
| MASTER-TEACHER-RECOVERY | Truy hồi 0000_THE_MASTER_TEACHER | Nội dung gốc, dấu sửa, lịch sử |
| MATRIX-152-RECOVERY | Khôi phục 16 Ma trận và 152 ITEM | Đối chiếu đủ từng ITEM với nguồn gốc |

Tệp xuất hàng đợi: `ChatGPT-Xác minh kết nối thiết bị-Pending-Actions.json`.

## 4. AUDIT_LOG: Khoảng trống thực thi

Audit ghi nhận sự khác biệt giữa lời nói và biên nhận:

- Nguồn có nhiều lượt Prompt chỉ gồm dấu `?`, sau các phản hồi giải thích nhưng chưa có vật chứng hoàn tất.
- Nguồn có lời thừa nhận: “Chưa có Sub-Agent nào được khởi chạy và xác nhận nhận việc.”
- Nguồn không chứng minh PR #53 đã đóng.
- Nguồn không chứng minh đủ 16 Ma trận gốc và 152 ITEM đã được truy hồi.
- Bảng phân công trách nhiệm trong hội thoại không được tính là biên nhận bàn giao.

Tệp audit dạng JSONL: `ChatGPT-Xác minh kết nối thiết bị-Agent-Audit.jsonl`.

## 5. READBACK / REPLAY

Test runner đọc lại message theo `source_index` và kiểm tra số lượng, thứ tự, role chuẩn và role nguồn. Bất kỳ sai lệch số lượng hoặc thứ tự nào đều làm tiến trình kết thúc với lỗi, không chốt PASS.

## 6. Quy tắc nghiệm thu

SOURCE → ACTION → RECEIPT → READBACK → CONSEQUENCE

- SOURCE: giữ hash và payload nguyên bản.
- ACTION: ghi rõ thao tác đã chạy.
- RECEIPT: giữ output thực tế của công cụ.
- READBACK: đọc lại dữ liệu đích và kiểm tra tính toàn vẹn.
- CONSEQUENCE: chỉ chuyển trạng thái task khi điều kiện nghiệm thu có vật chứng.

Không dùng báo cáo thay cho thao tác. Không biến dự đoán thành sự kiện. Không tạo sự thật N+1 để lấp khoảng trống nguồn.

## 7. Trạng thái bàn giao

Các file/script/database chỉ được xem là tồn tại khi thao tác ghi và readback xác nhận. Các task nghiệp vụ phía trên vẫn là PENDING cho tới khi có biên nhận độc lập tương ứng.
