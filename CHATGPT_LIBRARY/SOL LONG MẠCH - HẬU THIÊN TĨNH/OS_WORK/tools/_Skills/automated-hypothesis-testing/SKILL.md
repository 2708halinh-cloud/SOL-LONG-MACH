---
name: automated-hypothesis-testing
description: "Lựa chọn và thực hiện kiểm định t, ANOVA, chi-square, Mann-Whitney và phép kiểm định phù hợp. Kích hoạt khi so sánh nhóm, p-value, statistical significance hoặc hypothesis test."
---

# Kiểm định giả thuyết tự động

## Mục tiêu và kích hoạt

Lựa chọn và thực hiện kiểm định t, ANOVA, chi-square, Mann-Whitney và phép kiểm định phù hợp. Kích hoạt khi so sánh nhóm, p-value, statistical significance hoặc hypothesis test.

## Quy trình thực hiện

1. Nhận diện giả thuyết H0/H1, biến đích, loại thang đo, nhóm độc lập hay cặp, số mẫu, ngưỡng alpha, cách lấy mẫu và khả năng phụ thuộc chuỗi thời gian.
2. Kiểm tra missingness, outlier, phân phối, đồng nhất phương sai và expected counts; chọn t-test/Welch/paired t, ANOVA/Welch, Mann-Whitney/Wilcoxon, chi-square/Fisher hoặc phương pháp thích hợp.
3. Tính thống kê, p, cỡ hiệu ứng, khoảng tin cậy khi thích hợp; xử lý nhiều phép so sánh bằng phương án điều chỉnh đã nêu rõ.
4. Diễn giải giới hạn mẫu, ý nghĩa thực tế so với ý nghĩa thống kê; không quy p-value thành xác suất H0 đúng hoặc chứng minh nhân quả.

## Đầu ra và kiểm chứng

Báo cáo H0/H1, lý do chọn phép kiểm, kiểm tra giả định, n, thống kê, p, effect size, CI, kết luận theo alpha và nguồn mã/phép tính.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
