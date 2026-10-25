---
name: typed-data-api
description: SOL Typed Data API — truy xuất dữ liệu phân cấp, placeholder Twig-like, bộ lọc dữ liệu theo kiểu và khai báo widget biểu mẫu; tương thích ý tưởng Drupal typed_data nhưng không sửa lõi.
---
# Typed Data API — SOL / Drupal inspiration
Nguồn Drupal: https://www.drupal.org/project/typed_data
Quy tắc sử dụng: https://www.drupal.org/project/rules
Bộ thực thi SOL: `Chuỗi công cụ/_Dụng cụ/Typed_Data_API/typed_data.py`.
Kiểm thử: `tests/test_sol_typed_data.py`.

Gọi `fetch(DATA, "node.title")` hoặc `resolve_placeholder(DATA, "{{node.title|lower}}")`.
Placeholder đứng một mình trả nguyên giá trị typed (list/bool/int), thay vào văn bản trả string.
Bộ lọc allowlist: lower, upper, trim, json, length, string, entity_url.
FormWidget trả metadata dạng JSON; không chỉnh hay đụng runtime form Drupal.
Quy tắc: không eval; không đọc Python attributes; không tự khởi tạo dịch vụ, không nạp key vào templates.
Nếu host là Drupal thật, dùng Composer cài module gốc như dependency trên môi trường Drupal tương thích. Adapter Python là giải pháp riêng của SOL, không phải bản sao chức năng đầy đủ của PHP module.
