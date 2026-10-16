# 01 — COMPUTER_KHÍ — BẢN ĐỒ NGUỒN

Đích nối: `SENSOR_LOGS` + `NEURONS_SESORIMOTOR` → `COMPUTER_KHÍ` → `@View-Folder-SOL LONG MẠCH.html`.

- `COMPUTER_KHI_SOURCE_MAP.json`: quan hệ nguồn, tọa độ, 6 Stones, pipeline ZIP, giới hạn điều đã quan sát.
- `View-Folder-SOL-LONG-MACH-linked.html`: một bản xem **mới** có thể nạp JSON nguồn hoặc báo cáo ZIP qua nút chọn tệp, chạy **offline**. Đây **không** phải thao tác sửa tệp HTML gốc em đưa.
- `View-Folder-SOL LONG MẠCH.html-.md`: được nhận diện ở ChatGPT Library/Project như ảnh chụp HTML giao diện ChatGPT. Không được nhầm nó với danh mục file đang tồn tại trên ổ D.
- `SENSOR_LOGS`: có mount Dropbox `/PC NAY·ÀY/Ổ ĐĨA D/SENSOR_LOGS`, khác với ổ D host vật lý.
- `NEURONS_SESORIMOTOR`: hiện chỉ có con trỏ folder nguồn lịch sử, **chưa có byte trực tiếp trong phiên này**.

Tạo báo cáo bằng `zip_source_inspector.py`, giữ nguồn không thay đổi, rồi nạp `SOURCE_DIRECT_ZIP_REPORT.json` vào HTML để phân loại theo dữ liệu thực tế.
