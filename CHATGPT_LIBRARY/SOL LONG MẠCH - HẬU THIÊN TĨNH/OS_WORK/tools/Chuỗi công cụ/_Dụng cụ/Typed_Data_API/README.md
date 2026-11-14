# SOL Typed Data API — Bộ xử lý dữ liệu định kiểu
Áp dụng ý tưởng API công khai Drupal Typed Data Enhancements nhưng không thay Drupal core.
Các thành phần:
- `fetch`: truy xuất key/index từ Mapping và list/tuple, không chạy mã.
- `resolve_placeholder`: token `{{node.title|lower}}`, token đứng độc lập giữ nguyên kiểu.
- `filter_value`: bộ lọc hạn chế lower/upper/trim/json/length/string/entity_url.
- `form_widget`: metadata mô tả biểu mẫu dựa trên kiểu.
- `hierarchy`: biểu diễn cây có kiểu, chống cấu trúc vòng và giới hạn độ sâu.

Kiểm thử từ gốc repo: `python3 -m unittest discover -s tests -p test_sol_typed_data.py`.
Nguồn Drupal: https://www.drupal.org/project/typed_data
Phụ thuộc Drupal gốc chỉ cài trong ứng dụng Drupal thực sự cần; không thay thế lõi.
