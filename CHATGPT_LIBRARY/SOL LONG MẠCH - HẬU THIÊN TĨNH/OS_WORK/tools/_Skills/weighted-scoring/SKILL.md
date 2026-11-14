---
name: weighted-scoring
description: "Xây ma trận ra quyết định công nghệ/vendor/build-vs-buy; tiêu chí, trọng số và sensitivity. Kích hoạt weighted decision matrix, vendor selection, multicriteria choice hoặc build vs buy."
---

# Người chấm điểm có trọng số

## Mục tiêu và kích hoạt

Xây ma trận ra quyết định công nghệ/vendor/build-vs-buy; tiêu chí, trọng số và sensitivity. Kích hoạt weighted decision matrix, vendor selection, multicriteria choice hoặc build vs buy.

## Quy trình thực hiện

1. Xác định mục tiêu, lựa chọn, hard constraints, stakeholder, chi phí và hệ giá trị; loại các phương án không thỏa điều kiện bắt buộc trước khi chấm.
2. Chọn tiêu chí đo được, hướng lợi/hại, thang chuẩn hóa thống nhất và trọng số tổng 100%; ghi nguồn của mỗi score và xung đột lợi ích.
3. Tính weighted total = Σ(w_i × s_i), bảng ranking và trade-offs; thử sensitivity, threshold, đổi trọng số và điểm thiếu.
4. Trình bày cả phương án xếp nhất và điều kiện có thể đảo thứ tự, tránh chính xác giả nếu điểm chủ quan.

## Đầu ra và kiểm chứng

Trả decision matrix, trọng số chuẩn hóa, tổng điểm, ranking, sensitivity và các giả định chưa xác nhận.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
