---
name: phan-chia-cong-viec
description: Phân rã mục tiêu thành các phần việc có chủ thể chịu trách nhiệm, phụ thuộc, thứ tự thực hiện, tiêu chí nghiệm thu và bằng chứng hoàn thành. Kích hoạt khi lập kế hoạch, giao việc, điều phối nhiều tác nhân/công cụ, xử lý nhiều nhánh song song hoặc bổ sung quy trình cho Cam kết (README.md).
---

# Phân chia công việc

## Mục đích

Bổ sung cho **Cam kết (README.md)** bằng một quy trình biến mục tiêu thành các phần việc có thể thực hiện, kiểm tra và tiếp nối. Kỹ năng này không thay thế Cam kết, AGENTS.md, quyền truy cập hay quy tắc an toàn của môi trường.

## Nguyên tắc

1. **Đọc nguồn trước khi chia việc.** Tìm Cam kết README.md, AGENTS.md, checkpoint hiện hành, nguồn nhiệm vụ và hiện vật liên quan. Phân biệt điều đã quan sát, điều suy luận và điều chưa biết.
2. **Giữ đúng vai trò.** Người thiết kế xác định mục tiêu, nguyên tắc, phạm vi và tiêu chí nghiệm thu. Tác nhân thực thi phân tích nguồn, lập cách làm, triển khai, kiểm thử và đọc lại kết quả; chỉ hỏi người thiết kế khi thiếu quyết định, quyền hoặc thao tác thực sự thuộc về họ.
3. **Chia theo kết quả có thể nghiệm thu.** Mỗi phần việc phải tạo ra một thay đổi, hiện vật, quyết định hoặc bằng chứng cụ thể; không chia chỉ theo tên công cụ hoặc hoạt động chung chung.
4. **Giữ quan hệ phụ thuộc.** Xác định việc nào phải hoàn tất trước, việc nào có thể chạy song song, việc nào chặn riêng một nhánh và việc nào thực sự chặn toàn mục tiêu.
5. **Không đánh đồng báo cáo với hoàn thành.** Chỉ đánh dấu hoàn thành khi có hành động đúng đích, biên nhận phù hợp, hậu quả quan sát được và đọc lại đích. Nếu thiếu một mắt xích, ghi chính xác phần đã xác minh và phần còn mở.
6. **Tiếp tục sau mỗi lát cắt.** Sau mỗi lần đọc lại, quét lại các phần việc chưa xong và chọn phần tiếp theo còn khả thi. Một phần việc hoàn thành, một lỗi hoặc một connector ngoại tuyến không tự động kết thúc toàn bộ nhiệm vụ.
7. **Bảo toàn nguồn và lịch sử.** Trước thay đổi rủi ro, xác định đúng đích, quyền, bản sao/khả năng khôi phục và tác động. Không ghi đè hoặc xóa nguồn độc nhất khi chưa có cơ sở an toàn; không ghi bí mật vào Git hoặc nhật ký.
8. **Không bịa trạng thái.** Phân biệt PLANNED, IN_PROGRESS, BLOCKED_ON_DEPENDENCY, VERIFIED và NOT_VERIFIED trong bảng công việc; các nhãn chỉ là cách trình bày, không thay thế bằng chứng.

## Quy trình thực hiện

### 1. Xác lập mục tiêu và nguồn

- Viết mục tiêu thành một câu có thể kiểm chứng.
- Xác định nguồn chỉ đạo, Cam kết README.md, AGENTS.md, đích tác động và trạng thái/checkpoint hiện tại.
- Ghi rõ phạm vi bao gồm, phạm vi không được tự ý mở rộng và điều kiện nghiệm thu.
- Nếu có xung đột giữa nguồn, giữ nguyên lịch sử và tìm nguồn có thẩm quyền hơn; không âm thầm chọn một giả định.

### 2. Phân rã thành phần việc

Mỗi phần việc nên có các trường sau:

| Trường | Nội dung cần ghi |
|---|---|
| ID | Mã duy nhất trong kế hoạch, ví dụ W-01 |
| Kết quả | Hiện vật hoặc thay đổi cụ thể phải tạo ra |
| Chủ thể | Tác nhân/nhóm chịu trách nhiệm thực hiện và xác minh |
| Phụ thuộc | ID các việc phải có trước; ghi NONE nếu độc lập |
| Đích và nguồn | Đường dẫn, repo, dịch vụ hoặc vật mang chính xác |
| Phương pháp | Các thao tác cần làm và công cụ phù hợp |
| Tiêu chí nghiệm thu | Điều kiện quan sát được để chấp nhận kết quả |
| Bằng chứng | Receipt, kiểm thử, hash/revision hoặc kết quả đọc lại cần thu |
| Rủi ro/rollback | Rủi ro chính và cách khôi phục nếu cần |
| Trạng thái | Trạng thái hiện tại cùng lý do và bằng chứng |

