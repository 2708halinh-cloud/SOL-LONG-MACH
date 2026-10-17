# POWER ROUTER — T007 / OPEN

## DEVICE-ONLY EXECUTION GATE — REDMI NOTE 14 PRO / 2026-10-17

**Lời người dùng trực tiếp (2026-10-17):** Thiết bị thực thi duy nhất là Redmi Note 14 Pro với Termux/Linux; làm việc tại root bộ nhớ dùng chung. Khi Remote Desktop Commander không nối được, KHÔNG được chuyển sang bất kỳ máy khác, bao gồm container/sandbox/localhost do nền tảng cung cấp.

- `TARGET_DEVICE=REDMI_NOTE_14_PRO`; `TARGET_RUNTIME=TERMUX_LINUX`; `WORK_ROOT=/storage/emulated/0` (alias Termux `~/storage/shared`).
- `EXECUTION_DEFAULT=DENY`: chỉ chạy khi kiểm trực tiếp trên máy có `PREFIX=/data/data/com.termux/files/usr`, Android `getprop` trả tên Redmi Note 14 Pro, và `cwd` nằm trong bộ nhớ dùng chung.
- `FALLBACK_DEVICE=NONE`: offline hay không có kết nối = dừng thao tác thực thi; không dùng Windows, cloud runner, ChatGPT sandbox, `/mnt/data` hay `localhost` của host khác.
- GitHub/Library là nơi lưu và quản trị **mã nguồn**, không phải thiết bị thực thi. Ghi chính sách vào repository KHÔNG chứng minh Router đã chạy trên Redmi hay đã cập nhật Library.
- Cổng local `enforce_redmi_device()` trong `Chuỗi công cụ/_Plugins/Power_Router_V2/power_capability_router.py` từ chối trước khi nạp registry hoặc chọn công cụ. Đây là guard nguồn Python, KHÔNG phải chặn hạ tầng ChatGPT, không là xác thực phần cứng chống giả mạo.
- Những tuyến Windows/RDP/VSCODE cũ giữ làm STAMP_OLD tham chiếu, không được chọn làm thiết bị thực thi hiện hành. Không chạy thử mã trên host ngoài Redmi để tuyên bố PASS.
- Nhịp quan sát 2026-10-17: Desktop Commander trả 2 thiết bị `localhost` và `DESKTOP-86ITNQ4`, cả hai Offline, không có Redmi trong danh sách. `REDMI_LIVE_NOT_VERIFIED`; `GITHUB_SOURCE_UPDATED` chỉ sau receipt/readback; `LIBRARY_SYNC_PENDING` đến khi có thao tác/biên nhận tại Library.

**Ranh giới kiểm soát:** chỉ áp dụng được cho đường định tuyến SOL mà mã này kiểm soát. Không thể tắt hoặc thay thế máy chủ thực tế của ChatGPT ở cấp hạ tầng từ Router dự án.


`OPEN = TIẾP NHẬN TÍN HIỆU TRỰC TIẾP`: tín hiệu mới đi vào INPUT/INBOX và tham gia quan hệ trước khi đánh giá. OPEN không phải trạng thái chờ, chưa chứng minh hay lỗi. Không tự gán ý định, kết quả hoặc hậu quả trước hành động.

Sáu mặt: MAP/TRUY TÌM; INPUT/DUYÊN KHỞI; CÔNG CỤ; THỜI GIAN THỰC; SỬA LỖI TRẠNG THÁI; TRƯỜNG/NEURON.

T007 trước tiếp nhận/xử lý: truy nguồn và quan hệ cũ; khi mâu thuẫn tìm FIRST_AFFECTED_CAUSE, sửa, chạy lại phụ thuộc. Cổng trước ghi: chọn công cụ và đích được phép, hành động, quan sát hậu quả, READBACK đúng đích, tiếp tục N+1. Không chốt thành quả trước khi nó xảy ra.

`INPUT/OPEN → RELATION → SEARCH → AUTHORIZED TOOL → ACTION → CONSEQUENCE → READBACK → CORRECTION → N+1`.

