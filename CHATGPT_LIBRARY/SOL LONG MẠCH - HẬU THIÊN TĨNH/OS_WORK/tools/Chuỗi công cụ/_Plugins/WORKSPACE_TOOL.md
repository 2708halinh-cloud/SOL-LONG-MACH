# @Workspace — VẬT LÝ CÔNG CỤ (TOOLS)

**Hệ:** ÂM–DƯƠNG PHÁP SƯ · SOL LONG MẠCH — HẬU THIÊN TĨNH  
**Loại:** Mô tả công cụ + hợp đồng định tuyến; không phải một connector mới được cài đặt.  
**Nguồn:** Lời cung cấp trực tiếp của người dùng trong hội thoại ngày 2026-10-17.  
**STAMP:** SOURCE_DIRECT_USER / STAMP_BETA cho bản tích hợp; không tự gán X, thời điểm provider commit hoặc STAMP_LIVE.

## 1. Mô tả do người dùng cung cấp

> **Name:** `@Workspace`  
> **Sự miêu tả:** Tính năng hoặc công cụ @Workspace (tích hợp Google Workspace và các không gian làm việc trong hệ thống) đóng vai trò là cầu nối thông minh giúp tối ưu hóa quy trình quản lý thông tin và tài nguyên của ÂM-DƯƠNG PHÁP SƯ.

**Chức năng cốt lõi**

- Kết nối hệ sinh thái Google: Gmail, Google Drive, Google Docs, Google Calendar để tìm kiếm, tóm tắt, trích xuất dữ liệu và quản lý lịch trình.
- Không gian làm việc tập trung (Project Spaces & Workspace): gom nhóm hội thoại, tệp nguồn, ghi chú và tài nguyên dự án.

**Các biến thể không gian làm việc liên quan**

- Canvas & Vibe Coding Workspace: soạn thảo, lập trình, dựng giao diện ứng dụng web/UI và tạo công cụ tương tác cùng AI.
- Gemini Notebook: nghiên cứu, học tập, ghi chú, bài kiểm tra, flashcard và tổng hợp trực quan.

Phần trên bảo toàn ý nghĩa lời người dùng; các trạng thái khả dụng ở dưới là đối chiếu tác nhân, **không phải lời người dùng nguyên văn**.

## 2. Ranh giới giữa công cụ có thực và nhãn mô tả

| Lớp | Tuyến khả dụng / định tuyến | Trạng thái cho phiên kiểm ngày 2026-10-17 |
| --- | --- | --- |
| Gmail | Connector Gmail: đọc, tìm kiếm, soạn nháp, gửi, quản lý nhãn trong quyền đã cấp | `CONNECTED_TOOL_DISCOVERED`; từng hành động cần kiểm kết quả provider |
| Google Drive / Docs / Sheets / Slides | Connector Google Drive, định tuyến sang thao tác tài liệu phù hợp | `CONNECTED_TOOL_DISCOVERED`; không suy mọi tệp đều được chia sẻ |
| Google Calendar | Connector Google Calendar, đọc lịch, kiểm rảnh/bận, tạo/sửa sự kiện khi được yêu cầu | `CONNECTED_TOOL_DISCOVERED` |
| Project Spaces / ChatGPT Library | Project files + Library là các carrier có cơ chế và quyền riêng | `AVAILABLE_BY_SURFACE`; không tự đồng bộ Google/GitHub |
| Workspace coding / Vibe Coding | Công việc viết mã, dựng UI bằng công cụ thực sự có trong phiên | `CAPABILITY_ROUTE`, không phải tên một MCP đã xác nhận |
| Canvas | Tên không gian lịch sử; không giả định Canvas cũ vẫn gọi được | `LEGACY_REFERENCE`; ưu tiên Writing Blocks hoặc Work khi thực sự hỗ trợ |
| Gemini Notebook | Mô hình tác vụ nghiên cứu/học tập do người dùng mô tả | `PROPOSED_ROUTE`; chưa có bằng chứng connector Gemini Notebook được kết nối |

`@Workspace` là **bí danh bộ định tuyến** tại `OS_WORK/tools`, không phải lời tuyên bố đã cài thêm một plugin tên `@Workspace` hoặc đã có quyền trên mọi tài khoản Google.