Chia nhỏ thêm nếu một phần việc có nhiều đích độc lập, tiêu chí nghiệm thu không rõ, hoặc thất bại của nó sẽ che khuất tiến độ các nhánh khác. Không chia vụn đến mức mỗi bước nhỏ trở thành một nhiệm vụ độc lập vô ích.

### 3. Xác định thứ tự và khả năng song song

- Dựng đồ thị phụ thuộc từ các ID công việc.
- Ưu tiên khảo sát chỉ đọc, kiểm tra quyền và xác minh đích trước thao tác ghi hoặc thay đổi khó đảo ngược.
- Chỉ chạy song song khi các nhánh không tranh chấp cùng tệp, trạng thái, tài nguyên hoặc quyền.
- Nếu có xung đột ghi, chỉ định một chủ thể sở hữu đích hoặc tách thành các thay đổi nhỏ có thể hợp nhất an toàn.
- Khi một nhánh bị chặn, tiếp tục nhánh độc lập; ghi rõ phụ thuộc cụ thể khiến nhánh đó chưa thể tiến triển.

### 4. Thực thi và kiểm chứng

Với từng phần việc:

1. Đọc lại nguồn và đích ngay trước thao tác khi trạng thái có thể đã thay đổi.
2. Kiểm tra quyền và chọn công cụ có thể thực hiện đúng thao tác.
3. Thực hiện thay đổi nhỏ nhất đáp ứng mục tiêu.
4. Thu biên nhận từ hệ thống/provider nếu có.
5. Kiểm tra hậu quả thực tế ở đúng đích; đọc lại nội dung hoặc trạng thái đã thay đổi.
6. Chạy kiểm thử phù hợp; phân biệt kiểm thử cục bộ, mô phỏng và kiểm thử trên môi trường thật.
7. Ghi bằng chứng, giới hạn còn lại và các phần việc phát sinh.
8. Quét lại đồ thị phụ thuộc và tiếp tục phần việc khả thi kế tiếp.

### 5. Quản lý phần việc còn mở

Phân loại mỗi phần việc chưa hoàn tất thành:

- **Tác nhân tự thực hiện được:** còn công cụ/quyền và bước an toàn có thể làm ngay — tiếp tục thực hiện.
- **Phụ thuộc người thiết kế:** cần lựa chọn, quyết định phạm vi hoặc tiêu chí chỉ người thiết kế mới có thể xác lập — hỏi đúng một câu hỏi cụ thể.
- **Phụ thuộc môi trường/vật mang:** dịch vụ, thiết bị, credential hoặc connector chưa truy cập được — tìm tuyến thay thế hợp lệ; nếu chưa có, ghi chính xác phép kiểm cần thiết và tác động của việc chặn.
- **Chờ kiểm chứng:** đã tạo hiện vật nhưng chưa có kiểm thử, receipt, hậu quả hoặc readback đủ — không tuyên bố hoàn thành.

Không chuyển việc thuộc trách nhiệm tác nhân sang người thiết kế chỉ vì chưa thử các công cụ hoặc tuyến thay thế hợp lệ.

### 6. Bàn giao

Bản bàn giao phải gồm:

- Mục tiêu và nguồn chính.
- Các phần việc đã xác minh, kèm liên kết/định danh hiện vật và bằng chứng.
- Các phần việc còn mở, nguyên nhân và bước tiếp theo khả thi.
- Những quyết định hoặc thao tác duy nhất cần người thiết kế thực hiện.
- Các rủi ro, thay đổi chưa kiểm thử và phương án khôi phục.
- Mốc/checkpoint để lần thực thi sau có thể tiếp tục mà không làm lại phần đã có bằng chứng.

Chỉ kết thúc khi không còn phần việc tự thực hiện được trong phạm vi đã giao, hoặc khi có phụ thuộc thật sự cần người thiết kế xử lý và đã nêu rõ hành động cụ thể đó.

## Tiêu chí nghiệm thu của kỹ năng

- Mỗi phần việc có kết quả và tiêu chí nghiệm thu cụ thể.
- Quan hệ phụ thuộc và nhánh song song được thể hiện rõ.
- Chủ thể chịu trách nhiệm không mơ hồ.
- Trạng thái được hỗ trợ bằng chứng, không chỉ bằng lời báo cáo.
- Phần việc bị chặn không làm dừng các nhánh độc lập.
- Có đọc lại đích, ghi checkpoint và nêu rõ phần chưa xác minh.
- Không sửa hoặc thay thế nội dung Cam kết README.md ngoài phạm vi bổ sung đã yêu cầu.
