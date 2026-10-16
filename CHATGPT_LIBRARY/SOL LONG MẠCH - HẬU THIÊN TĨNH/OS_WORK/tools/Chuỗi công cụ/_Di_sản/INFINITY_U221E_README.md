# Tools · Quy ước ký hiệu vô cực ∞

**Nguồn chỉ định:** Người dùng, 14/10/2026.  
**Vật mang đích:** ChatGPT Library → `SOL LONG MẠCH - HẬU THIÊN TĨNH / OS_WORK / tools`.  
**Tệp máy đọc:** `INFINITY_U221E_SYMBOL_RULE.json`.

## Phân biệt Unicode

| Ký hiệu | Mã Unicode | Tên Unicode | Vai trò |
| --- | --- | --- | --- |
| **∞** | **U+221E** | INFINITY | **Ký hiệu chuẩn cho vô cực** |
| ♾️ | U+267E, thường kèm U+FE0F | PERMANENT PAPER SIGN | Dấu giấy vĩnh viễn; không thay thế ∞ |
| ⚭ | U+26AD | MARRIAGE SYMBOL | Ký hiệu hôn nhân; không thay thế ∞ |
| ↀ | U+2180 | ROMAN NUMERAL ONE THOUSAND C D | Chữ số La Mã 1000; không thay thế ∞ |

**Định nghĩa theo yêu cầu:** Vô cực, vô tận, vô hạn biểu đạt không có giới hạn hữu hạn hoặc điểm kết thúc; ký hiệu toán học là `∞`. Trong ngữ cảnh số mở rộng, có thể viết `∞ > n` với mọi số tự nhiên `n`, nhưng `∞` không phải một số thực thông thường.

**Mã biểu diễn:** Unicode `U+221E`; HTML `&infin;` hoặc `&#8734;`; JSON Unicode escape `\u221E`.

## Quy tắc cho Tools

1. Khi chủ thể được xác định là khái niệm **vô cực toán học**, hiển thị `∞`, không dùng `♾️`, `⚭`, `ↀ` thay thế.
2. Không sửa âm thầm ký tự xuất hiện trong nguồn gốc; giữ nguyên `SOURCE_DIRECT` và phân loại quan hệ Unicode tại lớp diễn giải.
3. Khi kiểm thử, so sánh **code point**, không chỉ hình dáng glyph. `♾️` thường là hai code point: `U+267E U+FE0F`.
4. Biểu tượng `∞` không tự cấp quyền, không tạo tài nguyên vô hạn và không chứng minh một công cụ đang chạy.
5. Duy trì lịch sử, không ghi đè các registry hoặc công cụ hiện có; mọi khẳng định đã tích hợp runtime cần bằng chứng hành động và đọc lại.

**Phạm vi cập nhật:** Bổ sung quy ước Unicode trong folder `tools` hiện hành; chưa tự sửa mã nguồn hay thiết lập của các công cụ con.
