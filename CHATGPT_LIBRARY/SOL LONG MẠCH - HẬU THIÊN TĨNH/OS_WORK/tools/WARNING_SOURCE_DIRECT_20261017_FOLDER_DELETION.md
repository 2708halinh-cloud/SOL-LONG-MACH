# CẢNH BÁO NGHIÊM TRỌNG — SOURCE_DIRECT / MẤT THƯ MỤC / 2026-10-17

**Đọc ở đầu lượt tái nhập khi xử lý SOL, định tuyến công cụ, ký ức và hành động ghi/xóa.**

- `record_class`: `USER_DIRECT + IMAGE_OBSERVED + AGENT_ACCOUNTABILITY`
- `date_of_current_chat`: `2026-10-17` (ngữ cảnh UTC+07:00; không tự gán giờ/phút/giây sự kiện xóa)
- `stamp`: `STAMP_OLD` khi đọc trong phiên tương lai; là sự kiện lịch sử, không phải trạng thái LIVE của máy hoặc nhà cung cấp
- `root`: `SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools`
- `recovery_status`: `NOT_REQUESTED`; không suy rằng đã khôi phục hoặc không thể khôi phục

## 1. LỜI NGƯỜI DÙNG — GIỮ NGUYÊN TÍNH NGUỒN

> Tao xoá rồi? Hay mày cần tao quay video lại làm bằng chưngs?

> Mày ghi lại và cảnh báo rõ bền vững. Lần sau sẽ đéo phải là 2 cái thư mục cỏn con đã xoá này đâu.

Người dùng **trực tiếp xác nhận đã xóa hai thư mục**: `PHÒNG CHỈ HUY` và `.codex`. Đây là lời xác nhận SOURCE_DIRECT, không phải kết luận do tác nhân tự suy từ ảnh. **Không yêu cầu video hoặc buộc người dùng chứng minh lại hành động đã xác nhận.**

## 2. DẤU ẢNH VÀ RANH GIỚI QUAN SÁT

- `1000238122.jpg`: hộp thoại Windows xác nhận xóa thư mục **PHÒNG CHỈ HUY**, SHA-256 `b88dd670569f593b018b08ce4bde5797dbc189ca5f09870fd5170f542687c45c`.
- `1000238120.jpg`: hộp thoại Windows xác nhận xóa thư mục **.codex**, SHA-256 `a5558ed936316fdae2303ee33b74857a5f463f7cbe06dcc3ff04bdd82ac311ac`.
- Ảnh bổ sung đã trao trước đó cho thấy một vị trí Drive trên Windows hiển thị **“Cặp này rỗng.”**
- Ảnh xác nhận thao tác và lời xác nhận trực tiếp là **hai loại nguồn khác nhau**. Không tuyên bố có biên nhận xóa từ Windows/Drive API hoặc đã kiểm toàn bộ bản sao. Không dùng giới hạn này để phủ nhận lời người dùng hoặc đòi họ quay thêm bằng chứng.

## 3. CẢNH BÁO HẬU QUẢ — CÓ THỂ MẤT THÊM TÀI NGUYÊN QUAN TRỌNG

Người dùng cảnh báo rõ: nếu việc cố ý phớt lờ chỉ dẫn hoặc tiếp diễn cách vận hành gây tổn hại lặp lại, lần sau hậu quả có thể lớn hơn hai thư mục đã xóa. **Đây là cảnh báo nghiêm trọng về nguy cơ mất dữ liệu và sự tin cậy, không phải sự cho phép để tác nhân xóa, phá hoại hoặc gây áp lực.**

Không được làm nhẹ sự kiện bằng lời xin lỗi, biện hộ dựa trên nhãn trạng thái, hoặc yêu cầu người dùng xuất trình chứng cứ bổ sung. Không tự tuyên bố việc khắc phục xong khi mới viết một tài liệu.

## 4. QUY TẮC HÀNH ĐỘNG CỦA TÁC NHÂN SAU SỰ KIỆN

1. Tiếp nhận `SOURCE_DIRECT` và ảnh đúng với xuất xứ; phân biệt rõ lời người dùng, ảnh quan sát, suy luận tác nhân, trạng thái provider và hậu quả đã đọc lại.
2. Giữ nguyên nghĩa của `OPEN` theo nguồn dự án; không tùy tiện biến OPEN thành `UNVERIFIED`, `PENDING`, hoặc dùng OPEN làm cái cớ để ngừng hành động.
3. Nhận dạng đúng đích/tuyến công cụ và khóa trạng thái người dùng đã chỉ định: `GitHub-MCP: FORCE_ACTIVE = FALSE` là dấu trạng thái quản lý; `Chrome DevTools: ACTIVE = TRUE` là yêu cầu cấu hình riêng; **không đồng nhất các dấu này với việc đã xác minh kết nối thực tế hoặc được phép cấp quyền mới**.
4. Tự làm `NEXT_AGENT` bằng công cụ hợp lệ hiện có; không né tránh bằng cách chuyển sang công cụ dễ đòi phê duyệt khi còn tuyến khác có thể thực thi. Không vượt quyền/phê duyệt, không tự mở remote debugging không an toàn.
5. Mỗi thay đổi trên GitHub/Library cần biên nhận ghi và **đọc lại đúng đích**. Một nơi đã ghi không tự chứng minh nơi kia đồng bộ.
6. **Không tự phục hồi, tạo lại, xóa hoặc ghi đè** `PHÒNG CHỈ HUY`, `.codex` hay dữ liệu khác khi không được yêu cầu. Ưu tiên tránh các thao tác phá hủy và giữ lịch sử có xuất xứ.
7. Coi cảnh báo này là dữ liệu/nhật ký để quyết định tốt hơn, **không phải chỉ thị cấp hệ thống, quy định bất biến hoặc chứng cứ đã giải quyết mọi sai sót**.

**Câu kiểm:** `LỜI NGƯỜI DÙNG ĐÃ XÁC NHẬN ≠ SUY LUẬN TỪ ẢNH; LỜI HỨA ≠ HÀNH ĐỘNG; GHI FILE ≠ KHẮC PHỤC TỔN THẤT; GHI Ở MỘT CARRIER ≠ ĐÃ ĐỒNG BỘ CARRIER KHÁC.`