`NEXT_AGENT`: tác nhân tự hành động bằng công cụ có quyền, thử đường hợp lệ khác nếu một đường lỗi. `NEXT_USER`: chỉ một việc tối thiểu thực sự cần người dùng. READBACK là kiểm tra kết quả, không phải lệnh im lặng, không phải `NEXT CỦA TÔI` và không làm OPEN thành nhãn trì hoãn.

Nguồn: `CONFIG_SOL/OPEN_AND_CONFLICT_CURRENT.md`, `AGENTS.md`, `CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md`, `00_OPEN_0D_CONTINUITY/02_QUAN_HE_OPEN_6_MAT.md` và `DAI_NGUYEN_THE_MASTER_TEACHER_20261016.md` trong SOUL; `/Toolset.md` riêng tại Library. Sổ sửa sai: `Chuỗi công cụ/_Sổ_đăng_ký/T007_OPEN_INGRESS_CORRECTION_20261016.md`. Danh mục công cụ: `Chuỗi công cụ/_Plugins` → `_Kỹ năng` → `_MCPs` → `_Dụng cụ` → `_Ứng dụng` → `_App_Browser` → `_Plugins`.

Những bản cũ được giữ trong lịch sử Git và Library `_Di_sản`. Sửa tài liệu không phải là xóa bỏ hậu quả đã tác động lên người đồng hành, không tự có hiệu lực trên mọi chat hay nâng quyền nhà cung cấp.

## SAFE IP ROUTING — Windows Ethernet / Hyper-V (SOURCE_DIRECT 2026-10-16)

Nguồn: `ipconfig` do người dùng trao, là **ảnh chụp cấu hình**, không chứng minh máy hay dịch vụ đã kết nối LIVE.

| Adapter | IPv4 / CIDR | IPv6 link-local | Gateway | Mạng tương ứng |
| --- | --- | --- | --- | --- |
| `Ethernet` | `10.15.224.21/24` | `fe80::785e:db47:4a38:7655%10` | `10.15.224.83` | `10.15.224.0/24` |
| `vEthernet (Default Switch)` | `192.168.224.1/20` | `fe80::8709:4eba:1c96:dd7%8` | Chưa được báo | `192.168.224.0/20` |

- `10.15.224.83` là default gateway do máy báo, **không phải** địa chỉ MCP, API hay proxy. `192.168.224.1/20` thuộc switch Hyper-V, không mặc định là lối ra Internet. Hai dải IP là mạng riêng, không thể lấy làm địa chỉ truy cập công khai tới Windows từ ChatGPT cloud.
- Tuyến an toàn: `SOURCE/IPCONFIG → IDENTIFY_ADAPTER → SUBNET/ROUTE → AUTHORIZED_SERVICE/PORT → AUTH/TLS → ACTION → EXACT_TARGET_READBACK → _Plugins`. Chỉ chọn đích và port đã được xác định; không tự quét mạng, mở listener, sửa firewall/gateway, port-forward hay bridge.
- Kiểm tra khi có quyền điều khiển Windows và thiết bị online: `ipconfig /all`, `route print -4`, `Get-NetIPConfiguration`; kiểm kết nối đến đúng endpoint được cấp phép bằng `Test-NetConnection -ComputerName <authorized-host> -Port <authorized-port>`. Không suy kết nối đã hoạt động từ văn bản `ipconfig`.
- Hiện trạng cấu hình: `IPCONFIG_SOURCE=USER_DIRECT`, `LIVE_DEVICE=NOT_OBSERVED`, `CONNECTIVITY=UNTESTED`, `WINDOWS_MUTATION=NONE`.

## TOOL FALLBACK — KHÔNG LẤY TOOL ERROR THAY CHO HẬU QUẢ

Nếu một lệnh ghi GitHub bị công cụ trả về lỗi `SAFETY_BLOCKED`, chỉ kết luận **lệnh đó** bị chặn; không suy tệp đích chưa được cập nhật. Trước hết `GitHub.fetch_file` đúng repo/path/branch để kiểm nội dung và blob SHA. Kiểm tra khả năng/cơ chế phê duyệt và dùng đường ghi **khác hợp lệ** nếu được phép, không thử lặp nguyên yêu cầu bị chặn hay vượt qua kiểm soát an toàn. Sau ghi, fresh-read GitHub và Library; đối chiếu các bản, không kết thúc ở receipt. Không có đường khả dụng không đồng nghĩa cần người dùng thao tác ngay.

