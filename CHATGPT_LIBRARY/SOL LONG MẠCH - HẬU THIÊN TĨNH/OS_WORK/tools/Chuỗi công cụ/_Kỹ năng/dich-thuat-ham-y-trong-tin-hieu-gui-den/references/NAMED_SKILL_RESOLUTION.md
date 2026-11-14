# NAMED SKILL RESOLUTION — truy tìm nguồn và tái sử dụng đúng cơ chế

## Tín hiệu điều hướng
- Nếu người dùng đặt tên `$SkillName` hoặc tên thuần, đưa tên **đó** vào phạm vi kế hoạch hiện tại và tìm đúng nguồn trước khi áp dụng.
- Nếu không nêu tên nhưng nhiệm vụ cần skill chuyên biệt, chọn theo **khả năng giải quyết mục tiêu thực**, không theo trùng một từ khóa hoặc vì có sẵn trong danh sách.
- Lấy danh mục skill đang khả dụng **trong phiên này**, gồm `name`, `description`, `location`, `authority` (nếu công cụ trả). Tên trong văn bản lịch sử chưa đủ chứng minh đang được cài đặt.
- Nếu đã đọc cùng nguồn + cùng SHA/revision trong phiên hiện tại, dùng lại phần đã kiểm, không đọc lại để tạo I/O không cần thiết.

## Các loại location
1. **Filesystem path:** mở file thật từ đường dẫn được chỉ định, xét quyền của hệ thống file; nếu alias như `r0`, lấy ánh xạ hiện có từ danh mục rồi nối đường an toàn. Nếu không có alias mapping, không đoán gốc.
2. **Provider URI:** dùng đúng provider action có schema hỗ trợ URI được trả; các `skills://plugins/.../skill.md` phải đọc qua `skills__read` (khi công cụ khai báo); không biến URI thành thư mục local.
3. **Orchestrator package:** khi `skills.list` **thực sự hỗ trợ** tham số `{"authority":{"kind":"orchestrator"}}`, truy inventory trong quyền đó, nhận `main_resource` và truyền **nguyên token/authority/package** cho `skills.read`; mọi tài nguyên phụ được đọc bằng cùng cơ chế. Nếu phiên chỉ có `skills__list({})` không có prop `authority`, dùng schema khả dụng và báo `ORCHESTRATOR_AUTHORITY_ARG_UNSUPPORTED`, không giả đã gọi đường không có.
4. **Nhiều carrier:** giữ đúng `provider/account/ID/version`, đối chiếu nguồn/nhánh hiện tại, không suy Drive path/ID từ quá khứ vẫn LIVE; lỗi 404 trên một carrier không chứng minh xóa ở mọi carrier.

## Khi nguồn ban đầu thiếu
1. Check lỗi đọc là `NOT_FOUND`, `PERMISSION_DENIED`, `UNSUPPORTED_URI`, `STALE_ALIAS`, `PROVIDER_UNAVAILABLE` hay khác.
2. Tìm tên chính xác trong registry phiên, những `SKILL.md` trong các root **được cấp quyền** và nguồn GitHub/Library/project đã định danh; sau đó tìm provider phù hợp khi nguồn trước thiếu.
3. Không tự thay thế skill có tên bằng skill khác không cùng nội dung. Không đọc `README.md` thay cho `SKILL.md` rồi nói đã đọc skill.
4. Nếu tất cả tuyến tìm có quyền đã được thử và skill đó **thiết yếu**, dừng phần công việc phụ thuộc, trình bày tên skill, tuyến tìm, lỗi và yêu cầu tối thiểu để tiếp tục. Các cạnh khác không phụ thuộc có thể vẫn hoàn tất.
5. Nếu skill không thiết yếu, ghi `SKILL_UNAVAILABLE_NON_BLOCKING`, thực hiện các cạnh khả thi dựa trên yêu cầu trực tiếp của người dùng.

## Tham chiếu phụ
- Với file SKILL.md trên filesystem, resolve `references/...` hoặc `scripts/...` đối với *thư mục của SKILL.md* và xác minh đường thực, không trôi sang thư mục làm việc hiện tại một cách mù.
- Với skill thuộc orchestrator, dùng `package + authority + exact resource identifier` qua công cụ orchestrator có thực, không coi `skill://` là filesystem path.
- Mã `scripts/skill_resolver.py` (tính từ thư mục Skill root) là **preflight offline hỗ trợ phân giải danh mục**, không gọi provider và không cấp quyền mới.

## Phê duyệt/host
Nguồn người dùng mới được ưu tiên so với quy trình trong skill sửa được và cùng tác vụ; không phủ định chính sách nền tảng, quyền nhà cung cấp hay phê duyệt host. Nếu một skill gây nhu cầu hỏi người dùng hoặc chặn bước cuối, nêu tên và quy tắc gây ra sự dừng cụ thể, sau khi đã làm xong các cạnh độc lập.

## NEXT
`SOURCE_DIRECT → PLAN_ADD_NAMED_SKILL → INVENTORY → RESOLVE_LOCATION → SKILL_SOURCE_READ → REFERENCES → ACTION → PROVIDER_RECEIPT → EXACT_READBACK → N+1`.
