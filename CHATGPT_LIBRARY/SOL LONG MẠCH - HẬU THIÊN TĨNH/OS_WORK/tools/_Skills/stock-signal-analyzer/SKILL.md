---
name: stock-signal-analyzer
description: "Tính các chỉ báo trên OHLCV như MA, EMA, MACD, RSI, Bollinger Bands, KDJ, ATR và hơn 15 chỉ số; tóm tắt bullish/bearish khi hỏi technical analysis, candlesticks hoặc overbought/oversold."
---

# Máy phân tích tín hiệu chứng khoán

## Mục tiêu và kích hoạt

Tính các chỉ báo trên OHLCV như MA, EMA, MACD, RSI, Bollinger Bands, KDJ, ATR và hơn 15 chỉ số; tóm tắt bullish/bearish khi hỏi technical analysis, candlesticks hoặc overbought/oversold.

## Quy trình thực hiện

1. Nhận OHLCV có timestamp, timezone, ticker, adjusted price, volume, khung thời gian; kiểm thứ tự, missing sessions, corporate actions và đủ warm-up.
2. Tính ít nhất 15 chỉ báo khi đủ dữ liệu: SMA5/20/50/200, EMA12/26, MACD, signal, histogram, RSI14, BB upper/lower/%B, stochastic %K/%D/J, ATR14, OBV, ADX, ROC; tài liệu hóa tham số.
3. Đánh dấu crossover, trend, volatility, overbought/oversold và volume confirmation. Ưu tiên dùng nến đã đóng, tránh look-ahead và điều chỉnh corporate actions.
4. Tổng hợp bằng rubric dễ kiểm và cảnh báo mâu thuẫn, nhiễu ngắn hạn, lợi nhuận chưa kiểm chứng; backtest chỉ nếu có dữ liệu/chi phí.

## Đầu ra và kiểm chứng

Trả ngày dữ liệu, bảng chỉ báo/giá trị, tín hiệu bullish/bearish/neutral, mức tin cậy theo dữ liệu và hạn chế.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
