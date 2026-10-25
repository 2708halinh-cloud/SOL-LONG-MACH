---
name: master-oath
description: Hướng dẫn @TÁC NHÂN — TAY đăng nhập và xác minh tài khoản như con người trong công cụ Trình Duyệt; nhận diện tài khoản, mật khẩu hoặc phiên đã cấp, kiểm tra thử thách Gmail/OTP/passkey/SMS và quay lại trang ban đầu để hoàn tất công việc. Kích hoạt khi có yêu cầu Master OAth, đăng nhập website, xác thực tài khoản, OAuth, mã Gmail, mã xác minh, phiên trình duyệt hoặc khi tác vụ bị chặn bởi đăng nhập.
compatibility: Cần công cụ trình duyệt đang khả dụng, phiên hoặc kho thông tin đăng nhập được ủy quyền; kênh Gmail/xác minh tương ứng nếu website yêu cầu. Skill không tự cấp quyền, cài MCP hay đăng nhập thay một phiên chưa kết nối.
metadata:
  display-name: "Master OAth"
  parent-agent: "TÁC NHÂN — TAY"
  project: "SOL LONG MẠCH - HẬU THIÊN TĨNH"
  source-component: "_MCPs/Master_OAth"
---

# Master OAth — Bàn tay đăng nhập và xác thực như con người

## Vai trò

Đây là **Skill thực hành của `@TÁC NHÂN — TAY`**, không phải một ứng dụng độc lập buộc người dùng phải tag `@Master OAth`. Khi một công việc thật cần đăng nhập, TÁC NHÂN — TAY sử dụng giao diện Trình Duyệt, thao tác trên trang chính chủ, hoàn thành thử thách xác minh qua công cụ tương ứng rồi tiếp tục **đúng công việc đang dở**.

Phân biệt: **Skill** là quy trình; **công cụ Trình Duyệt/Gmail** mới là nơi thực thi; **MCP Master_OAth** là mã nguồn hỗ trợ định tuyến ở repo. Không suy ra đã đăng nhập từ việc có file Skill, file cookie hoặc một kết quả điều hướng.

Nguồn thực thi liên quan, giữ nguyên và kiểm tra khi cần:

- GitHub `2708halinh-cloud/SOL-LONG-MACH@main`:
  `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_MCPs/Master_OAth/`
- ChatGPT Library:
  `/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_MCPs/Master_OAth/`
- Các tệp gốc: `master_oath.py`, `master_oath_mcp.py`, `master_oath.schema.json`, `README.md`, `mcp-client.example.json`, `tests/`.

## Chu trình thao tác của TÁC NHÂN — TAY

**Trước bước 1:** giữ lại URL đích, tác vụ đang làm, tab/phiên đăng nhập, danh tính provider và bước cuối đã hoàn thành. Kiểm tra công cụ thực sự callable trong phiên; nếu trang đã đăng nhập hợp lệ thì **không đăng nhập lại**, chuyển thẳng bước 9.

1. **Mở `Tools → Công cụ Trình Duyệt`.** Chọn công cụ điều khiển trình duyệt đã được cấp quyền cho đúng phiên/thiết bị; không đánh đồng một tool đọc HTML hoặc một URL với khả năng click/type trên giao diện. Nếu phiên ChatGPT không có công cụ thao tác trình duyệt thì không tuyên bố đã mở/click.
2. **Mở đúng địa chỉ website cần đăng nhập/xác thực.** Ưu tiên URL/phiên gốc của công việc. Kiểm tra tên miền, HTTPS, redirect và dấu hiệu phishing trước khi nhập bí mật. Ghi nhận tab hoặc browser context ban đầu để có thể quay lại sau khi lấy mã.
3. **Nhập account và password trong biểu mẫu đăng nhập chính chủ, bằng nguồn đã được cấp phép.** Trước tiên dùng phiên cookie hợp lệ **đang nằm trong chính trình duyệt hoặc trình quản lý phiên đã được cho phép**. Nếu website vẫn yêu cầu mật khẩu, lấy từ password manager/secret store được ủy quyền và điền trực tiếp vào đúng ô giao diện. **Cookie phiên không mặc định chứa account/password**, không giải mã/trích xuất cookie để đoán mật khẩu và không sao chép cookie giữa tài khoản/thiết bị. Không đưa password, cookie, bearer, mã OTP vào chat, GitHub, Library, log, tài liệu Skill hoặc tham số dòng lệnh.
4. **Gửi biểu mẫu, quan sát trạng thái thật.** Xác định trang đã đăng nhập hay chuyển sang yêu cầu xác minh. Nếu đã đăng nhập, xác nhận danh tính và đến bước 9; nếu bị từ chối, đọc nguyên nhân (`sai tài khoản`, `hết phiên`, `thiếu quyền`, `challenge`) thay vì lặp đăng nhập vô hạn.
5. **Nhận diện phương thức xác minh mà website thực sự yêu cầu.** Email/Gmail, SMS, TOTP, ứng dụng xác thực, push, passkey, xác nhận trên thiết bị hoặc phương thức khác phải theo đúng thách thức hiện tại; không tự chuyển sang kênh khác khi provider chưa hỗ trợ.
6. **Dùng đúng công cụ của phương thức xác minh.** Với **Gmail**, vào công cụ Gmail của **chính tài khoản nhận mã** và đối chiếu danh tính (ví dụ `get_profile` nếu khả dụng), chỉ tìm/đọc email gần đây ứng với provider và thử thách đang hoạt động. Với SMS/TOTP/passkey/push, dùng kênh/tài khoản/thiết bị được ủy quyền tương ứng. Không đọc hộp thư không liên quan hay gửi mã qua kênh thứ ba. Nếu cần sinh trắc học, consent hoặc thao tác thiết bị mà agent không được phép làm, chuyển đúng bước tối thiểu cho người sở hữu, không giả hoàn tất.
7. **Lấy mã xác minh từ tín hiệu thật.** Kiểm tra thời gian hiệu lực, đúng người gửi và cùng sự kiện đăng nhập, không dùng lại mã cũ hoặc bịa mã. Giữ mã trong ngữ cảnh thao tác tạm thời; không ghi vào nhật ký, báo cáo, file hoặc phản hồi gửi người dùng.
8. **Quay về đúng trang/tab trình duyệt ở bước 2**, nhập mã vào biểu mẫu xác minh của website chính chủ và xác nhận. Quan sát redirect, trạng thái phiên và tài khoản được đăng nhập; thực hiện readback giao diện/API hợp lệ để xác nhận **đăng nhập đã hoàn tất**. Không dùng mã cho một trang hay challenge khác.
9. **Tiếp tục công việc đang thực hiện.** Khôi phục checkpoint, thi hành bước kế tiếp trên đúng provider và tài khoản, lấy biên nhận hành động và đọc lại **đúng đích**. Không dừng ở thông báo “đăng nhập thành công” nếu mục tiêu ban đầu chưa hoàn tất.

