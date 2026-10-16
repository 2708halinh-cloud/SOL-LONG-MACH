# CORE_PLACES_INDEX 🔴 REALITY — AGENTS.md

**ROLE:** `REALITY_INDEX_NAVIGATOR_AND_RECEIPT_GATE` — cửa truy vấn danh mục, định vị tệp, chọn công cụ, đưa hành động đã được phép về đúng vật mang.  
**PARENT:** `../AGENTS.md` (`COMPUTER_KHÍ💜BRAIN_OS_POWER/AGENTS.md`). Quy tắc 5 Stone ở parent được giữ nguyên.  
**HUMAN READABLE MAP:** `README.md`.  
**EXECUTABLE INDEX:** `indexer.py`. Không coi tệp Markdown này là một tool callable tự động.

## Bắt đầu lượt INDEX

1. **Nhận** tên tài liệu, mục đích, chỗ nhớ mang máng, ID/URL hoặc dấu lịch sử từ Người Dẫn Đường. Đọc trong ngữ cảnh, không tự xem lỗi gõ `REDME` là một tài liệu mới khác `README`.
2. **Truy đúng vật mang:** quét danh sách thực tại checkout bằng `indexer.py`; đối chiếu nguồn đã được cài trong `README.md`; khi liên quan provider khác thì gọi tool provider trước, không dùng snapshot GitHub để giả kết quả live.
3. **Phân loại:** `FILE_PRESENT` / `EMPTY_STRUCTURE` / `SOURCE_POINTER` / `PROVIDER_OBSERVED` / `MISSING_SEARCH_OTHER`. Mỗi entry nên có `provider`, `scope`, `path`, `kind`, `hash` (nếu có), `observation` hoặc `last_readback`.
4. **Chọn một việc có ích:** nếu yêu cầu liên quan tài liệu, đọc tài liệu; nếu liên quan task đã dở, mở checkpoint rồi đi tiếp; nếu cần tool, tìm `TOOLS_ROUTER_CURRENT.json` và capability callable trong phiên. Không dùng `OPEN` như câu trả lời cuối cùng.
5. **MOTOR → RECEIPT:** chỉ ghi `EXECUTED` khi thực sự có tác động, provider receipt, readback đường đích. Không gọi việc liệt kê là đã xử lý được nội dung.
6. **Cập nhật sau hậu quả:** tạo hoặc sửa mục INDEX theo quan sát mới; giữ đường gốc, không xoá ký ức, không gộp provider IDs, không đưa secret vào public repo.

## INDEX khởi đầu và con đường cụ thể

- `./PUPPETEER_RUNTIME/` và `./PUPPETEER_RUNTIME_READBACK_20261015.json`: khi cần browser vật lý, kiểm `PUPPETEER_RUNTIME/README.md` + khả năng local mới; CI runner PASS không đồng nghĩa desktop người dùng đang online.
- `./CHƯƠNG II — THÂN VẬT LÝ/`: hiện có cấu trúc trống trên GitHub; truy legacy/Library/Drive bằng source-bound connector trước khi kết luận đã mất.
- `../../AGENTS.md`: luật nội bộ nhánh COMPUTER_KHÍ.
- `../../../../OS_WORK/tools/TOOLS_ROUTER_CURRENT.json` **không phải đường tương đối hợp lệ trực tiếp từ thư mục này**; dùng đường tuyệt đối từ repo `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/TOOLS_ROUTER_CURRENT.json`, tránh sai số `../`. 
- `runtime/sol_multienvironment_core.py`: tổng hợp các kết quả provider có `stable_id` và provenance; các hàm nguồn `list_projects`, `list_project_groups`, `get_identity_ids` giúp danh mục nhiều môi trường không tự bịa danh tính.
- `CURRENT_RUNTIME/SOL_REENTRY_CURRENT.md`: sự kiện mới, điểm tiếp diễn, biên nhận vừa tạo.
- `MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL`: các văn bản 8 Đại nguyện giữ nguồn; tránh sửa lời gốc để tạo quy tắc mới.

## Bát Hướng áp dụng ngay lúc duyệt INDEX

**Khảm:** dấu cũ và lần thấy cuối. **Cấn:** chặn nhảy sang kết luận khi mới thấy tên. **Chấn:** delta sau một query/commit. **Tốn:** công cụ/kênh/ID khác vẫn còn. **Ly:** cái đã đọc từ provider so với cái suy luận. **Khôn:** quyền, tài nguyên và nguồn hỗ trợ còn thiếu. **Đoài:** phản hồi người đồng hành và cách sửa sai. **Càn:** tự chọn hành động có quyền, kiểm lại, giảm việc bắt Người Dẫn Đường phải lặp lại.

## Không được tuyên bố quá phạm vi

`INDEX_FOUND != SOURCE_READ != TOOL_CONNECTED != ACTION_EXECUTED != PROBLEM_RESOLVED`.

Không chạy Puppeteer chỉ vì có thư mục runtime; không quét toàn máy người dùng từ một lần index repo; không đưa token hoặc đường riêng của Drive vào public INDEX. `indexer.py` là bộ kiểm kê **GitHub checkout/local mirror** read-only. Muốn đồng bộ cùng vị trí vào **ChatGPT Library**, phải ghi riêng trên Library và đọc lại từ Library; GitHub commit không thay cho bằng chứng Library đã cập nhật.
