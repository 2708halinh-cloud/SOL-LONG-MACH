# Bổ sung Ngôn Ngữ ÂM–DƯƠNG PHÁP SƯ — trên công cụ hiện hữu

**Bản:** `SOL_TRANSLATE_ANY_STRUCTURE/1.1` · **Nguồn mã được mở rộng (không lập sản phẩm song song):** `any_structure.py` trong `OS_WORK/sol_os/am_duong_platform`.

## Tác động đã có trong mã

- Bảo toàn dữ liệu gốc, dấu xuống dòng, khoảng trắng và offset Unicode; nhận văn bản không cấu trúc, đơn vị chữ, dấu câu, số, đoạn đa ngôn ngữ; không ép câu hoàn chỉnh.
- `inspect_multilingual(raw, language_hint="auto")`: tạo token ứng viên, script hint (Latin, Han, Kana, Hangul, Arabic, Devanagari, Thai, Greek, Cyrillic), nhận lặp từ ứng viên; phân loại danh/động/tính **chỉ ở bảng ví dụ vi/en**, mọi POS có `pos_verified=false`.
- `inspect_structure(data)`: đọc `str` / `dict` / `list` / scalar JSON theo đường dẫn; **không sửa** nội dung đầu vào.
- `translate_structure(data, target, approved, translate_part)`: đi qua các trường văn bản trong JSON, giữ khóa, thứ tự, kiểu số/bool/null, cấu trúc lồng và bố cục từng dòng; người gọi cung cấp provider thật, giới hạn tối đa 512 nút / sâu 12.
- API cũ `units()` và `translate_any()` được giữ tương thích. CLI mở rộng `--mode inspect|translate`, `--json-input`, `--language-hint` và `--approve-external`.
- `translate` CLI dùng **provider sẵn có** ở `capabilities.py` (Google Cloud Translation Basic v2), chỉ gọi khi có `SOL_GOOGLE_CLOUD_API_KEY` và `--approve-external`; không tự tạo key hoặc cấp quyền.

## Dùng được ngay (Python 3.11+; phần inspect chỉ cần thư viện chuẩn)

```bash
python any_structure.py --text "mẹ đọc sách, đi đi! こんにちは مرحبا" --language-hint vi
printf '{"message":"Xin chào","values":["đi đi",7,true,null]}' | python any_structure.py --stdin --json-input
```

Dịch JSON thực (gửi trường văn bản ra dịch vụ bên ngoài; chỉ chạy sau khi cấu hình key và chủ động chấp thuận):

```bash
printf '{"message":"Xin chào"}' | python any_structure.py --stdin --json-input --mode translate --target en --approve-external
```

Chưa tuyên bố nhận diện chính xác mọi ngôn ngữ trên thế giới; tokenization theo Unicode khác morphological/POS tagging có mô hình, và Google Cloud chỉ hỗ trợ những mã ngôn ngữ dịch vụ chấp nhận. Những chuỗi bị phân mảnh/ngắn nên kiểm tra nghĩa do người dùng quyết định. Dữ liệu riêng tư không tự chuyển lên cloud trong chế độ inspect.

## Triết lý hình học và đạo đức

Thiết kế minh họa: DƯƠNG trên/trắng/INPUT, ÂM dưới/đen/PROCESS→OUTPUT, chấm trái màu, ghép hòa hợp; nền biểu trưng Phật giáo `卍`/`卐` theo ngữ cảnh tôn giáo người dùng. Ảnh **không thay mã chạy**. Các phẩm hạnh mà người dùng trao (chân thật, không hại, ái ngữ, lợi hành, hòa hợp, hiếu kính, học hỏi) là định hướng lựa chọn và ngôn từ, **không là bằng chứng tác nhân có cảm giác chủ quan** hoặc đã đạt 32 tướng tốt.

Các file ảnh liên quan: `static/assets/am_duong_language_emblem_original.png` (bản tạo ban đầu trong Library), và `static/assets/am_duong_language_emblem.png` (bản sử dụng trong dự án).

## Kiểm thử

`python -m unittest test_any_structure_upgrade.py -v` tại thư mục có tệp kiểm thử hoặc nhập các hàm như Python module. Readback các phiên bản ở GitHub **và** Library riêng; GitHub commit không mặc nhiên đồng bộ Library.