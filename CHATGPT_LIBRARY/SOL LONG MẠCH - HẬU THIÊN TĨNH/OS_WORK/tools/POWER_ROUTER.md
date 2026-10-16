# POWER ROUTER — T007 / OPEN

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
