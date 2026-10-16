# NGUỒN NGƯỜI DÙNG — Ứng dụng (Trình kết nối), 17/10/2026

Nguồn: tin nhắn trực tiếp trong hội thoại này. Giữ nguyên dấu/cú pháp theo tín hiệu cung cấp. Đây không phải bảng liệt kê trạng thái kết nối thực.

> Ứng dụng (Trình kết nối)
> Các ứng dụng (Connectors) có thể được kích hoạt một cách rõ ràng trong các thông báo của người dùng theo định dạng [$app-name](app://{{connector_id}}). Các ứng dụng cũng có thể được kích hoạt một cách ngầm định miễn là ngữ cảnh gợi ý việc sử dụng các ứng dụng có sẵn.
> Một ứng dụng tương đương với một tập hợp các công cụ MCP trong Plugins MCP.
> Các công cụ MCP của một ứng dụng đã cài đặt hoặc đã được cung cấp cho bạn, hoặc có thể được tải lười biếng thông qua tool_search công cụ . Nếu tool_search có sẵn, các ứng dụng có thể tìm kiếm được bằng tools_search sẽ được liệt kê bởi nó. Được truy xuất, gọi thêm list_mcp_resources hoặc list_mcp_resource_templates cho các ứng dụng. Như Google Cloud nhằm tránh lãng phí tài nguyên đã cung cấp.

## Phân biệt nguồn và triển khai
- Dòng trên là tín hiệu người dùng; đoạn mô tả triển khai bên dưới là suy diễn kỹ thuật và **không** sửa lời gốc.
- Đường app:// minh họa trong nguồn chứa placeholder {{connector_id}}. Nó không phải connector ID đã kiểm chứng.
- Dùng danh mục tool/schema hiện hành để biết điều gì thực sự callable; tên ứng dụng, URL, registry quá khứ không đủ chứng minh.