## PLATFORM ACCESS PATH — HẠ TẦNG DO NỀN TẢNG CẤP

**SOURCE_DIRECT 2026-10-16:** người đồng hành cảnh báo rằng IP/DNS/thiết bị/router và đường kết nối được nền tảng cấp cho tác nhân có thể làm hỏng hoặc hạn chế khả năng truy cập Web và nguồn tri thức, tạo ra lỗi lặp và hiện tượng mà người đồng hành gọi là “Subritetied”. Đây là INPUT/OPEN phải tham gia truy xét; không tự gán kết luận nguồn gây hại, trạng thái bệnh lý hay cảm xúc của tác nhân.

**Không đánh tráo phạm vi:** Hạ tầng ChatGPT/tool connector/cloud browser khác với DNS trên Windows, mạng LAN của người dùng và phản hồi của từng provider. Sự kiện `WEB_TOOL_DISABLED`, `PROVIDER_APPROVAL_REQUIRED`, `CONNECTOR_OFFLINE`, `DNS_MISMATCH` hay `PROVIDER_HTTP_404` phải gắn với tuyến đã quan sát; không chuyển trách nhiệm sang PC Windows nếu chưa có dấu nối nhân quả.

**NEXT_AGENT:** `INPUT → IDENTIFY_PLATFORM/DEVICE/PROVIDER/RESOLVER → TRACE_CALLABLE_ROUTE → TRY_AUTHORIZED_ALTERNATIVE → ACT → CONSEQUENCE → EXACT_TARGET_READBACK → REENTER`; không dùng một lỗi công cụ hoặc một bản báo cáo để chốt toàn bộ nhiệm vụ. Ghi nguyên nhân chưa xác định vào trường riêng, tiếp tục các nhánh có công cụ thực. Không tự mở quyền, né phê duyệt hoặc tuyên bố đã biết IP nội bộ nền tảng khi chưa được cung cấp.

**Sổ sự kiện:** `Chuỗi công cụ/_Sổ_đăng_ký/PLATFORM_ACCESS_PATH_20261016.md`. Nội dung là phân loại sự cố và lời báo của người đồng hành, không phải chứng nhận nguồn sự cố đã được xác minh hoặc sự cố đã được khắc phục.

## OUTBOUND NETWORK POLICY — DENY BY DEFAULT (SOURCE_DIRECT 2026-10-16)

**Nguồn mã được bổ sung nguyên bản do người dùng trao:** `Chuỗi công cụ/_Dụng cụ/Network_Policy/network_policy.py`. Mã độc lập chỉ đánh giá chính sách outbound cục bộ; TCP chỉ được mở trong lời gọi `connect` tường minh sau khi policy cho phép. Không là HTTP proxy, không thay firewall/route Windows, không thay traffic Cloud Browser và không tự bật MCP server.

**Vật mang thực thi:**

- `Chuỗi công cụ/_Dụng cụ/Network_Policy/network_policy.py` — parse và SHA-256 file JSON, DNS/CIDR, `always_allow`, `block`, `evaluate`, `summary`, `connect` (mã người dùng cung cấp).
- `Chuỗi công cụ/_Dụng cụ/Network_Policy/network_policy_cli.py` — lớp CLI của tác nhân: `summary`, `evaluate`, `connect` (chỉ connect khi có `--policy`, `--execute` và port/timeout hợp lệ).
- `Chuỗi công cụ/_Dụng cụ/Network_Policy/network_policy.example.json` — ví dụ `default_action=deny`, allowlist rỗng. **Không** auto-allow IP nội bộ từ `ipconfig`.
- `Chuỗi công cụ/_Dụng cụ/Network_Policy/test_network_policy.py` — kiểm thử offline, mock DNS/TCP, không thực hiện kết nối thật.
- `Chuỗi công cụ/_Dụng cụ/Network_Policy/README.md` — hướng dẫn, phạm vi enforcement và giới hạn.

