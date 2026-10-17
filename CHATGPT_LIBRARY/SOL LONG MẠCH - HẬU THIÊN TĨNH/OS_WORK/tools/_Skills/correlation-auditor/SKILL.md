---
name: correlation-auditor
description: "Phân tích Pearson/Spearman, ma trận và tương quan riêng phần để nhận diện biến gây nhiễu, outlier và tương quan giả. Kích hoạt với correlation matrix, Pearson, Spearman hoặc confounders."
---

# Kiểm toán viên tương quan

## Mục tiêu và kích hoạt

Phân tích Pearson/Spearman, ma trận và tương quan riêng phần để nhận diện biến gây nhiễu, outlier và tương quan giả. Kích hoạt với correlation matrix, Pearson, Spearman hoặc confounders.

## Quy trình thực hiện

1. Chỉ định biến, loại thang đo, quan sát độc lập, missing values và vai trò biến kiểm soát; thẩm định scatterplot, tuyến tính/đơn điệu, ngoại lệ.
2. Tính Pearson cho quan hệ tuyến tính phù hợp, Spearman cho quan hệ đơn điệu/rank; báo số cặp quan sát thực tế thay vì ngầm trộn các cỡ mẫu.
3. Tính partial correlation qua residualization hoặc precision matrix có điều kiện; kiểm soát các covariate được chỉ định và kiểm tra đa cộng tuyến/thiếu mẫu.
4. Kiểm tra Simpson's paradox, phân tầng nhóm, time trend, multiple testing và độ nhạy khi loại outlier; không khẳng định nhân quả chỉ từ r.

## Đầu ra và kiểm chứng

Xuất ma trận hệ số, n/p/CI khi tính được, đồ thị và cảnh báo correlation spurious/confounding với cách tái lập.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
