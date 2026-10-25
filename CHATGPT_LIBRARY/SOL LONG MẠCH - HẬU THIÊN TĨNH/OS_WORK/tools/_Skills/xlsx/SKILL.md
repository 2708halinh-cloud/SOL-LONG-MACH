---
name: xlsx
description: "Tạo, chỉnh sửa, phân tích XLSX/XLSM/CSV; công thức, định dạng, biểu đồ, mô hình ba báo cáo, DCF và so sánh công ty. Kích hoạt advanced spreadsheet, Excel modeling, formulas, workbook hoặc xlsx."
---

# XLSX

## Mục tiêu và kích hoạt

Tạo, chỉnh sửa, phân tích XLSX/XLSM/CSV; công thức, định dạng, biểu đồ, mô hình ba báo cáo, DCF và so sánh công ty. Kích hoạt advanced spreadsheet, Excel modeling, formulas, workbook hoặc xlsx.

## Quy trình thực hiện

1. Đọc quy ước bảng tính của môi trường trước; lấy đúng workbook/sheet/range, sao lưu nếu ghi lên nguồn, phân biệt XLSX, XLSM, CSV và macro.
2. Sử dụng openpyxl hoặc artifact_tool được cấp để chỉnh sửa có phạm vi; bảo toàn sheet, format, formulas, named ranges, chart links và VBA với keep_vba khi phù hợp.
3. Xây công thức tài chính có input/assumption riêng, tham chiếu nhất quán, number format tiền tệ, khóa cell hợp lý và error checks; đánh dấu các ô được thay.
4. Tính lại bằng bộ máy được phép nếu có; openpyxl không tự calculate nên không khẳng định cache công thức đã cập nhật. Mở lại tệp, kiểm formulas, công thức lỗi và kết quả engine khi hỗ trợ.

## Đầu ra và kiểm chứng

Trả workbook đã ghi đúng path với readback sheet/range, danh sách thay đổi, cảnh báo tính lại chưa được xác thực nếu thiếu engine.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
