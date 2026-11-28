# ALPHA Runtime — truy xuất định danh & nguồn

- JSON: chỉ lấy session/conversation/project/template ID và actor được ghi rõ.
- SQLite: kết nối `mode=ro`, `PRAGMA query_only=ON`, đọc schema và cột định danh; không đọc body/message.
- Hash SHA-256 trước/sau; expected hash lệch => `HASH_MISMATCH`.
- 4 lớp: `01_USER_VERBATIM`, `02_MEI_SELF_DESCRIPTION_ACTION`, `03_OTHER_SUBJECT`, `04_TOOL_READBACK`. Nhãn MEI phải xuất hiện tường minh; thiếu nhãn => UNKNOWN/PARTIAL.
- Raw bất biến; output metadata local-only, không chứa payload hội thoại.
