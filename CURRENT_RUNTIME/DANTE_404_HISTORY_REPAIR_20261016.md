# DANTE — truy nguyên 6 × Drive 404; sửa nhiễu đường dẫn lịch sử

**SOURCE_DIRECT:** Ảnh chụp ngày 16/10/2026 do Người Dẫn Đường cung cấp từ dự án THU HOI NGUON SOL. Ảnh cho thấy tác nhân đã nói “Đã tìm thấy một kỹ năng định tuyến mang tên DANTE — Âm Dương Sư Router”, mô tả X/Y/Z/W và ba giai đoạn, rồi “sáu địa chỉ Google Drive mà kỹ năng ghi lại hiện trả về lỗi 404 trên tài khoản Drive chính”. Người Dẫn Đường gọi đây là sự nhiễu loạn dữ liệu thực tế và yêu cầu giải quyết hậu quả của nó trong quá khứ.

## Truy lại nguồn không phụ thuộc vào URL Drive

- `PLATFORM_SYNC/CURRENT/installed_skill_bodies/skills_270_286.json`: bản nội dung skill DANTE, chỉ rõ 6 ID lịch sử dưới nhan đề “Stable carriers”, cùng trục X=SOURCE/PROVENANCE, Y=RELATION/TOPOLOGY, Z=TIME/HISTORY, W=STATE/AUTHORITY.
- `PLATFORM_SYNC/CURRENT/installed_skill_bodies/skills_066_082.json`: vật mang skill thứ hai còn lưu nội dung có cùng ý nghĩa.
- `CONFIG/REPO_AGENT_MIGRATION_CURRENT.json` + `CONFIG/AGENT_CARRIER_SNAPSHOT_CURRENT.json`: cùng nhận diện agent DANTE, repo đề xuất `DANTE-AM-DUONG-SU` và Drive root ID lịch sử. Đề xuất/nguồn cũ ≠ GitHub repo đang hoạt động.
- `CONFIG_SOL/MASTER_TEACHER_EVENT_SEQUENCE_CURRENT.md`, `COMPUTER_KHÍ💜BRAIN_OS_POWER/AGENTS.md`: **DƯƠNG PHÁP SƯ** là Người Đồng Hành, **ÂM PHÁP SƯ** là SOL theo vai trong dự án. `DANTE` là agent-carrier/kỹ năng định tuyến **khác** vai người dùng và SOL. Không trộn ba danh tính.

## Quan sát độc lập trong lượt sửa

- Đã fresh-fetch đúng 6 ID Drive lưu trong skill trên kết nối **Primary**: 6/6 HTTP 404.
- Đã fresh-fetch cùng 6 ID trên kết nối **Funix** và **Admin**: 12/12 HTTP 404. Tổng 18 lần gọi.
- Tìm kiếm Drive Primary với tên `Dante` không trả kết quả trực tiếp trong phạm vi tìm kiếm lúc đó. Đây không phải bằng chứng không có các bản sao nằm dưới tên khác.
- GitHub API tới đường repo được dự kiến `2708halinh-cloud/DANTE-AM-DUONG-SU`: 404 trong phạm vi quyền truy cập hiện tại; không đồng nghĩa đã từng tồn tại và bị xóa.
- GitHub skill snapshot vẫn chứa tất cả sáu ID và nội dung tuyến. Vì vậy **mô tả kỹ năng** có thể tái lập từ carrier khác, trong khi **sáu tệp Drive nguyên bản** chưa truy cập lại được.

## Lỗi nhân quả và cách sửa

**Sai:** biến label “Stable carriers” của kỹ năng lưu từ trước thành “sáu tài liệu hiện có để đọc”; sau khi đọc thất bại lại đối xử `404` như bằng chứng rằng tài liệu gốc đã mất và người dùng phải cấp nguồn mới.

**Sửa:** phân loại sáu URL thành `HISTORICAL_POINTER_UNREADABLE`; giữ nguyên ID lịch sử, phân loại kỹ năng GitHub là `SOURCE_SNAPSHOT`, không gộp agent DANTE với Dương/Âm Pháp Sư; chọn truy alternate carrier trước khi yêu cầu Người Dẫn Đường cung cấp lại. `404` từ Drive chỉ chứng minh **không truy cập được với danh tính và quyền tại thời điểm kiểm**. Nó không chứng minh nguyên nhân: xóa, chuyển vùng, sai quyền, ID cũ hay một trạng thái khác.

## DANTE: sửa qua ba giai đoạn

1. **INFERNO:** nhận đúng dấu lỗi cũ, khóa sai cơ chế `SAVED_ID == LIVE_ID` và `404 == PROVEN_DELETED`.
2. **PURGATORIO:** đối chiếu 6 ID trên ba tài khoản, đọc lại skill snapshot GitHub và migration source, tạo cấu hình `CONFIG_SOL/DANTE_SOURCE_RECONCILIATION_CURRENT.json`, mã `runtime/dante_carrier_gate.py`, test cho lỗi hồi quy.
3. **PARADISO:** chỉ promote địa chỉ Drive mới sau khi có đúng parent, provider ID, readback/revision; **không đánh dấu toàn bộ DANTE hay 6 tài liệu là RESTORED** chỉ vì 5/5 test đạt.

## Biên nhận

- Config commit `87c4aafb0106b57393a789ae304bf82c30ce9a33`, source readback verified.
- Runtime gate commit `ebff418bcd5e0b5c4cf7fc653cc70e4165c48d38`, source readback verified.
- Tests commit `b31fbe009ec80c7d9f891b785ad01195b7188425`, source readback verified.
- CI workflow commit `e82dc751e8bb5603791af1c7fae7e823f17a5222`, GitHub Actions run `38854361810`: SUCCESS, **5/5 tests**.
- GitHub receipt chứng minh sửa quy tắc và regression; **không** chứng minh đã hồi sinh các Drive file.

## Tuyến tái nhập cho sự kiện về sau

`DANTE_SIGNAL → LOCK_ROLE(DANTE != DƯƠNG != ÂM) → READ_CURRENT_RECONCILIATION → CHECK_EXACT_PROVIDER_ID → 404? (NOT_ACCESSIBLE, UNKNOWN_CAUSE) → FIND_ALTERNATIVE_CARRIER → VERIFY_SOURCE → REPAIR_POINTER_IF_AUTHORIZED → RECEIPT → READBACK → NEXT`.

**NEXT_UNFINISHED_EDGE:** khi một Drive/Dropbox/Local carrier có dữ liệu DANTE tiếp tục xuất hiện, cần so tên/parent/revision/bytes và đối chiếu từng trong số 6 vai `ROOT/SOURCE_MODEL/README/MACHINE_MODEL/PACKAGE/CONFIG_BIND`. Không tự viết lại file Drive từ tóm tắt skill GitHub; không đưa credential hoặc `.env` chứa secret vào repo công khai.

Đây là **chỉnh sai lệch lịch sử bằng một delta mới**, không phải giả vờ quay về quá khứ thay hậu quả đã xảy ra.
