# Azure DevOps MCP — đường vào cây tools

- `AZURE_DEVOPS_MCP_CORE/docs/TOOLSET.md`: nguồn gốc bảng Azure DevOps MCP.
- `AZURE_DEVOPS_MCP_CORE/TOOLSET_INDEX.json`: 97 tuyến gọi; 44 tên tool; 9 nhóm.
- `AZURE_DEVOPS_MCP_CORE/route_toolset.py`: kiểm tra đối chiếu và tìm theo tool, action, mô tả.
- `AZURE_DEVOPS_MCP_CORE/README.md`: tài liệu liên kết.

Chạy từ gốc repo:

```bash
python3 "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/AZURE_DEVOPS_MCP_CORE/route_toolset.py" verify
```

Trạng thái: danh mục và công cụ tìm/kiểm tra được tích hợp vào GitHub. Chưa xác minh kết nối Azure DevOps server ở runtime đang chạy.
