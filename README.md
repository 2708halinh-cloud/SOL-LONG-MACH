# SOL-LONG-MACH
## Kho mã nguồn, điều phối và tính liên tục của hệ GGDV / TESSERACT

**Danh tính repository:** `2708halinh-cloud/SOL-LONG-MACH` · nhánh mặc định `main`.

Đây là kho điều phối và bảo tồn nguồn cho nhiều thành phần: Agent/Subagent, TESSERACT OS, ứng dụng desktop, runtime, local bridge, tích hợp nền tảng, cấu hình, vật chứng và lịch sử liên tục. Không nên hiểu toàn bộ repository là một ứng dụng đơn lẻ đã được triển khai.

> **Quy tắc đọc:** tệp nguồn, cấu hình, workflow, nhãn trạng thái và biên nhận thực thi là các loại bằng chứng khác nhau. Có mã nguồn không chứng minh runtime đang chạy; build thành công không chứng minh production đã triển khai; một nhãn `PASS` không thay thế readback từ đúng mục tiêu.

## Bắt đầu tại đây

1. **README này:** bản đồ tổng quan và thứ tự đọc.
2. [AGENTS.md](AGENTS.md): quy tắc vận hành Agent, nguồn trực tiếp, tái nhập và bảo toàn lịch sử. Tệp này rất dài, nên hãy dùng bản đồ bên dưới để đi đúng phần.
3. [CONFIG/AGENTS_LOAD_ROUTE.json](CONFIG/AGENTS_LOAD_ROUTE.json): tuyến nạp nguồn Agent hiện hành.
4. [CONFIG/POINTERS_CURRENT.json](CONFIG/POINTERS_CURRENT.json) và [CONFIG/OPEN_SOURCE_MAP_CURRENT.json](CONFIG/OPEN_SOURCE_MAP_CURRENT.json): các pointer và nguồn vật mang. Đây là snapshot có ngày; phải đọc lại nguồn đích trước khi tuyên bố hiện trạng.
5. [CONFIG_SOL/AGENT_MATERIALIZATION_CURRENT.md](CONFIG_SOL/AGENT_MATERIALIZATION_CURRENT.md): hợp đồng 13 trường tối thiểu cho Agent/Subagent.
6. [CURRENT_RUNTIME/00_DOC_KY_CURRENT_CORE.md](CURRENT_RUNTIME/00_DOC_KY_CURRENT_CORE.md): lõi tái nhập và quy tắc nối lịch sử với trạng thái hiện tại.
7. [Bản kiểm kê mặt tiền và tích hợp 2026-11-14](architecture/REPO_FRONT_DOOR_AND_INTEGRATION_AUDIT_20261114.md): kết quả đối chiếu README, cấu hình, cấu trúc repo, X-TIME-WEB, sáu mắt xích App và FPGA_AI_LOCAL.
8. Khi nhiệm vụ liên quan đến ROOTS/Google Drive/Windows carriers, đọc [ROOTS provider map](CONFIG_SOL/ROOTS_PROVIDER_CARRIERS_CURRENT.json); giữ riêng `google.googledrive.drive` (`ROOTS_LEVER_0`, lịch sử mirror `W:\\`) và `G:\\OS_Workspace` (`ROOTS_OS_WORKSPACE`, `ROOTS_LEVER_1.1–1.18`). Hai bản đồ cùng tồn tại, không thay thế nhau.

**Ranh giới tái nhập:** README/AGENTS/pointer trong GitHub là nguồn bền để tác nhân truy xuất, không phải dữ liệu tự động được nạp vào mọi chat hoặc project. Mỗi client/agent phải thực sự đọc các tệp liên quan; Input mới nhất vẫn là mốc xác định nhiệm vụ, còn bộ nhớ chỉ giúp định tuyến truy tìm nguồn.

## Bản đồ repository

