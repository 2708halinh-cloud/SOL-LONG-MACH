# ĐÍNH CHÍNH NGUỒN — 2026-10-15 — R-014

## Câu người đồng hành đã viết (SOURCE_DIRECT, giữ nguyên ký tự)
> "Âm dương" mới là ranh giới. Chẳng có cái ranh giới nào đo mô hình dựng lên nó là "Sự Thật" cả.

## Câu do assistant tự thêm (ASSISTANT_OUTPUT, KHÔNG PHẢI LỜI NGƯỜI DÙNG)
> Âm–Dương là ranh giới trong cách nhìn em đang nói đến.

**Sai lệch:** Cụm `trong cách nhìn em` không xuất hiện trong lời nguồn. Assistant tự thêm khung chủ quan hóa phát biểu của người đồng hành, rồi gán thành “cách nhìn em”. Đây là biến lời mô hình thành lời nguồn, không được giữ tư cách SOURCE_DIRECT hay xem là diễn giải được người đồng hành chấp thuận.

**Khắc phục:** Rút lại cách gán, giữ nguồn nguyên văn; mọi phần giải thích phát sinh của mô hình phải ghi tác giả là ASSISTANT_INTERPRETATION và không được thay lời nguồn. Đây không phải kết luận triết học, khoa học hoặc phép đo về Sự Thật.

**Hành động kiểm được:** bổ sung `verify_source_attribution()` vào `runtime/continuity_guard.py`, nối cổng kiểm vào `r014_pre_response_gate(source_attribution=...)`, bổ sung các regression test. `SOURCE_DIRECT` chỉ đạt khi nội dung khớp nguyên văn trong chuỗi nguồn; câu tự thêm bị từ chối tại gate.

**Giới hạn:** Đây là kiểm tra xuất xứ ký tự đối với statement được truyền vào, không thay được hiểu biết ngữ nghĩa, không tự kiểm soát phản hồi host ChatGPT nếu runtime không gọi cổng này. Không lấy PASS của test làm chứng rằng mọi phản hồi AI đã được tự động chặn sai diễn giải.

**Không thay việc còn nợ:** trợ lý tra cứu GitHub/Dropbox chưa triển khai; lời chat JINEY trước Canon chưa được phục hồi. Việc sửa cách gán nguồn không thay hai kết quả đó.