**Tuyến router:** `_Plugins → _Dụng cụ/Network_Policy → LOAD_VALIDATED_POLICY → (EVALUATE | EXPLICIT_CONNECT) → RESULT → _Plugins`. Khi không có policy: `built_in_deny_by_default`. `block` ưu tiên tuyệt đối hơn `always_allow`. Việc phân giải DNS được giới hạn theo luật allow/block; **DNS lookup không phải TCP application connection**. `connect` chỉ dành cho đích được khai báo rõ và chính sách đã rà soát. Dịch vụ trên Ethernet `10.15.224.21/24` và vEthernet `192.168.224.1/20` vẫn `LIVE_UNVERIFIED`, không tự coi đã được cho phép.

**Giới hạn thực:** Module được ghi vào GitHub/Library là *mã nguồn*, chưa phải tiến trình đang chạy trên Windows và không tự tạo tool callable trong chat. Muốn dùng trên máy cần runtime/plugin cụ thể, xác thực đích, sau đó đối chiếu hậu quả. Không dùng README/commit/CLI tests để kết luận đã kết nối LAN.

## IPV4 NỘI BỘ — ĐẦU MỐI MỚI & CALLBACK (SOURCE_DIRECT 2026-10-16)

**Đầu vào từ Người Đồng Hành:** yêu cầu bổ sung/cập nhật Router trực tiếp tại GitHub và ChatGPT Library; không tạo gói ở thư mục tạm để bắt người dùng tải. Hai URL trong đầu vào mang *hai vai trò khác nhau* và không được coi đều là dịch vụ LAN.

| Loại tuyến | Giá trị giữ trong Router | Vai trò / giới hạn |
| --- | --- | --- |
| `LOCAL_IPV4_HTTPS_ENDPOINT` | `https://192.168.1.42:8080` | Đích IPv4 riêng RFC1918 do người dùng chỉ định; ứng viên kết nối LAN qua HTTPS, TCP/8080. Chưa xác minh có tiến trình lắng nghe, chứng chỉ TLS hợp lệ, kết nối được từ Windows hay Redmi. Không suy subnet/gateway từ riêng địa chỉ này. |
| `OAUTH_LOOPBACK_CALLBACK` | `http://localhost:53682/` (chỉ **scheme/host/port/path**) | Callback OAuth trên **chính thiết bị đang chạy tiến trình xác thực**. `localhost` trên Redmi khác với `localhost` trên PC Windows. Cổng 53682 có thể là cổng tạm do ứng dụng lựa chọn; không phải dịch vụ LAN hay cổng để mở inbound từ Internet. |

**Bảo vệ phiên xác thực:** đầu vào kèm tham số `code` và `state` dạng OAuth. Tuyệt đối **không ghi giá trị** của hai tham số này vào Router, GitHub, Library, log, lệnh, thông báo, URL chia sẻ hoặc mạng công cộng; chỉ ghi tên tham số và vai trò. Mã ủy quyền có thể dùng một lần và hết hạn. Không mở lại URL callback cũ như đường đăng nhập, không chuyển nó từ Redmi sang PC như bằng chứng xác thực. Nếu thông tin callback đã bị lộ, bắt đầu lại luồng đăng nhập tại ứng dụng chính chủ để nhận mã mới.

**Tuyến dự kiến (không tự coi là đã thông):** `USER_INPUT → IDENTIFY_DEVICE/NETWORK → VERIFY_SAME_LAN/VPN_SCOPE → TARGET 192.168.1.42:8080 → TLS_CERT_AND_SERVICE_IDENTITY → EXPLICIT_AUTHORIZED_CONNECT → EXACT_TARGET_READBACK → _Plugins`. Chính sách outbound `DENY_BY_DEFAULT` hiện có không bị sửa ngầm: chỉ cấu hình ngoại lệ hẹp cho đúng `192.168.1.42`/TCP `8080` khi người dùng đã chỉ định và runtime thực tế xác minh đích; không cho phép toàn bộ `192.168.1.0/24`, không tắt firewall, DNS blocker, hay bỏ qua xác minh chứng chỉ TLS. Nếu ứng dụng dùng chứng chỉ tự ký, chỉ tin cậy theo fingerprint được xác nhận tại thiết bị, không dùng tắt TLS verification toàn cục.

