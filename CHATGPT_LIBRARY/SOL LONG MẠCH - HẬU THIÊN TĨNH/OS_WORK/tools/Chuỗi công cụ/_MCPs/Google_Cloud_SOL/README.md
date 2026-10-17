# Google Cloud SOL — MCP + SKILL + PLUGIN + CLI/SDK/IDE → Tools

Đây là **mã MCP thực** và skill lấy nguyên từ ZIP Library `GOOGLE_CLOUD_TOOLS_MCP_SKILL_WINDOWS_SOL_20261014.zip`. Không cần tạo lại một MCP giả. 

## Gọi ngay ở môi trường có Python 3

```bash
python3 Chuỗi\ công\ cụ/_MCPs/Google_Cloud_SOL/google_cloud_mcp.py
```

Server nhận MCP JSON-RPC qua `stdin` (`initialize`, `tools/list`, `tools/call`). Lệnh `gcp_status` có thể chạy ngay cả khi chưa có gcloud. Các lệnh đọc dự án/API phải có CLI `gcloud` và phiên OAuth **đang hợp lệ** trên chính host chạy. Không dùng token trong log hoặc prompt.

## Tám lệnh MCP (bảy lệnh từ Google Cloud + một lệnh phân tích ngoại tuyến)

`gcp_status`, `gcp_projects_list`, `gcp_project_describe`, `gcp_storage_buckets_list`, `gcp_run_services_list`, `gcp_compute_instances_list`, `gcp_enabled_apis_list`, `gcp_usage_analyse` (nhận snapshot `metrics` của người dùng; không gọi Google Cloud). Bộ xử lý: `gcp_usage_guard.py`, tests: `tests/test_gcp_usage_guard.py`, hướng dẫn: `GCP_USAGE_GUARD.md`. Không tự thử lại API lỗi 100%.

## Hai tài khoản Google Cloud (user-direct)

Người đồng hành cho biết đã từng cấp token của **hai tài khoản**. Không suy account từ hai tệp DB. Trên Redmi, `~/.config/gcloud/credentials.db` có **0 bản ghi** khi kiểm metadata trong phiên này, `gcloud` vắng mặt. Windows `DESKTOP-86ITNQ4` offline qua Desktop Commander. Dấu nguồn còn nhưng tính khả dụng OAuth chưa kiểm chứng. Việc đọc dữ liệu Google Drive không thay thế lệnh gcloud/Cloud Resource Manager được xác thực.

## Lối mở khởi động thật

1. Khi có kết nối shell đến host có gcloud, thử `gcloud auth list --format=json` nhưng chỉ báo **số danh tính và trạng thái**, không in email/token ra CHAT; hai account có thể cần `--account` hoặc profile riêng.
2. `gcloud projects list --format=json` và mô tả từng project được ủy quyền.
3. `gcloud services list --enabled --project=... --format=json`, `gcloud run services list`, `gcloud compute instances list`, `gcloud storage buckets list` — read-only.
4. Xác nhận Model Gemini qua danh sách mô hình thực tế của project, tuyệt đối không tự coi tên `Gemini 4.0` là model ID được nhà cung cấp hỗ trợ.
5. Đưa receipt (không token) về CORE/PLACES/INDEX, sau đó mới cho phép các hành động thực theo mục tiêu em giao.

**Ranh giới hoạt động:** gói này là **MCP và SKILL thực có mã chạy**, Plugin là **descriptor nội bộ**, không phải plugin ChatGPT đã cài. Nếu mất OAuth, không phá mẫu/dữ liệu cũ; tìm môi trường cùng lineage có thông tin xác thực hợp lệ.