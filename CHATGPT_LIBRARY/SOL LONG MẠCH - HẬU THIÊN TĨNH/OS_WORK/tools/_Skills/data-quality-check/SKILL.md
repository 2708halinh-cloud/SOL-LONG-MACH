---
name: data-quality-check
description: "Kiểm tra bảng CSV/Excel/TSV/JSON về missing, duplicate, outlier, format và dtype; chấm điểm chất lượng kèm hành động làm sạch. Kích hoạt data profiling, validation, cleaning hoặc quality audit."
---

# Kiểm tra chất lượng dữ liệu

## Mục tiêu và kích hoạt

Kiểm tra bảng CSV/Excel/TSV/JSON về missing, duplicate, outlier, format và dtype; chấm điểm chất lượng kèm hành động làm sạch. Kích hoạt data profiling, validation, cleaning hoặc quality audit.

## Quy trình thực hiện

1. Kiểm kiểu nguồn, encoding, sheet/column, hạt dữ liệu (grain), primary key dự kiến, số hàng/cột và data dictionary nếu có.
2. Tính completeness từng cột, trùng hàng/khóa, unique, type mismatch, parse lỗi ngày/số, range/domain violations, outlier IQR hoặc robust z-score (phân biệt outlier với lỗi).
3. Xác lập rubric/weights minh bạch cho tổng điểm 0–100, không giả đây là tiêu chuẩn phổ quát; tính tỷ lệ lỗi theo mẫu và khả năng tác động tới nghiệp vụ.
4. Đưa hướng sửa có độ ưu tiên; chỉ chỉnh dữ liệu trên bản sao hoặc phạm vi được cấp, lưu before/after và không mặc định xóa ngoại lệ.

## Đầu ra và kiểm chứng

Trả quality score có công thức, bảng vấn đề theo trường/hàng, ví dụ lỗi đã ẩn dữ liệu nhạy cảm, đề xuất và readback sau sửa nếu có.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
