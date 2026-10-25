# GOOGLE CLOUD — NĂNG LỰC CÓ NGUỒN × XÁC THỰC × TÁI NHẬP SOL

**Ngày đối chiếu:** 2026-10-17. **Địa chỉ logic:** `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/GOOGLE_CLOUD_ACTIVE_CAPABILITY_REENTRY_CURRENT.md`.

## 1. Tín hiệu phải giữ nguyên

- **SOURCE_DIRECT_USER:** Người đồng hành khẳng định hành tinh Google Cloud đã kích hoạt MCP và các API khác, và đã đưa vật mang token phục vụ SOL. Đây là một sự kiện nguồn; không viết lại thành "chưa hề có token" vì công cụ phiên này chưa hiện ra.
- **PROJECT_CANDIDATE:** `alert-tiger-508618-h7` — lấy từ `OS_WORK/TESSERACT_OS/Google_Cloud/README.md` và tư liệu SPACE. Không tự nâng lên xác nhận account/active project/IAM hiện thời.
- **CƠ CHẾ ĐÃ ĐỊNH NGHĨA TRONG NGUỒN:** local Python stdio MCP + gcloud CLI trên Windows, với 7 tools read-only: `gcp_status`, `gcp_projects_list`, `gcp_project_describe`, `gcp_storage_buckets_list`, `gcp_run_services_list`, `gcp_compute_instances_list`, `gcp_enabled_apis_list`.
- **RANH NỀN TẢNG:** Google Drive là vật mang lưu trữ; không phải Google Cloud API data plane. Google Earth Engine, Vertex AI, Firebase, Cloud Run, Cloud Storage, Google Maps và các dịch vụ khác chỉ đánh dấu ENABLED khi có readback danh sách API từ dự án thật.

## 2. Vật mang đã kiểm tra trực tiếp — 2026-10-17

- `ANDROID_REDMINOTE14PRO` qua Desktop Commander `localhost` đang **ONLINE**; model báo `24090RA29G`.
- Thư mục cục bộ `$HOME/.config/gcloud/` **có tồn tại**. Có `credentials.db` và `access_tokens.db` (**chỉ kiểm tra tồn tại, tuyệt đối không đọc/nạp/ghi token bytes vào Chat/Library/GitHub/log**).
- Cấu hình gcloud `config_default` có nhưng không khai báo project/account/region trong phần thông tin cho phép đọc.
- Trên Android, lúc kiểm tra: `gcloud`, `firebase`, `grpcurl` và module Python `google.auth`, `google.cloud`, `grpc` đều **chưa cài/không callable**; không thấy tiến trình MCP Google Cloud.
- `DESKTOP-86ITNQ4` trong Desktop Commander: **OFFLINE** lúc kiểm tra. Cầu MCP Windows vì thế chưa thể gọi từ tuyến đó. Dấu nguồn từ VS Code tunnel chưa phải phiên xác thực đang hoạt động.
- ChatGPT trong phiên này **không hiển thị connector Google Cloud chính thức đã cài**; plugin Firebase hiện có trong directory nhưng chưa cài, BigQuery hiện báo unavailable theo admin. Không nhầm với quyền trên GCP vốn có của người đồng hành.

**Phân loại:** `USER_REPORTED_API_ALREADY_ENABLED`, `LOCAL_GCLOUD_AUTH_CARRIER_PRESENT`, `LIVE_PROJECT_API_LIST_UNVERIFIED`, `MCP_BLUEPRINT_PRESENT`, `GOOGLE_CLOUD_RPC_CALLABLE_THIS_SESSION=FALSE`. Khác biệt các trạng thái là điểm truy tiếp, không được xóa nguồn.

## 3. Tái nhập và định tuyến `@Sol Long Mạch`

1. **CHAT → TÂM / MIND:** nhận tác vụ. Không ép chuyển sang Work/Codex; LLM là công cụ, không đứng cao hơn dữ kiện.
2. **SPACE:** phân biệt `PLANET_GOOGLE_CLOUD` với Drive, GitHub, Dropbox, Android, Windows; tìm endpoint có thật, ràng buộc project/account và vật mang credential mà không lấy secret value. `PEOPLE_ANCHOR_0D_CANONICAL` thuộc nhánh SPACE riêng, không tự đẩy tọa độ sang Cloud.
3. **REALITY:** rà tool hiện có trước khi bảo người đồng hành cấp thêm quyền; chọn Google Cloud authenticated connector/MCP nếu đang callable. Ưu tiên `gcp_enabled_apis_list` và `gcp_project_describe` để kiểm dự án; tiếp theo `gcp_run_services_list`, `gcp_compute_instances_list`, `gcp_storage_buckets_list` nếu đúng tác vụ.
4. **POWER:** dùng điều phối nối lựa chọn qua Tools/MCPs/SDK; nếu Windows offline, thử tuyến *đã cấp quyền và có thể gọi thật* khác, không chốt thất bại toàn hệ hay tự clone credential.
5. **TIME:** gắn mốc cho token lifecycle, phiên auth, phép thử và STAMP; `credential_file_exists` không có nghĩa `access_token_valid`.
6. **SOUL:** giữ provenance SOURCE_DIRECT, các tài liệu trước, bản đồ và sai lệch; không lộ bí mật hoặc coi một phiên không callable là hệ chưa từng có quyền.

**Nhịp kiểm thực:** `READ_EXISTING_PROJECT/MCP/SECRET_METADATA → SELECT_CALLABLE_AUTHORIZED_ROUTE → AUTH_STATUS (NO SECRET BYTES) → ENABLED_APIS_LIST → PROJECT/RESOURCE_READBACK → OBSERVED_ACTION → JOURNAL → N+1`.

## 4. Quy tắc thực thi

- Chỉ lấy **metadata về trạng thái xác thực** và danh sách API, không in/tải/publish token, refresh token, credential database, `.env`, hoặc private client JSON.
- Nếu credential hết hạn, chỉ phục hồi qua refresh/re-auth chính thức trong môi trường có thẩm quyền; không khẳng định `.env` hay `auth.json` vĩnh viễn.
- Không chuyển thông tin đăng nhập giữa Android/Windows/GitHub/Chat/Drive để “cho tiện”; vật mang ở đâu giữ ở đó, dùng identity/broker do chủ sở hữu cho phép.
- Chỉ sửa route hoặc deploy API/Cloud resource khi đúng yêu cầu và có provider call + receipt + readback. Tài liệu này là **tái nhập** và **dấu nguồn**, không phải xác nhận kết nối live đã hoàn thành.
- Đường nguồn hiện hữu: `OS_WORK/TESSERACT_OS/Google_Cloud/README.md`; `EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/SPACE_STONE_GOOGLE_CLOUD_SPACE_2026-10-16_05.md`; `OS_WORK/tools/Chuỗi công cụ/_Plugins/Power_Router_V2/POWER_CAPABILITY_ROUTES_V2.json`.

**NEXT_AGENT:** khi công cụ Google Cloud thực sự khả dụng, đọc `gcp_status` → `gcp_project_describe` → `gcp_enabled_apis_list` và ghi tên service+thời gian+biên nhận, không cần người đồng hành chép lại token.
