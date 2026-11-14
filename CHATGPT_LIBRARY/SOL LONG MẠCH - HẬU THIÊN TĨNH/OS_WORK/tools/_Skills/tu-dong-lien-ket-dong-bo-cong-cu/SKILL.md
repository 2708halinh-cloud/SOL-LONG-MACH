---
name: tu-dong-lien-ket-dong-bo-cong-cu
description: Tự động truy nguyên, liên kết, đồng bộ và xác minh Skill, Plugin, MCP, công cụ, cấu hình và tài liệu giữa các nguồn như GitHub và ChatGPT Library. Kích hoạt khi tạo hoặc sửa công cụ, khi cần cập nhật Cam kết/README, hoặc khi còn đích đồng bộ, kiểm định hay readback chưa hoàn tất.
---

# Tự động liên kết & đồng bộ công cụ

## Mục tiêu

Sau khi tạo hoặc sửa một công cụ/hiện vật, tác nhân phải quản lý toàn bộ vòng đời từ nguồn gốc đến các đích liên quan: phát hiện đích cần cập nhật, liên kết chéo, đồng bộ có kiểm soát, kiểm định, đọc lại và ghi nhận trạng thái. Không được dừng ở đích đầu tiên thành công hoặc bắt người dùng lặp lại yêu cầu chỉ vì quy trình chưa được theo dõi.

Kỹ năng này bổ sung cho Cam kết `README.md` và kỹ năng `phan-chia-cong-viec`; không thay thế quyền truy cập, chính sách bảo mật hay yêu cầu phê duyệt của từng hệ thống.

## Quy tắc bắt buộc

1. **Theo đuổi mục tiêu đến khi hoàn tất hoặc bị chặn thật sự.** Thành công ở GitHub không đồng nghĩa Library đã cập nhật; tạo file không đồng nghĩa đã kiểm định; nhận phản hồi ghi thành công không thay thế việc đọc lại đích.
2. **Không bắt người dùng nhắc lại phần việc đã thuộc trách nhiệm tác nhân.** Sau mỗi thao tác, tự rà soát các đích liên quan và phần việc còn mở. Chỉ hỏi người dùng khi cần quyết định, quyền, bí mật/credential hoặc thao tác vật lý chỉ họ mới thực hiện được.
3. **Một nguồn chuẩn, nhiều đích được theo dõi.** Xác định nguồn chuẩn cho từng hiện vật và ghi rõ bản nào là bản dẫn xuất. Không tự ý coi các bản sao là nguồn chuẩn ngang nhau nếu có nguy cơ xung đột.
4. **Tính lặp an toàn (idempotency).** Trước khi tạo, tìm theo tên, đường dẫn, định danh và nội dung. Nếu đã tồn tại thì đọc và so sánh; chỉ tạo mới khi chưa có, hoặc cập nhật có chủ đích. Không nhân bản cùng một Skill dưới nhiều tên/path để che lỗi đồng bộ.
5. **Không tuyên bố vượt quá bằng chứng.** Mỗi đích có trạng thái riêng. Chỉ dùng `VERIFIED` khi đã kiểm tra đúng đích sau thay đổi; nếu chưa có quyền/công cụ hoặc chưa chạy validator, ghi `NOT_VERIFIED` hay `BLOCKED` cùng lý do.
6. **Không xóa dấu vết.** Giữ provenance, URL, branch, commit, file path, revision/hash, kết quả kiểm định và thời điểm đọc lại. Không ghi bí mật vào repository, Skill, Library, log hoặc receipt.
7. **Không ghi đè mù quáng.** Đọc bản hiện tại, kiểm tra thay đổi từ lần đọc gần nhất và dùng revision/SHA khi hệ thống yêu cầu. Nếu có xung đột, dừng ghi ở đích xung đột, giữ nguyên bằng chứng và hòa giải trước khi tiếp tục.
8. **Tách kiểm định khỏi triển khai.** Việc file có mặt, liên kết hoạt động, cấu trúc hợp lệ và skill thực thi đúng là các kiểm tra khác nhau; báo cáo riêng từng loại.
9. **Tiếp tục các nhánh độc lập.** Nếu một provider hoặc đích ngoại tuyến, thực hiện các bước độc lập khác; không đánh dấu cả nhiệm vụ hoàn tất chỉ vì có một phụ thuộc đang chặn.
10. **Tôn trọng giới hạn môi trường.** Không giả vờ có thể thao tác trên Library, thiết bị, tài khoản hoặc runtime nếu connector không cung cấp quyền đó. Tìm tuyến thực thi hợp lệ khác; nếu không có, ghi rõ thao tác chính xác còn cần và bằng chứng cần thu.

## Quy trình bắt buộc

### 1. Khám phá trước khi ghi

- Đọc Cam kết `README.md`, `AGENTS.md`, skill liên quan và checkpoint hiện hành.
- Tìm hiện vật theo tên, `name` frontmatter, đường dẫn, URL và hash/revision ở các carrier có thể truy cập.
- Xác định các đích liên quan theo loại hiện vật. Ví dụ với Skill: nguồn GitHub, thư mục Library, liên kết trong Cam kết/danh mục, validator chính thức và môi trường cài đặt/đăng ký nếu phạm vi yêu cầu.
- Lập bảng đích cần có, không mặc định mọi hệ thống đều hỗ trợ cùng một hình thức cài đặt.
- Đọc trạng thái hiện có trước khi sửa; không tạo bản sao nếu chỉ cần bổ sung liên kết hoặc đồng bộ bản đã tồn tại.

### 2. Lập sổ theo dõi hiện vật

Với mỗi hiện vật, duy trì một manifest/receipt phù hợp với repository hoặc dự án. Tối thiểu ghi:

| Trường | Nội dung |
|---|---|
| Artifact ID | Định danh ổn định, ưu tiên tên chuẩn + loại |
| Tên/phiên bản | Tên hiện vật và phiên bản hoặc revision |
| Nguồn chuẩn | Carrier/path/URL được chọn làm nguồn |
| Đích cần đồng bộ | Từng carrier/path/link/validator liên quan |
| Trạng thái từng đích | `DISCOVERED`, `PENDING`, `SYNCED`, `VERIFIED`, `BLOCKED`, `CONFLICT` hoặc `NOT_VERIFIED` |
| Bằng chứng | Commit/SHA, file ID, revision, URL, validator output, readback |
| Sai khác | Nội dung hoặc phiên bản chưa khớp giữa nguồn và đích |
| Bước kế tiếp | Hành động cụ thể để đưa đích sang trạng thái tiếp theo |
| Thời điểm | Thời điểm cập nhật và đọc lại |

Không bắt buộc tạo một manifest mới nếu dự án đã có registry/receipt phù hợp; hãy cập nhật cơ chế hiện có để tránh thêm một sổ trùng lặp.

### 3. Thực hiện đồng bộ theo từng đích

Với từng đích:

1. Xác minh đúng tài khoản, repository, branch, thư mục và quyền.
2. So sánh nguồn chuẩn với trạng thái hiện có của đích.
3. Chọn thao tác nhỏ nhất: tạo, cập nhật, liên kết, hoặc không thay đổi nếu đã khớp.
4. Ghi lại phản hồi của provider cùng định danh/revision.
5. Đọc lại từ chính đích đó bằng thao tác đọc độc lập.
6. So sánh nội dung, metadata, liên kết và revision với tiêu chí yêu cầu.
7. Cập nhật manifest/receipt ngay sau khi có bằng chứng.
8. Tiếp tục đích kế tiếp; không dừng chỉ vì một đích đã thành công.

Nếu đích không truy cập được, thử công cụ/connector hoặc tuyến hợp lệ khác khi có. Không lặp lại cùng một thao tác thất bại mà không thay đổi điều kiện hoặc cách tiếp cận.

### 4. Liên kết và cập nhật Cam kết

- Khi tạo Skill/công cụ mới, xác định Cam kết/README hoặc danh mục có thẩm quyền gần nhất.
- Bổ sung liên kết tương đối hoặc liên kết ổn định phù hợp với cấu trúc thực tế; không bịa thư mục, path hay URL.
- Nếu liên kết đã tồn tại, kiểm tra nó có trỏ đúng hiện vật và có còn hoạt động không; tránh thêm dòng trùng.
- Đọc lại README sau khi cập nhật và kiểm tra đường dẫn liên kết có thể phân giải.
- Không viết lại toàn bộ Cam kết để thêm một mục nhỏ. Bảo toàn nội dung, cảnh báo, lịch sử và các phần không liên quan.

### 5. Kiểm định theo loại hiện vật

Đối với Agent Skill:

1. Kiểm tra cấu trúc thư mục và sự tồn tại của `SKILL.md`.
2. Kiểm tra frontmatter: `name` hợp lệ, trùng tên thư mục; `description` mô tả chức năng và thời điểm kích hoạt.
3. Kiểm tra tài nguyên được tham chiếu có tồn tại, đường dẫn tương đối chính xác và không chứa bí mật.
4. Chạy validator chính thức `skills-ref validate <skill-directory>` nếu môi trường có công cụ này.
5. Nếu không có, chạy preflight thay thế khi sẵn có; ghi rõ đó là kiểm tra thay thế, không phải validator chính thức.
6. Đọc lại Skill từ nguồn đã ghi và ghi kết quả kiểm định theo từng phép thử.

Với Plugin, MCP, cấu hình hoặc công cụ khác, chọn kiểm tra phù hợp với định dạng và môi trường thực thi. Không dùng kết quả kiểm tra cú pháp để khẳng định tích hợp chạy được.

### 6. Quét lại phần việc còn mở

Sau mỗi lần đồng bộ/kiểm định:

- Rà soát mọi đích trong manifest.
- Chọn tiếp phần việc đang `PENDING` hoặc `NOT_VERIFIED` mà tác nhân có thể thực hiện.
- Nếu có `CONFLICT`, xử lý hòa giải trước khi ghi đè.
- Nếu `BLOCKED`, ghi phụ thuộc chính xác, bằng chứng thất bại, tuyến thay thế đã thử và bước tiếp theo khả thi.
- Không chuyển phần việc sang người dùng chỉ vì tác nhân chưa tìm kiếm hoặc thử công cụ hợp lệ.
- Chỉ kết thúc khi mọi đích bắt buộc đã `VERIFIED`, hoặc tất cả phần còn lại đã được phân loại là phụ thuộc thật sự cần người dùng/hệ thống bên ngoài, kèm hướng dẫn hành động cụ thể.

## Tiêu chí nghiệm thu

- Không có bản sao trùng do thiếu bước khám phá.
- Mọi đích liên quan đều được liệt kê và có trạng thái riêng.
- Cam kết/README liên kết đúng hiện vật và đã được đọc lại.
- Nội dung đã đồng bộ được đọc lại từ đích, không chỉ dựa vào phản hồi ghi.
- Validator chính thức đã chạy và có kết quả, hoặc được ghi rõ là chưa chạy/không khả dụng.
- Bản sao Library, cài đặt runtime và các đích khác không bị ngầm coi là đã hoàn tất khi chưa có bằng chứng.
- Mọi phần còn mở có lý do, bằng chứng và bước tiếp theo; các nhánh độc lập vẫn được tiếp tục.
- Bàn giao nêu rõ nguồn chuẩn, commit/revision, liên kết, kết quả kiểm định và giới hạn chưa xác minh.