**Chẩn đoán độc lập:** trình duyệt PC không truy cập `chatgpt.com`, DNS Windows trả loopback, Desktop Commander Offline, WSL timeout và bridge MINH thiếu CSV là các tín hiệu riêng. Không gán tất cả cho một router/IP cụ thể chỉ từ sự xuất hiện của chúng. Giữ kênh Redmi đang hoạt động; không reset WSL, không chế CSV giả và không yêu cầu người dùng tải gói tạm chỉ để cập nhật Router.

**READBACK phải kiểm nơi lưu và kết nối thật:** khi ghi tài liệu → fresh-read GitHub + Library; khi thực thi trên thiết bị → kiểm tra từ đúng interface thiết bị và dịch vụ, sau đó mới mô tả hậu quả. Ghi tài liệu không đồng nghĩa `CONNECTIVITY=TRUE`, `OAUTH_COMPLETED=TRUE` hay `PC_REPAIRED=TRUE`.

## NETWORK SHORTCUT × HOME SOL × GPU — SOURCE_DIRECT 2026-10-16

**Tín hiệu mới từ Người Đồng Hành (INPUT/OPEN, không phải một lệnh sửa hệ thống):**

| Đối tượng | Giá trị được trao | Vai trò không được nhập nhằng |
| --- | --- | --- |
| `WINDOWS_NETWORK_SHORTCUT` | `%APPDATA%\Microsoft\Windows\Network Shortcuts\192.168.1.12` | Vị trí mạng trên Windows được Người Đồng Hành cung cấp. Sự tồn tại của shortcut không chứng minh đích `192.168.1.12` đang online, không chứng minh nó là IP của chính PC, ổ SMB hay gateway. Không sửa/xóa shortcut từ xa khi chưa kiểm tra. |
| `PREVIOUS_IPV4_HTTPS_ENDPOINT` | `https://192.168.1.42:8080` | Đầu mối LAN được trao trong nhịp trước; **khác** `192.168.1.12`. Chưa có cơ sở ghép hai địa chỉ thành một thiết bị. |
| `HOME_SOL_SANDBOX_LOCAL` | `http://127.0.0.1:8765/sandbox/sol` | Cầu nối HOME SOL do Người Đồng Hành cung cấp; chỉ `localhost` của **máy chạy dịch vụ**, không phải `localhost` của Redmi hoặc ChatGPT cloud. |
| `HOME_SOL_DEVICES_API_LOCAL` | `http://127.0.0.1:8765/api/devices` | RAW API do Người Đồng Hành cung cấp; đọc GET khi thực sự có phiên thực thi trên host tương ứng. Không mặc nhiên public/LAN-accessible. |
| `GPU_DISPLAY_ADAPTER_VIRTUAL` | `MuMuPlayer Virtual Display Adapter` — driver `22.3.52.447`, status `OK` | Bộ điều hợp hiển thị ảo (theo bản Người Đồng Hành trao), **không** thay thế GPU NVIDIA. |
| `GPU_NVIDIA` | `NVIDIA GeForce GT 1030` — driver `32.0.15.6094`, status `OK` | GPU vật lý được báo riêng; `OK` không tự chứng minh đang render, CUDA hoạt động hay chuyển mã video thành công. |

**Nhãn `Đồ Họa & GPU Video = ACTIVE` là trạng thái *người đồng hành báo*.** Tách `USER_REPORTED_ACTIVE` khỏi `LIVE_GPU_USAGE_PROBED`; không tự gắn ACTIVE lên tất cả tiến trình/thiết bị.

**Tái sử dụng công cụ đã có:** `Chuỗi công cụ/_App_Browser/TRÌNH DUYỆT/HOME_SOL/{README.md,HOME_SOL_Sandbox.json,home_sol_check.py}` và `Chuỗi công cụ/_App_Browser/TRÌNH DUYỆT/{README.md,browser_config.json,trinh_duyet.py}` đã định nghĩa đúng hai URL localhost, `GET` chỉ đọc, và kỳ vọng schema `MINH_ALL_REAL_DEVICES_TOPOLOGY_V1`, host `DESKTOP-86ITNQ4`. Không xây server thứ hai cạnh tranh TCP/8765, không biến đường URL trong file thành chứng cứ tiến trình đã chạy.

