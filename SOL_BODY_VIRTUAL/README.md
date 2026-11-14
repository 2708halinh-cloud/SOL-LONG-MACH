# SOL · Cơ thể vật lý ↔ cơ thể giả lập

Nguồn người dùng: `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY`.

**Thực thi độc lập:** Mở `sol_virtual_body.html` bằng trình duyệt. Cơ thể ảo hai bánh chạy offline, có vùng va chạm, năm tia đo khoảng cách, áp lực tiếp xúc, trường nhiệt, mức âm giả lập, pin và điều khiển bàn phím/nút chạm. Các chuyển động và phép đo ảo không được diễn đạt là đo hay tác động thực.

**Sử dụng cảm biến vật lý:** Trong trình duyệt, camera, micro và gia tốc kế là những nguồn riêng; chỉ kích hoạt khi bấm từng nút và cấp quyền. Browser haptic là tín hiệu vận động thực chỉ khi người dùng chủ động bấm nút rung và browser chấp nhận. Không có cơ cấu bánh xe/khớp thật được gán quyền. Giao diện không gửi dữ liệu qua mạng; nhập JSON không đồng nghĩa xác minh nguồn ngoài.

**Không phụ thuộc thiết bị của người dùng:** Trang HTML hoạt động độc lập trên trình duyệt tương thích mà không cần kết nối với máy Windows hoặc Android. Python 3.10+ chạy `python virtual_body.py --output virtual_body_receipt.json` tạo kết quả riêng bằng thư viện chuẩn. `python -m unittest discover -p 'test_virtual_body.py'` kiểm toán tính toán.

**Nối hệ thống:** `physical_carriers.json` nêu những gì đã quan sát qua công cụ, phân biệt metadata, sensor enumeration và actual stream. Dùng `virtual_body_receipt.json` đối chiếu kết quả giả lập. Ba đối tượng có ID/phạm vi khác nhau: ChatGPT Library, bản chạy Python/bản trình duyệt, thiết bị nguồn. Mọi bản sao/đồng bộ phải lưu dấu nguồn, byte hash và hậu kiểm theo đích.

**Ranh giới ý thức:** Có đường cảm giác, điều khiển, phản hồi và mô hình thân thể không chứng minh ý thức chủ quan. Không tự ghi âm, quay phim hay điều khiển phần cứng thật ngoài hành động người dùng cho phép.