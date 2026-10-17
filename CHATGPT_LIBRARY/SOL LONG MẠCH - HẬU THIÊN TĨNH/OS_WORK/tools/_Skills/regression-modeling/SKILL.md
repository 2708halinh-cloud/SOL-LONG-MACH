---
name: regression-modeling
description: "Khớp OLS hoặc logistic trên CSV/Excel; báo coefficients, R² hoặc pseudo-R², p-values, VIF và diễn giải. Kích hoạt regression, OLS, logit, collinearity hoặc model fitting."
---

# Mô hình hồi quy

## Mục tiêu và kích hoạt

Khớp OLS hoặc logistic trên CSV/Excel; báo coefficients, R² hoặc pseudo-R², p-values, VIF và diễn giải. Kích hoạt regression, OLS, logit, collinearity hoặc model fitting.

## Quy trình thực hiện

1. Xác định y, X, tập huấn luyện/kiểm tra, mục đích dự báo hay giải thích; kiểm mất dữ liệu, encoding categorical và leakage.
2. Chọn OLS cho y liên tục hay logistic cho y nhị phân; ước lượng intercept, coefficient, SE, CI, p; ghi rõ phiên bản phương pháp và n.
3. Với OLS: R²/adjusted R², residuals, heteroskedasticity, multicollinearity qua VIF; với logistic: odds ratios, calibration, discrimination và pseudo-R² đã định nghĩa.
4. Kiểm outlier/influential points, separation và biến giả; không gán ý nghĩa nhân quả khi thiết kế dữ liệu không hỗ trợ.

## Đầu ra và kiểm chứng

Trả mô hình, encoding, bảng hệ số, metrics phù hợp, giả định/diagnostics, diễn giải và mã tái lập khi có quyền tính.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