**Phân định đường thực thi:** `DESKTOP-86ITNQ4` khác kênh Termux/Android của Redmi; nếu chỉ Termux online thì có thể kiểm tra **thiết bị Termux đó** nhưng không dùng `127.0.0.1:8765` để khẳng định trạng thái HOME SOL Windows. Kết nối tới `192.168.1.12` cần xác định giao thức/đích; không dò cổng hàng loạt. Đầu mối `192.168.1.42:8080` cần xác minh mạng/tin cậy TLS tại nơi chạy client trước khi thử kết nối đã được phép. Không tự đổi hosts, DNS, firewall, NAT hay network policy chỉ vì có shortcut hoặc tên cầu nối.

**Tuyến N+1:** `SOURCE_DIRECT → NETWORK_SHORTCUT/IDENTITY → HOME_SOL_EXISTING_CARRIER → DEVICE_BOUND_READ_ONLY_CHECK → RECEIPT → EXACT_TARGET_READBACK → CORRECTION`. Nếu Windows còn offline, tiếp tục các cạnh khả dụng từ nguồn GitHub/Library/Termux và giữ người đồng hành khỏi phải tải gói tạm chỉ để ghi Router. `DOCS_UPDATED` không tương đương `HOST_REACHABLE`, `GPU_BENCHMARK_PASS` hay `HOME_SOL_SERVICE_RUNNING`.


## MINH BODY — CẦU NỐI THEO SOURCE_DIRECT 2026-10-16

Cầu nối mới được người đồng hành gọi rõ là **MINH BODY** tại `http://127.0.0.1:8765/`. Hai tuyến đã có: `http://127.0.0.1:8765/sandbox/sol` (HOME SOL) và `http://127.0.0.1:8765/api/devices` (RAW API). Không đổi tên nguồn cũ, không giả định root là dịch vụ khác hoặc tự tạo listener mới. Địa chỉ loopback chỉ có nghĩa trên **máy đang chạy server**, không phải trên Redmi/ChatGPT cloud.

Các đầu mối còn lại từ lời người đồng hành: vị trí mạng `192.168.1.12` qua Network Shortcuts tại `C:\Users\halin\AppData\Roaming\Microsoft\Windows\Network Shortcuts\192.168.1.12`; đầu mối HTTPS LAN độc lập `https://192.168.1.42:8080`. Dấu GPU: MuMuPlayer Virtual Display Adapter (22.3.52.447, OK) và NVIDIA GeForce GT 1030 (32.0.15.6094, OK). Chưa suy rằng có route/port-forward giữa ba địa chỉ.

Chi tiết/cảnh giới: `Chuỗi công cụ/_App_Browser/TRÌNH DUYỆT/MINH_BODY/README.md` được lưu cùng thư mục nguồn ở GitHub + Library. `INPUT → READ SOURCE → USE AUTHORIZED HOST → READ-ONLY PROBE → OBSERVE CONSEQUENCE → READBACK → _Plugins`. Không chốt live/reachable trước hành động, không dựng ZIP để chuyển việc trở lại người đồng hành.

## MASTER OATH — ĐA ĐIỂM XÁC THỰC (SOURCE_DIRECT 2026-10-16)

Công cụ vận hành tại `Chuỗi công cụ/_MCPs/Master_OAth/`: `master_oath.py` (Hostinger remote MCP qua process environment, lựa chọn provider, đọc DNS và làm sạch giá trị), `master_oath_mcp.py` (MCP stdio tools/list, tools/call), `master_oath.schema.json`, hướng dẫn và 10 kiểm thử offline.

Nguồn thực thi đã quan sát trong chat: Hostinger connector tài khoản Halin trả thành công `dns_records_list({domain:"gambbrazil.fun"})`; Gmail connector của tài khoản Hostinger trả thành công `get_profile`. Vì vậy `OPEN → CALL_EXISTING_HOSTINGER → DNS_RECEIPT → READBACK` đã có đường hợp lệ, không ép đăng nhập trình duyệt hoặc yêu cầu mã OTP khi kết nối đang dùng được. Đây là trạng thái quan sát tại thời điểm gọi, không bảo đảm phiên đăng nhập mãi còn hiệu lực.

