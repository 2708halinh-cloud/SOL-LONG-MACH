---
name: data-visual-infographics
description: "Tạo infographic HTML/SVG độc lập từ JSON: KPI cards, bar charts, flow diagrams và dashboard. Kích hoạt khi yêu cầu đồ họa thông tin, biểu đồ, data visualization hoặc dashboard không phụ thuộc thư viện ngoài."
---

# Trình hiển thị dữ liệu trực quan

## Mục tiêu và kích hoạt

Tạo infographic HTML/SVG độc lập từ JSON: KPI cards, bar charts, flow diagrams và dashboard. Kích hoạt khi yêu cầu đồ họa thông tin, biểu đồ, data visualization hoặc dashboard không phụ thuộc thư viện ngoài.

## Quy trình thực hiện

1. Xác nhận schema JSON, phép đo, đơn vị, thứ tự, đối tượng đọc và chủ đề cần kể bằng dữ liệu; làm sạch dữ liệu lỗi trước khi vẽ.
2. Chọn thành phần KPI, biểu đồ cột, luồng hoặc dashboard; dùng SVG/HTML/CSS/JS nhúng hoàn toàn, không CDN và không font/icon remote.
3. Cung cấp tám bộ màu có tên và tương phản phù hợp; dựng biểu tượng bằng SVG inline; hỗ trợ nhãn, tooltip/description hoặc bảng dữ liệu thay thế cho hỗ trợ tiếp cận.
4. Đối chiếu từng con số hiển thị với JSON, kiểm viewport mobile/desktop, nhãn trục và màu không phải tín hiệu duy nhất.

## Đầu ra và kiểm chứng

Trả một tệp HTML hoặc SVG có thể mở độc lập, nguồn JSON (nhúng hay cạnh bên), ghi rõ điều đã render/được kiểm.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
