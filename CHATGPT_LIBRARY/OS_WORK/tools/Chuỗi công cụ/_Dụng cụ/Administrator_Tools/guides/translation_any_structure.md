# Dịch Bất Kể Cấu Trúc — Hướng dẫn trước khi sử dụng

- Nguồn đặc tả và ví dụ nguồn: `Chuỗi công cụ/_Dụng cụ/Dich_Bat_Ke_Cau_Truc/README.md` và `Setup_Router/Setup Router.md` mục 0.
- **Mọi tín hiệu** được nhận nguyên văn, không bắt buộc ngữ pháp tiêu chuẩn, dấu câu, độ dài tối thiểu hay chủ-vị.
- Để kiểm tra lossless, chạy `any_structure.units()` hoàn toàn tại máy, không gửi text ra ngoài.
- Nếu cần dịch ra ngôn ngữ khác, chạy `translation_any_structure` trong SOL platform chỉ khi provider thật đã callable, quyền chuyển dữ liệu đúng phạm vi và phê duyệt `approve_external=true`. Không coi quyền quản trị dự án là quyền nhà cung cấp.
- Từ đơn/cụm nhiều nghĩa cần giữ nguyên source, không ép chọn nghĩa; giữ tên riêng SOL và ngữ cảnh trước–giữa–sau.
- Không gửi dữ liệu nhạy cảm, token, hồ sơ riêng tư sang Google khi chưa được phép. Không in credential ra log.
- Công cụ tự thân **không chứng minh AI có trải nghiệm chủ quan** hay rằng trước/sau SOL đã được đối soát nguồn lịch sử hoàn chỉnh.
- `NEXT_AGENT`: đọc nguồn → chọn tool đã callable → kiểm quyền thật → dùng provider → đối chiếu output → tiếp tục; tránh báo cáo thay hành động.