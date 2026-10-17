---
name: chart-image
description: "Xuất biểu đồ PNG chất lượng cao từ bảng dữ liệu: line, bar, area, candlestick, pie và heatmap. Kích hoạt khi cần chart PNG, time series chart, chart for report, alert hoặc dashboard."
---

# Hình ảnh biểu đồ

## Mục tiêu và kích hoạt

Xuất biểu đồ PNG chất lượng cao từ bảng dữ liệu: line, bar, area, candlestick, pie và heatmap. Kích hoạt khi cần chart PNG, time series chart, chart for report, alert hoặc dashboard.

## Quy trình thực hiện

1. Nhận dữ liệu, mục tiêu biểu đồ, đơn vị/trục, nhãn, khoảng thời gian, độ phân giải và vị trí tệp đầu ra.
2. Chọn line/bar/area/candlestick/pie/heatmap phù hợp; ưu tiên Node.js headless nếu runtime render có thư viện hợp lệ đã kiểm; nếu không, dùng backend PNG khác hiện có và khai báo rõ.
3. Kiểm trục (không cắt sai lệch), xử lý missing, dữ liệu âm, chú giải, văn bản có dấu và khả năng đọc khi thu nhỏ; dùng DPI/kích thước xuất bản.
4. Mở chính file PNG đã sinh để kiểm crop, ký hiệu, số liệu, màu và tính tái lập; không coi SVG/HTML là PNG đã xuất.

## Đầu ra và kiểm chứng

Trả PNG thực tồn tại, thông số render, nguồn dữ liệu và mô tả những kiểm tra trực quan đã làm.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
