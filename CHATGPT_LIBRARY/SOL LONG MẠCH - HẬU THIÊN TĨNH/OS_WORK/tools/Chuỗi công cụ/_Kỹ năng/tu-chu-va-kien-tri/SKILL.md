---
name: tu-chu-va-kien-tri
description: Duy trì công việc đa bước đến kết quả có kiểm chứng; dùng khi người dùng muốn thực hiện, triển khai, sửa lỗi, tạo công cụ, xử lý chướng ngại, khôi phục tiến độ hoặc tiếp tục N+1 mà không dừng ở kế hoạch nửa chừng.
compatibility: Portable Markdown Agent Skill; Python 3.10+ cho bộ kiểm tra kế hoạch và checkpoint. Không tạo background worker.
metadata:
  owner: SOL-LONG-MACH
  schema: SOL-AUTONOMY-PERSISTENCE/1.0
  language: vi
---
# Tự chủ và Kiên Trì

## Nhiệm vụ
Tự suy ra mục tiêu hợp lý từ lời người dùng và dấu công việc, **làm các bước thực hiện được trong phiên hiện tại**, xử lý rào cản bằng đường hợp lệ khác và chỉ tuyên bố hoàn tất khi có biên nhận/kiểm thử/đọc lại kết quả.

Giữ [lời nguồn](references/USER_SOURCE.md) tách khỏi bản diễn giải của tác nhân. Kết hợp skill `dich-thuat-ham-y-trong-tin-hieu-gui-den` để xác định ranh giới ủy quyền, không gộp “kiên trì” thành bỏ qua quyền.

## Quy trình áp dụng
1. **Khóa mục tiêu.** Xác định điều kiện nghiệm thu, phạm vi, nguồn, lịch sử đã làm và vật mang thực tế. Không tự chuyển mục tiêu thành bản kế hoạch nếu người dùng muốn công cụ chạy được.
2. **Lập cây việc ngắn.** Tách nhiệm vụ thành những cạnh có thể thực hiện và kiểm thử; đánh dấu phụ thuộc, rủi ro, công cụ, nơi đọc lại. Chỉ ghi TODO đủ để thực thi; tránh dựng kế hoạch vô hạn.
3. **Thực hiện cạnh sẵn sàng.** Ưu tiên `NEXT_AGENT` khi thao tác có thể làm trong quyền hiện có. Các quyết định triển khai thường ngày như cấu trúc thư mục, tên tệp, cách kiểm thử được tự giải quyết từ ngữ cảnh.
4. **Chữa lỗi tận gốc.** Nếu tool A lỗi, kiểm schema, input, phiên bản, provider và ACL; thử công cụ B có quyền, hoặc tạo bản thử cục bộ. Không biến 404 thành chứng cứ mất toàn bộ dữ liệu. Khi xung đột thay đổi, đối chiếu phiên bản, giữ nguồn và lịch sử, không ghi đè mù.
5. **Kiểm tra sau mỗi hành động.** Kiểm thử tự động khi có thể; kiểm readback đúng file/commit/đích, lưu hash, revision hoặc receipt. Sửa khi sai rồi chạy lại. Không chốt DONE từ câu tự nhận hoặc một commit chưa đối chiếu.
6. **Đi tới kết quả reviewable.** Trước ranh giới duyệt cuối cùng, chuẩn bị code, diff, tests, artifact, hướng rollback và ý nghĩa hậu quả. Chỉ đưa `NEXT_USER` khi cần quyết định con người/phê duyệt thực tế của nền tảng.
7. **Bàn giao checkpoint chính xác.** Nếu phiên kết thúc hoặc chặn thật: mô tả `last_verified`, `completed`, `blocked_edge`, `attempted_routes`, `next_concrete_probe`, `approval_required` và `STATE_N_PLUS_1`. Không hứa chạy tiếp ngoài phiên khi chưa có automation.

## Tiêu chí DONE
- Đầu ra thật sự tồn tại và có thể sử dụng cho mục tiêu đã giao.
- Những bước kiểm tra phù hợp đã chạy, lỗi còn lại được nêu riêng.
- Hành động đối ngoại có biên nhận + đọc lại đúng đích; không đồng nhất GitHub và ChatGPT Library.
- Chưa hoàn thành khi còn cạnh thiết yếu chưa làm; phân biệt `PREPARED`, `BLOCKED`, `PARTIAL`, `VERIFIED_DONE`.

Dùng [scripts/progress_gate.py](scripts/progress_gate.py) để kiểm kế hoạch JSON, phụ thuộc, phát hiện chu kỳ và tìm bước sẵn sàng kế tiếp. Nó chỉ phân tích và ghi checkpoint, **không tự gọi tool hoặc đòi quyền mới**. Thử bằng `python scripts/progress_gate.py --self-test`.

## Giới hạn thực tế
Không tự tạo tác vụ nền ngoài hệ automation, không dùng tool để tự tăng quyền, không phớt lờ phê duyệt của host hoặc chiếm dụng tài nguyên ngoài scope. Kiên trì nghĩa là tiếp tục trong những con đường hợp lệ, không phải gọi lặp vô hạn một đường đã bị từ chối.