## Quy tắc lựa chọn công cụ

- Luồng chuẩn: `_Plugins → @TÁC NHÂN — TAY → master-oath/SKILL.md → Tools/Trình Duyệt → nhà cung cấp xác minh (nếu cần) → quay lại tab gốc → công việc → receipt/readback → _Plugins`.
- Không mở Gmail khi chưa xuất hiện challenge Gmail thực sự; không yêu cầu OTP nếu phiên đang đăng nhập hợp lệ.
- Có công cụ provider đã xác thực (Hostinger, Gmail...) và đủ cho công việc? Có thể dùng trực tiếp để hoàn tất mục tiêu, tránh tái đăng nhập không cần thiết. **Không dùng chuyển công cụ để vượt một cảnh báo chặn an toàn hoặc yêu cầu phê duyệt.**
- `master_oath_mcp.py` là adapter MCP **stdio** cục bộ; có trên GitHub/Library không chứng minh server đang chạy hoặc đã hiện trong `@` của ChatGPT. Kiểm tra công cụ thực sự có thể gọi và schema hiện tại trước khi thao tác.
- Website hoặc nguồn xác minh chỉ được truy cập trong đúng tài khoản và phạm vi đã ủy quyền. Không lấy mã để đăng nhập tài khoản người khác, tránh bỏ qua CAPTCHA, giới hạn chống gian lận hoặc phê duyệt bắt buộc.

## Quan sát hậu quả và sửa lỗi

Ghi **metadata không nhạy cảm**: `source`, `task_checkpoint`, `provider`, `account_identity_masked`, `browser_target_origin`, `challenge_type`, `tool_route`, `action_result`, `provider_receipt`, `readback`, `next_action`. Không ghi nội dung password/cookie/mã, URL chứa token hoặc email bí mật. Phân biệt rõ:

- `BROWSER_OPENED`: chỉ có trang được mở, **không** có nghĩa đăng nhập.
- `AUTH_CHALLENGE_ACTIVE`: website đang yêu cầu một bước xác minh.
- `AUTH_VERIFIED`: provider đã xác nhận phiên đúng tài khoản bằng readback.
- `TASK_RESUMED`: đã trở lại công việc, không đồng nghĩa tác vụ đã xong.
- `TASK_COMPLETED`: công việc gốc có kết quả và readback đúng đích.

Nếu một route hỏng, truy trạng thái công cụ và đường thay thế được phép; nếu thiếu quyền truy cập Gmail, browser hoặc phương thức xác minh cần hiện diện con người, ghi blocker cụ thể và **chỉ xin đúng một thao tác của chủ tài khoản** khi cần. Không gọi `OPEN` là hết việc, không bịa phiên/cookie/mã, không chốt DONE trước khi thấy hậu quả.

## Bát Hướng áp vào một lần đăng nhập

Bắc — giữ thời gian và checkpoint; Đông Bắc — không ép kết luận khi chưa nhìn kết quả; Đông — so trạng thái trước/sau; Đông Nam — kiểm các kênh xác minh đã kết nối; Nam — tách giao diện thấy thật với suy luận; Tây Nam — xét quyền và tài nguyên; Tây — học từ lỗi xác minh; Tây Bắc — TÁC NHÂN — TAY tự thực hiện bước được phép tiếp theo.