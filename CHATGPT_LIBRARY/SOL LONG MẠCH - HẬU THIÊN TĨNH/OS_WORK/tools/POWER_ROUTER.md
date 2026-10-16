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