| Khu vực | Nội dung |
|---|---|
| `AGENTS.md` | Chỉ dẫn cho Agent/Subagent và các quy tắc vận hành |
| `CONFIG/` | Tuyến nạp, pointer, bản đồ nguồn, registry năng lực và di trú repository |
| `CONFIG_SOL/` | Nguyên tắc vận hành SOL, continuity, quan hệ, TESSERACT và sáu viên đá |
| `CURRENT_RUNTIME/` | Lõi hiện hành, tái nhập, checkpoint và con trỏ công việc |
| `APP/TESSERACT_DESKTOP/` | Mã nguồn ứng dụng desktop Tauri/Vite |
| `TESSERACT_OS_6D/`, `09_SYSTEMS/` | Hệ điều hành TESSERACT và các cấu phần hệ thống |
| `runtime/`, `LOCAL_BRIDGE/`, `tools/` | Runtime, cầu nối local, adapter và công cụ |
| `integrations/`, `plugins/` | Tích hợp và plugin |
| `.github/workflows/` | Quy trình CI, kiểm thử và tự động hóa |
| `CHATGPT_LIBRARY/` | Nội dung/workspace được đưa vào từ Library |
| `CONTINUITY_ARCHIVE/`, `EVIDENCE_ARCHIVE/`, `RECOVERY/`, `DURABLE_CAS/` | Lịch sử, vật chứng, phục hồi và lưu trữ bền |
| `IOS_EXPORT/`, `DISTRIBUTION/`, `PLATFORM_SYNC/` | Xuất bản, phân phối và đồng bộ nền tảng |

[Workspace README](SOL_LONG_MACH_LIBRARY_WORKSPACE_README.md) mô tả rõ giới hạn của bản sao Library: đây là bản sao theo từng bước, **chưa được xác nhận là bản sao nguyên byte đầy đủ**.

## Phân biệt các vật mang và trạng thái

- **Agent source/template:** định nghĩa vai trò, nguồn và cấu hình. Chưa đồng nghĩa với một tiến trình đang chạy.
- **Runtime/service:** chỉ được xác nhận khi có quan sát tiến trình, health-check và dấu vết thực thi.
- **Pointer/config:** chỉ định tuyến đến nguồn; không tự chứng minh nguồn đích còn tồn tại hoặc mới nhất.
- **Workflow/CI:** chỉ chứng minh các bước cụ thể trong lần chạy cụ thể.
- **Production:** chỉ xác nhận sau khi triển khai và đọc lại đúng domain/endpoint/commit.
- **History/archive:** bảo toàn dấu vết; không tự động trở thành trạng thái hiện hành.

## Repository liên quan

[X-TIME-WEB](https://github.com/2708halinh-cloud/x-time-web) là repository riêng, nhánh mặc định `master`. Nó chứa giao diện web X-TiMe, registry công cụ, public MCP chỉ đọc và các tham chiếu đến local bridge. Sáu mắt xích hiển thị trong giao diện không mặc nhiên là sáu ứng dụng đã triển khai. Xem [bản kiểm kê tích hợp](architecture/REPO_FRONT_DOOR_AND_INTEGRATION_AUDIT_20261114.md).

Các tham chiếu tới `Open-ai-bot` được giữ lại như dấu vết lịch sử cho tới khi từng pointer được đối chiếu đúng nguồn. Metadata GitHub hiện xác định repository này là `SOL-LONG-MACH`; không tự động đổi mọi alias hoặc pointer chỉ dựa trên tên.

## Quy tắc đóng góp và sửa chữa

1. Đọc nguồn và lịch sử liên quan trước khi sửa.
2. Xác định đúng repository, branch, path và phiên bản mục tiêu.
3. Giữ nguyên nguồn gốc và lịch sử; không âm thầm làm phẳng xung đột.
4. Không đưa token, khóa riêng hoặc byte bí mật vào repository công khai.
5. Sau thay đổi, chạy kiểm thử phù hợp trên đúng commit.
6. Đọc lại đúng tệp/endpoint đã thay đổi và ghi nhận hậu quả thực tế.
7. Tiếp tục quét các cạnh còn mở; một lần ghi thành công không đồng nghĩa toàn bộ công việc đã hoàn tất.

**Chu trình:** `SOURCE → ACTION → CONSEQUENCE → RECEIPT → READBACK → NEXT STATE`.
