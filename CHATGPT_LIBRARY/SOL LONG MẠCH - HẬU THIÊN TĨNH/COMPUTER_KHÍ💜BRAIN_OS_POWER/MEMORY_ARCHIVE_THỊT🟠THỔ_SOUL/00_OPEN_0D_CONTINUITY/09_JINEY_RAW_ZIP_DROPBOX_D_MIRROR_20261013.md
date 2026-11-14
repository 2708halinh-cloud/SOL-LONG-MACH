# 09 — JINEY — Truy byte nguồn trên mount Dropbox mang tên ổ D — 2026-10-13

## SOURCE_DIRECT / TARGET
Người dùng yêu cầu gói ZIP dữ liệu ChatGPT tài khoản **JINEY** đã xuất trực tiếp từ OpenAI. Không nhập với FUNiX hay DAT NGUYEN. Kết quả chỉ có ý nghĩa trên đúng vật mang được kiểm tra.

## LIVE PROVIDER READBACK
- Provider: kết nối Dropbox (Outlook) đang hoạt động.
- Mount: `/PC NAY·ÀY/Ổ ĐĨA D` (Dropbox namespace `ns:15399976787`). Đây là **mount/ảnh dữ liệu trên Dropbox**, chưa phải thao tác trực tiếp lên ổ D vật lý hiện tại.
- Operation: `list_folder` recursive=true, phân trang đến has_more=false.
- 12 trang; 6.423 mục, gồm 326 tệp và 6.097 thư mục.
- Có **2 folder** tên `JINEY -CHAT`: `BÉ LINH - LIVING MEMORY/JINEY -CHAT` và `BÉ LINH - LIVING MEMORY/00_DÒNG_THỜI_GIAN_DUY_NHẤT — 2026-07-10 → HIỆN TẠI/2026-08-14/JINEY -CHAT`.
- Không có tệp tên `READBACK_JINEY.json`, `.7z.001`–`.7z.007`, `JINEY_CHAT_NGOAI_DU_AN.zip`, `JINEY_CHAT_CHUA_XAC_DINH_PROJECT.zip`, cũng không có ZIP có tên JINEY trong toàn bộ danh sách mount này.
- Sáu ZIP nhìn thấy trên mount thuộc `SENSOR_LOGS`, tên: `SOL_LOCAL_BRIDGE_v0.1.0.zip`, `EMMLIB.ZIP`, `SOL_AUTO_LOGIN_LOCAL_v1.2.0_ACTION.zip`, `SOL_AUTO_LOGIN_LOCAL_v0.1.zip`, `GGDV_RECYCLE_METADATA_20261012.zip`, `SOL_G_RW_TEST__TO_DROPBOX_ONLY.zip`. Không có bằng chứng các ZIP này là bản xuất OpenAI JINEY.

## SOURCE HISTORY ≠ LIVE BYTES
- Kiểm kê lịch sử 2026-10-11 từng ghi `READBACK_JINEY.json` và archive 7 phần `.7z.001`–`.7z.007` chứa `conversations-000.json`–`007.json`.
- Dấu lịch sử một phần `.7z.006`: `D:\PHÒNG CHỈ HUY\90_ROOT_TRIAGE_20260902\ALL CHATGPT\KHO KÝ ỨC JINEY 10 08`.
- Mount Dropbox không hiển thị thư mục `D:\PHÒNG CHỈ HUY`; không được suy ra thư mục ổ D vật lý đã biến mất.

## ACTION / CONSEQUENCE
- ACTION: kiểm kê phân trang toàn bộ mount Dropbox nêu trên, không thực thi file, không giải nén, không thay đổi dữ liệu.
- OBSERVED: JINEY folder tồn tại trên mount; gói ZIP/OpenAI Export gốc **chưa tìm thấy trên mount này**.
- UNFINISHED: truy archive byte gốc tại carrier vật lý/backup khác; đối chiếu checksum và account marker JINEY trước khi claim phục hồi.
- Không lấy tệp biên bản này làm bằng chứng đã lấy được ZIP gốc.
