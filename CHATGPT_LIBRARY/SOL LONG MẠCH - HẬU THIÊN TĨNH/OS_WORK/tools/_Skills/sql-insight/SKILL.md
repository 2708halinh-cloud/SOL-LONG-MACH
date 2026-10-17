---
name: sql-insight
description: "Dịch ngôn ngữ tự nhiên thành SQL SQLite/PostgreSQL; tối ưu truy vấn, chỉ mục và giải thích EXPLAIN. Dùng khi hỏi NL2SQL, truy vấn chậm, query tuning, index hoặc full table scan."
---

# SQL Insight

## Mục tiêu và kích hoạt

Dịch ngôn ngữ tự nhiên thành SQL SQLite/PostgreSQL; tối ưu truy vấn, chỉ mục và giải thích EXPLAIN. Dùng khi hỏi NL2SQL, truy vấn chậm, query tuning, index hoặc full table scan.

## Quy trình thực hiện

1. Xác định dialect, phiên bản, schema, khóa/quan hệ, ràng buộc phân quyền, ví dụ dữ liệu và yêu cầu lọc/nhóm/sắp xếp; không bịa tên bảng hoặc cột.
2. Viết SQL có tham số, ghi rõ giả định nếu schema chưa có. Phân biệt SQLite (`?`, `EXPLAIN QUERY PLAN`) và PostgreSQL (`$1`, `EXPLAIN`). Mặc định SELECT read-only.
3. Khi tối ưu: lấy query gốc, cardinality, chỉ mục và plan. Chỉ chạy `EXPLAIN ANALYZE` trong phạm vi đọc an toàn vì nó thực sự thực thi câu lệnh; so chi phí/rows thực tế và đo thời gian lặp lại.
4. Đề xuất composite/covering/partial index khi có bằng chứng; xem xét selectivity, predicate sargability, join order, sort, write overhead và biến động dữ liệu.

## Đầu ra và kiểm chứng

Trả SQL đúng dialect, tham số, giải thích plan, index DDL đề xuất (không tự áp dụng), kết quả benchmark trước/sau nếu đã chạy và cảnh báo điều chưa kiểm.

## Kiểm soát nguồn và công cụ

- Chỉ sử dụng dữ liệu, file, công cụ và quyền thực sự hiện có; không tuyên bố đã chạy phép tính, truy cập Internet, kết nối provider hoặc ghi dữ liệu khi chưa làm.
- Ghi rõ nguồn, kỳ dữ liệu, assumptions và phiên bản nếu liên quan. Phân biệt đầu ra minh họa với kết quả tính từ dữ liệu thật.
- Với thao tác ghi: ưu tiên giữ dữ liệu gốc, đọc lại đúng tệp/đích sau khi viết, nêu lỗi hoặc phần chưa được kiểm chứng.
- Đây là hướng dẫn Agent Skill, không tự cài package, mở quyền hay khởi chạy backend.