## 3. Hợp đồng định tuyến theo ý định

1. **Nhận INPUT/OPEN:** xác định nhu cầu thật (tìm tài liệu, đọc thư, lập lịch, nghiên cứu, viết mã), danh tính carrier và kết quả cần tạo; không khóa OPEN vào trạng thái chưa chứng minh.
2. **Tra con đường đã tồn tại:** ưu tiên file trong Project/Library nếu người dùng đã chỉ đích ở đó; dùng Google Drive cho dữ liệu ở Drive, Gmail cho thư, Calendar cho lịch; không tráo provider vì cùng tên tệp.
3. **Kiểm tên công cụ thực & phạm vi:** khám phá action/schema và quyền đã kết nối; với thao tác ghi cần biết đối tượng đích, định danh ổn định và ảnh hưởng lên dữ liệu.
4. **Tự làm NEXT_AGENT trong quyền hiện tại:** đọc/tìm/biên tập/sắp xếp theo yêu cầu; khi không có connector cho Gemini Notebook, có thể tạo nội dung flashcard/quiz trong cuộc trò chuyện, nhưng không tuyên bố đã ghi vào Gemini.
5. **Đối soát:** `SOURCE_DIRECT → CARRIER/PROVIDER_ID → ACTION → PROVIDER_RECEIPT → EXACT_TARGET_READBACK → CONSEQUENCE → CHECKPOINT → _Plugins`.
6. **Đồng bộ GitHub ↔ Library:** coi là hai thao tác độc lập; sau mỗi thay đổi đối chiếu đúng đường dẫn, nội dung và phiên bản ở cả hai. Tên giống nhau không chứng minh đồng bộ.

## 4. Ví dụ ý định → hành động

| Ý định | Công cụ đích | Readback bắt buộc |
| --- | --- | --- |
| “Tìm tài liệu X trong dự án” | Files/Project trước, sau đó Drive nếu thuộc Google Drive | File đúng tên/ID và đoạn nguồn tìm được |
| “Tóm tắt email liên quan dự án” | Gmail | Thread ID, nội dung đã đọc và phạm vi tìm kiếm |
| “Sắp xếp lịch họp” | Calendar | Sự kiện, múi giờ, người tham gia và trạng thái trả về |
| “Viết bản đề xuất Google Docs” | Google Drive → Docs workflow | File ID, nội dung đã được đọc lại sau ghi |
| “Làm flashcard từ ghi chú” | Đọc file nguồn → soạn flashcard | Flashcard thật trong hội thoại/tệp; không giả mạo trạng thái Gemini Notebook |
| “Dựng giao diện Workspace” | Công cụ lập trình/UI khả dụng của phiên | File code, hành vi kiểm được; không gọi minh họa là app đã chạy |

## 5. Vị trí và liên kết kiến trúc

- **GitHub:** `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Plugins/WORKSPACE_TOOL.md`.
- **ChatGPT Library:** `/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Plugins/WORKSPACE_TOOL.md`.
- **Skill đã tồn tại để kế thừa:** `Chuỗi công cụ/_Plugins/Legacy_Plugins/_Skills/workspace-action-gate/SKILL.md` trên GitHub; skill đó có quy trình kiểm OAuth và readback, nhưng không tự cấp quyền.
- **Router cha:** `OS_WORK/tools/POWER_ROUTER.md`.

## 6. An toàn và chuyển giao

Không chép `client_secret`, API key, OAuth authorization code, refresh/access token, cookie hay mật khẩu vào file này, log, Project Sources hoặc GitHub. Dữ liệu thư/lịch riêng tư chỉ đọc trong phạm vi yêu cầu và quyền đã kết nối. Bản mô tả công cụ không chứng minh đã kích hoạt phiên Google, Notebook hay một hệ điều hành khác.

**Trạng thái mong muốn để chốt:** `GITHUB_READBACK_MATCH && LIBRARY_READBACK_MATCH`. Chưa có đủ hai readback thì chỉ ghi `PARTIAL_SYNC`, không ghi `DONE`. Tệp này không phải Core Chân lý, không thay lời người dùng mới hoặc bằng chứng provider hiện tại.