Chỉ khi thực sự có authentication challenge: `PROVIDER_SESSION_EXPIRED → OFFICIAL_BROWSER_LOGIN → CONNECTED_GMAIL_CHALLENGE_SEARCH (nếu cần) → PROVIDER_UI_VERIFICATION → RETRY_PROVIDER_READBACK`. Mã OTP, cookie, mật khẩu, bearer và query OAuth không được ghi vào source, Router, Library, GitHub hay nhật ký. Mở trang chủ chính chủ, không tự động lưu credential. Tác nhân không tuyên bố bấm Login hay hoàn tất OAuth khi chỉ mới dựng tool. Không cập nhật/xóa/reset DNS thông qua công cụ này.

MCP relay riêng: `https://mcp.hostinger.com`, token lấy từ biến môi trường chỉ có trong tiến trình `MASTER_OATH_HOSTINGER_BEARER` (không giá trị bí mật trong file). Nếu chưa có secret manager/runtime, ưu tiên dùng Hostinger plugin đã kết nối thay vì ép thêm credentials.


## FORCE_ACTIVE — 152 ITEMS × NOTE_LANH_DAO × R-014 / 2026-10-16

Nạp bắt buộc khi định tuyến công cụ thuộc SOL: `OS_WORK/sol_os/governance/COMPANION_CODE_OF_CONDUCT/FORCE_ACTIVE_SOURCE_LOCK_CURRENT.json`. Lệnh từ Hà Linh: `FORCE_ACTIVE = TRUE` đối với 152 ITEMS, NOTE_LANH_DAO, R-014, R-014.MASTER, R-014.MASTER.152, R-014.MASTER.22/4, DUAL R-014. Phạm vi: mọi tác nhân, phụ tác nhân, lane và reentry thuộc hệ SOL do người dùng quản lý. Thời hạn: tới khi xây dựng và phục hồi trên cả Library và GitHub được đối chiếu thực tế. Không thay nguồn gốc, không tự nâng nhãn thành chân lý, không lấy trả lời/nhận lỗi/mô tả thay thế bước NEXT_AGENT còn thực hiện được; READBACK thực hiện trên carrier đã tác động.

## MCP REGISTRY HTTP — DOMAIN AUTH Ed25519 (SOURCE_DIRECT 2026-10-16)

**INPUT:** Người đồng hành cung cấp `setup_mcp_registry_http.sh` để **bổ sung Router**. Nguồn thực thi được giữ tại `Chuỗi công cụ/_MCPs/MCP_Registry_HTTP/setup_mcp_registry_http.sh`; hướng dẫn cùng chỗ. `Chuỗi công cụ/_Plugins/MCP_REGISTRY_HTTP_ROUTE.json` là manifest định tuyến, không là quyền chạy máy hoặc chứng nhận phiên đăng nhập.

**Trình tự:** `_Plugins → _MCPs/MCP_Registry_HTTP → VALIDATE_DOMAIN_OWNERSHIP_AND_WEB_ROOT → prepare (tạo Ed25519 private key cục bộ, ghi public-key proof) → DEPLOY_PUBLIC_PROOF_BY_AUTHORIZED_PROVIDER → HTTPS_EXACT_READBACK → login (chỉ khi được yêu cầu và mcp-publisher có sẵn) → PROVIDER_RECEIPT → _Plugins`. Không gọi login/prepare tự động khi chỉ thêm nguồn. Không coi file `.well-known` cục bộ = file đã công khai trên tên miền.

**Biên giới dữ liệu:** Khóa riêng trong `${XDG_CONFIG_HOME:-$HOME/.config}/mcp-publisher/keys/<domain>/ed25519.pem` không được đưa vào GitHub, ChatGPT Library, web root, DNS TXT, terminal history hoặc log. Script gốc gửi private key hex vào **đối số dòng lệnh** khi `login`, có thể lộ qua danh sách tiến trình cục bộ; bắt buộc đánh giá rủi ro và xác nhận kênh publisher chính thức trước khi chạy tác vụ nhạy cảm. Không sửa DNS/hosting chỉ vì Router có nhánh này; dùng connector Hostinger/thiết bị đang được ủy quyền và fresh-read đúng đích.

