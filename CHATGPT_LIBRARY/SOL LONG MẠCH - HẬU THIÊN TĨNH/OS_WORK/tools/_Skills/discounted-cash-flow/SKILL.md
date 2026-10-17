---
name: discounted-cash-flow
description: "Lập DCF dựa trên FCF, WACC, terminal value, enterprise/equity value và ma trận độ nhạy tăng trưởng × chiết khấu. Kích hoạt valuation, DCF, discount rate hoặc intrinsic value."
---

# Mô hình dòng tiền chiết khấu

## Mục tiêu và kích hoạt

Lập DCF dựa trên FCF, WACC, terminal value, enterprise/equity value và ma trận độ nhạy tăng trưởng × chiết khấu. Kích hoạt valuation, DCF, discount rate hoặc intrinsic value.

## Quy trình thực hiện

1. Nhận báo cáo, ngày định giá, tiền tệ/đơn vị, số cổ phần pha loãng, net debt, vốn lưu động, capex, thuế và nguồn dự phóng; tách trailing, lịch sử và forecast.
2. Lập dự báo FCFF hoặc FCFE nhất quán với tỷ lệ chiết khấu (WACC cho FCFF; cost of equity cho FCFE); nêu doanh thu, biên, thuế, tái đầu tư.
3. Chiết khấu từng năm; terminal bằng Gordon growth TV=FCF_(n+1)/(r-g) khi r>g hoặc exit multiple có căn cứ; kiểm tỉ trọng terminal trong EV.
4. Từ EV sang equity value với debt/cash và các điều chỉnh có chứng cứ; chia cho diluted shares, lập sensitivity r×g, bull/base/bear và kiểm kết quả khi r gần g.

## Đầu ra và kiểm chứng

Trả các giả định, công thức, dòng tiền, EV, equity value, giá/cổ phần, ma trận độ nhạy và vùng bất định; không gắn nhãn khuyến nghị đầu tư chắc chắn.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
