# MCP — Nguồn hướng dẫn tác nhân thiết lập MCP

## Nguồn do người dùng chỉ định

https://github.com/mcp

## Mục đích

Dùng đường dẫn trên làm điểm khởi đầu để tác nhân tìm hiểu, chọn, thiết kế, cấu hình và kiểm chứng các MCP server phù hợp với hệ SOL/GGDV.

## Quy trình tác nhân thiết lập MCP

1. **SOURCE_DIRECT:** Mở nguồn trên, xác định chính xác repository/server định dùng và đọc README, tài liệu cài đặt, giấy phép, các ví dụ cấu hình có liên quan. Không mặc định mọi repository đều là MCP server hoạt động.
2. **Đối chiếu môi trường:** Kiểm tra MCP client đích, loại vận chuyển mà server thực sự hỗ trợ (ví dụ `stdio` hoặc Streamable HTTP nếu tài liệu nguồn có ghi), hệ điều hành, runtime và dependencies. Không tự bịa câu lệnh cài đặt hay tham số.
3. **Thiết lập:** Từ hướng dẫn của *server đã chọn*, cấu hình lệnh chạy hoặc URL endpoint, tên server và quyền được cấp cho công cụ. Giữ token, PAT, OAuth, mật khẩu trong secret store hoặc biến môi trường được bảo vệ; không ghi bí mật vào README, SKILL.md, repository hoặc log.
4. **Kiểm chứng kết nối:** Xác thực danh tính/phiên nếu server yêu cầu; thực hiện MCP `initialize` và `tools/list` bằng client/công cụ hiện có, ghi nhận tên công cụ thật mà server công bố. Chỉ thử thao tác ghi khi có yêu cầu cụ thể.
5. **T007 READBACK:** So sánh trạng thái cấu hình với kết quả gọi công cụ thực tế, lưu dấu vết nguồn, tên server, công cụ, thời điểm và lỗi (nếu có) mà không chứa credential. Không đồng nhất “đã lưu hướng dẫn” với “đã cài/kết nối MCP”.

## Phân biệt phạm vi

- Đây là **đường dẫn học hỏi/thiết kế/cấu hình** do người dùng cung cấp, chưa phải xác nhận rằng mọi MCP trên trang đều hợp lệ hay đã được cài đặt.
- Với mỗi server, phải dùng đúng hướng dẫn, phiên bản, yêu cầu xác thực và khả năng thực tế của nguồn được chọn.
- Giữ nguyên cây thư mục Library hiện hành; không tự tạo ROOT mới, không thay thế thư mục `_Tool`.

Ghi nhận: 2026-10-14. Trạng thái tham khảo: URL do người dùng cung cấp; nội dung trực tuyến chưa được kiểm chứng trong phiên này.
