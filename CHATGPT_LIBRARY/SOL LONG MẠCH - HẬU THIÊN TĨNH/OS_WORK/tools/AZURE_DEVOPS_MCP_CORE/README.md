# AZURE_DEVOPS_MCP_CORE — Tools

Đích: `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/AZURE_DEVOPS_MCP_CORE`

Tài liệu gốc: [docs/TOOLSET.md](docs/TOOLSET.md), giữ nguyên.

Đã chuẩn hóa 97 tuyến thao tác, 44 tên tool thuộc 9 nhóm vào [TOOLSET_INDEX.json](TOOLSET_INDEX.json).

## Sử dụng

```bash
python3 route_toolset.py verify
python3 route_toolset.py categories
python3 route_toolset.py list --category "Repositories"
python3 route_toolset.py show wit_work_item_write
python3 route_toolset.py find "build"
```

Các nhóm: Core; Work; Work Items; Repositories; Pipelines; Test Plans; Wiki; Search; Advanced Security.

Thông tin tên và action được bảo toàn từ danh mục nguồn. Tham số chi tiết, địa chỉ Azure DevOps organization, lệnh khởi động server và cấu hình kết nối không có trong nguồn đã gửi, nên không tự gán.

Chỉ mục này chạy cục bộ để tìm và kiểm tra công cụ. Đây không phải một server MCP mới hay bằng chứng đã kết nối Azure DevOps. Trong phiên này chưa có callable Azure DevOps MCP tools.

Tài liệu đầu mối: `../AZURE_DEVOPS_MCP_TOOLSET_ENTRY.md`.