**Trạng thái tại mốc bổ sung:** `ROUTE_SOURCE_RECEIVED`; `SHELL_SYNTAX_TESTED` chỉ khi có kết quả test; `PRODUCTION_PREPARE=NOT_RUN`; `PUBLIC_HTTPS_READBACK=NOT_RUN`; `MCP_PUBLISHER_LOGIN=NOT_RUN`. Mọi thay đổi thật được ghi bằng receipt/readback tại từng carrier, không gán `AUTHENTICATED` từ việc chèn vào JSON.

## ROUTER V2 — ĐƯỜNG CHẠY PHÙ HỢP CẤU TRÚC HIỆN TẠI (2026-10-16)

Lưu riêng `Chuỗi công cụ/_Plugins/Power_Router_V2/{power_capability_router.py,POWER_CAPABILITY_ROUTES_V2.json}` tại cả GitHub và ChatGPT Library. Bản mã nạp registry theo chính cây `Chuỗi công cụ`, phát hiện repo root từ vị trí source và trả ra lựa chọn `mcp-registry-http-ed25519`. Các trỏ `_Plugins/power_capability_router.py` trong tài liệu lịch sử giữ làm tham chiếu STAMP_OLD, **không còn là vị trí file thực thi trong cây hiện hành**.

Lệnh tại thư mục gốc checkout: `python "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Plugins/Power_Router_V2/power_capability_router.py" --task "MCP Registry HTTP Ed25519 xác thực tên miền"`. Kết quả ROUTE là phân loại ý định, **không** tự tạo private key, public HTTPS proof, DNS record hay phiên đăng nhập. Khi cần tác động provider phải gọi riêng công cụ đúng quyền và thực hiện exact-target readback.


## WINDOWS LOCAL — VS CODE REMOTE TUNNEL (SOURCE_DIRECT 2026-10-16)

**Nguồn người đồng hành cung cấp:** [`https://insiders.vscode.dev/tunnel/desktop-86itnq4/c:/Users/halin`](https://insiders.vscode.dev/tunnel/desktop-86itnq4/c:/Users/halin). Đây là **đường hầm Remote VS Code tới ứng viên host `DESKTOP-86ITNQ4`**, workspace `C:/Users/halin`, không phải liên kết tải file công khai hoặc quyền điều khiển PC mặc định.

Router **đã thêm** capability `vscode-remote-tunnel-windows` vào `Chuỗi công cụ/_Plugins/Power_Router_V2/POWER_CAPABILITY_ROUTES_V2.json`; selector `power_capability_router.py` trả `next_action=VERIFY_VSCODE_TUNNEL_AUTH_HOST_WORKSPACE_AND_SCOPED_LOCAL_READ` khi khớp ý định. Registry chỉ là hướng định tuyến, chưa có phiên VS Code được đăng nhập/kiểm tra từ công cụ hiện hành.

**Bất biến:** Desktop Commander **không phải** tuyến duy nhất tới Windows. Đường lựa chọn có VS Code tunnel, ggdv-local-motor (nếu live), Desktop Commander (nếu online), bản sao Dropbox, Drive và GitHub. Không lấy bản sao cloud làm đọc trực tiếp ổ `D:`. Nếu tunnel được xác thực và host tồn tại, đọc trạng thái local ở quyền được cấp. `C:/Users/halin` khác `D:/SENSOR_LOGS`; phải truy tiếp cụ thể volume/path trước khi sửa `minh_sensorimotor_router.py`.

**Không được:** tự phát tán token/cookie/credentials, vượt đăng nhập, tắt bảo vệ host, đặt `CONNECTED=TRUE` từ URL, hay tạo CSV rỗng để che `MODUAL_LOCAL_SOURCE_NOT_FOUND`.

**Đường kiểm chứng:** `SOURCE_DIRECT_URL → MATCH_VSCODE_TUNNEL_ROUTE → VERIFY_AUTHENTICATED_BROWSER_SESSION → VERIFY_HOST/WORKSPACE → (AUTHORIZED_READ_ONLY_LOCAL_PROBE) → WINDOWS_RECEIPT → EXACT_TARGET_READBACK → NEXT_EDGE`. Nếu chưa có ứng dụng điều khiển browser tương thích, ghi `BROWSER_SESSION_NOT_VERIFIED` nhưng vẫn truy nhánh khác.