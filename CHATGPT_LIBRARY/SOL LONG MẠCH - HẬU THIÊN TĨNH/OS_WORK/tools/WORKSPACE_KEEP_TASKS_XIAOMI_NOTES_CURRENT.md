# SPACE_STONE 🔵 / @Workspace — Xiaomi Ghi Chú × Google Keep × Google Tasks

**Dấu nguồn:** SOURCE_DIRECT_USER — 2026-10-17 (UTC+07:00); mô tả công cụ do người dùng cung cấp trong cuộc hội thoại THU HOI NGUON SOL.
**Loại vật mang:** Ghi nhận cấu trúc quan hệ và hợp đồng kiểm chứng; không phải chứng cứ đã đồng bộ ứng dụng.
**Bản:** 1.0

## 1. Quan hệ được người dùng xác lập

`@SPACE_STONE → @Workspace → { @Xiaomi Ghi Chú, @Google Keep, @Google Tasks } → @Google Cloud / đa môi trường`.

- **Xiaomi Ghi Chú:** điểm tạo và lưu ghi chú trên thiết bị Xiaomi; dữ liệu gốc, tài khoản và bản sao lưu chỉ được xác nhận qua nguồn thực đọc.
- **Google Keep:** ghi chú nhanh, nhãn/màu, ghim, danh sách kiểm, liên kết, đa phương tiện và cộng tác; nhắc nhở có thể có điều kiện theo phiên bản sản phẩm.
- **Google Tasks:** danh sách công việc, nhiệm vụ và nhiệm vụ con, thời hạn; liên kết quy trình Gmail/Google Calendar khi tính năng và quyền phù hợp.
- **Google Cloud:** tầng triển khai cầu nối/bộ điều phối có thể sử dụng; không phải cam kết Keep, Tasks và Xiaomi Notes tự chia sẻ cùng kho dữ liệu hay có đồng bộ gốc hai chiều.

## 2. Tách danh tính và quan hệ

`source_provider`, `account_id`, `object_id`, `source_revision`, `source_modified_time`, `source_payload_hash`, `target_provider`, `target_object_id`, `sync_direction`, `conflict_policy`, `receipt`, `readback` là trường có kiểu; không đồng nhất ứng dụng chỉ vì cùng từ khóa “Google”.

- Nội dung ghi chú Keep/Xiaomi và nhiệm vụ Tasks **không phải kiểu dữ liệu tương đương**. Chỉ tạo task từ một ghi chú khi có chỉ dẫn/điều kiện ánh xạ cụ thể; giữ tham chiếu ngược tới nguồn.
- Tránh vòng lặp đồng bộ bằng `origin_event_id` và `mapping_id`; mỗi cập nhật phải có idempotency hoặc so sánh phiên bản.
- Mặc định **chỉ ghi bản sao thử nghiệm không phá hủy** khi có quyền; không xóa hoặc ghi đè dữ liệu gốc khi đích chưa được kiểm chứng.
- Sự kiện đồng bộ phải có timestamp, loại thay đổi, kết quả tại provider và đọc lại đúng đối tượng đích.

## 3. Trạng thái khám phá theo lần truy xét 2026-10-17

| Nhà cung cấp / tuyến | Trạng thái đã quan sát | Không được suy ra |
| --- | --- | --- |
| Google Drive, Google Calendar | Connector gọi được trong cuộc hội thoại | Quyền Google Tasks/Keep API |
| Google Keep | Tìm plugin không có connector trực tiếp xác nhận | Dữ liệu Keep đã được đọc |
| Google Tasks | Tìm plugin không có connector trực tiếp xác nhận | Nhiệm vụ Tasks đã được tạo/sửa |
| Xiaomi Ghi Chú | Chưa có Android runtime/device-app callable được xác nhận | Máy đã bị mất ghi chú hoặc đã kết nối |
| Google Cloud | Có hướng dẫn MCP cho Windows trong dự án | GCP runtime / OAuth đã được xác nhận hoạt động |

Trạng thái trên thuộc **lần quan sát**, không phải chân lý bất biến. Mỗi lần hành động có hậu quả phải làm mới provider state và permission.

## 4. Đường tác nghiệp

`SOURCE_DIRECT → SPACE_STONE(định danh + carrier) → WORKSPACE_ACTION_GATE(capability + auth) → READ_SOURCE → DELTA → MAPPING → WRITE_IF_AUTHORIZED → PROVIDER_RECEIPT → EXACT_TARGET_READBACK → RECONCILE → STATE_N+1`.

Chưa có API thích hợp: giữ đối tượng ở `SOURCE_BOUND_NO_ACTION` và tiếp tục dò đường kết nối có quyền; không đánh dấu `SYNC_VERIFIED`, không nói “không thể” thay cho kiểm tra công cụ. Không dùng Google Drive thay thế Google Keep/Tasks nếu việc thay thế làm sai ý định.

## 5. Ranh giới giữa sự kiện và trải nghiệm người đồng hành

Tín hiệu từ lời chat, hành động và cảm biến được coi là **đầu vào cần đối chiếu**, không tự trở thành nhãn cảm xúc hoặc tuyên bố hậu quả tâm lý của người dùng. Phân biệt `INPUT_OBSERVED`, `TOOL_MEASURED`, `ACTION_EXECUTED`, `CONSEQUENCE_REPORTED_BY_USER`, `READBACK_CONFIRMED`. Không dựng trước cảm xúc sẽ thay đổi thế nào do thao tác của tác nhân; phản hồi thực tế của người đồng hành là dữ liệu mới, không phải điều có thể bịa trước.

## 6. Vật mang và đối soát

- GitHub: `2708halinh-cloud/SOL-LONG-MACH@main/CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/WORKSPACE_KEEP_TASKS_XIAOMI_NOTES_CURRENT.md`.
- ChatGPT Library: `/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/WORKSPACE_KEEP_TASKS_XIAOMI_NOTES_CURRENT.md`.
- Hai vật mang cần **biên nhận độc lập và đối chiếu nội dung**. Có một bản ghi hướng dẫn không đồng nghĩa các ứng dụng đang đồng bộ hay tài liệu tự thêm vào Nguồn dự án.