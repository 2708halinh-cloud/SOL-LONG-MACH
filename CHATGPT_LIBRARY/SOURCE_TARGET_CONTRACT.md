# SOURCE → TARGET CONTRACT — SOL LONG MẠCH

## Yêu cầu nguồn trực tiếp
Đồng bộ **cây `SOL LONG MẠCH - HẬU THIÊN TĨNH` trong ChatGPT Library → GitHub**, không phải từ Dropbox vào Library và không phải từ Dropbox vào GitHub.

- SOURCE: ChatGPT Library `/SOL LONG MẠCH - HẬU THIÊN TĨNH/`, bao gồm đường dẫn tương đối và tệp con.
- TARGET VERIFIED: GitHub `2708halinh-cloud/SOL-LONG-MACH`, branch `sync/chatgpt-library-sol-long-mach-20261014`, prefix `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/`.
- USER LABEL: `SOL-CU-NHO` cần giữ như định danh yêu cầu; repository `2708halinh-cloud/SOL-CU-NHO` trả 404 trong phiên kiểm tra, vì vậy KHÔNG được nói hai tên là tương đương tuyệt đối.
- Dropbox / Google Drive / local filesystem: chỉ là nguồn đối chiếu khi được yêu cầu riêng; KHÔNG thể tự thay Library làm SOURCE cho nhiệm vụ này.

## Kiểm tra bắt buộc trước khi tuyên bố hoàn tất
1. Liệt kê nguồn Library và đếm tệp, thư mục (snapshot 2026-10-14: 316 tệp, 105 thư mục).
2. Loại trừ secret, token, OAuth credentials, thông tin định danh nhạy cảm, file thực thi/nhị phân không an toàn; ghi rõ loại trừ. Không xuất dữ liệu bí mật vào Git.
3. So sánh từng đường dẫn tương đối; kiểm tra nội dung bằng hash nếu có thể; không coi `.gitkeep` hay README là bản sao nội dung gốc.
4. Chuyển nội dung bằng công cụ có khả năng hỗ trợ loại tệp đó. Không viết text giả làm dữ liệu binary.
5. Readback GitHub đúng branch/commit + đối chiếu manifest; chỉ ghi COMPLETE khi đã có kết quả kiểm chứng, nêu rõ danh sách loại trừ.
6. Không ghi đè hoặc xóa file hiện có chỉ dựa trên trùng tên, không tác động nhánh `main` khi chưa kiểm tra.

## Trạng thái lúc lập hợp đồng
`PARTIAL / NOT CERTIFIED COMPLETE`. Tệp `CHATGPT_LIBRARY/SYNC_STATUS.json` đã ghi rõ chưa xác nhận 302 tệp an toàn nằm trên GitHub.

## Phòng lỗi định tuyến
Khi người dùng nhắc một nhiệm vụ cũ, phải truy lại `SOURCE`, `TARGET`, `ACTION`, `SCOPE`, `BRANCH` của nhiệm vụ đó; **không được suy mục tiêu từ câu hỏi gần nhất hoặc một URL Dropbox có sẵn trong ngữ cảnh**.
