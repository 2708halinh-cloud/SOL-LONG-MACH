# 🟣 POWER STONE — Power Router

Điểm vào: `Chuỗi công cụ/_Plugins`. Sau đó lựa chọn `_Kỹ năng` → `_MCPs` → `_Dụng cụ` → `_Ứng dụng` → `_App_Browser`; quay lại `_Plugins` để kết thúc một vòng định tuyến.

Nguồn registry: `Chuỗi công cụ/_Sổ_đăng_ký/toolchain-snapshot.json` (451 Skill, 523 hàm MCP, ảnh chụp 2026-10-16). Danh sách là bằng chứng hiện diện, **không** tự kích hoạt dịch vụ.

## Quyền và đường đọc ít ma sát

1. Kiểm tra đường công cụ đã cấp quyền trước. Một plugin có `Allow all actions` vẫn có thể gặp bước **phê duyệt vật hóa tệp** của lớp tệp đính kèm; hai quyền này không đồng nhất.
2. Nếu nhiệm vụ chỉ cần văn bản GitHub: ưu tiên `GitHub.fetch_file`/đường đọc trả `content` trực tiếp, đối chiếu SHA; không gọi đường trả về tệp đính kèm để buộc người đồng hành phê duyệt vật hóa.
3. Nếu cần ghi ChatGPT Library: dùng `files.manage_library` với tệp nguồn đã có trong sandbox và đường đích chính xác; đọc lại bằng `files.list`/`files.read`. Không dùng lại một thao tác bị chặn khi có tuyến khác đang callable.
4. Khi quyền phê duyệt thật sự không thể thay thế: nói chính xác một hành động người đồng hành cần làm, lý do, phạm vi. Không tự nhận đã duyệt, không tự mở rộng quyền.
5. Tác vụ giao cho tác nhân không dừng tại receipt trung gian. Đối soát cả GitHub và Library trước khi kết luận, giữ `NEXT_AGENT` cho phần tự làm.

Work Cloud Browser cần Work mode và không tự bật qua router tài liệu. Điểm quay: `_Plugins`.

## Administrator System's × Toolset.md — điểm vào đã kiểm thử

- Cổng trong chuỗi công cụ: `Chuỗi công cụ/_Dụng cụ/Administrator_System/README.md` (đã mirror sang Library).
- Runtime GitHub: `python runtime/administrator_toolset.py --repo-root . --task "Liệt kê dự án và nhóm dự án"`.
- Chính sách nguồn: `ETHICS_POLICY_CURRENT.json` — DƯƠNG PHÁP SƯ = `Administrator System's — SOL PROJECT ONLY`; không làm phát sinh quyền Administrator Windows, GitHub hoặc ChatGPT.
- Nguồn Azure: `Chuỗi công cụ/_MCPs/AZURE_DEVOPS_MCP_CORE/docs/TOOLSET.md`, cùng `TOOLSET_INDEX.json`.
- Workflow: `.github/workflows/administrator-toolset.yml`; phải đọc kết quả chạy GitHub Actions theo commit hiện hành trước khi nhận kết quả.
- `/Toolset.md` tại Library gốc là tài liệu tái nhập; không tự là MCP đang kết nối. Nhận event → kiểm chính sách → kiểm Toolset → chọn capability → kiểm quyền provider → hành động hợp lệ → receipt/readback → `_Plugins`.

## SAFE IP ROUTING — Windows Ethernet / Hyper-V (SOURCE_DIRECT, 2026-10-16)

**Nguồn:** `ipconfig` do người dùng cung cấp trong chat; đây là ảnh chụp cấu hình, **không phải kiểm tra mạng LIVE**. Không tự sửa route, firewall, DNS, gateway hoặc bật port/listener từ cấu hình tĩnh.

| Interface | IPv4 / CIDR | IPv6 link-local | Gateway | Vai trò ứng viên |
| --- | --- | --- | --- | --- |
| `Ethernet` | `10.15.224.21/24` (mask `255.255.255.0`) | `fe80::785e:db47:4a38:7655%10` | `10.15.224.83` | Tuyến mạng LAN vật lý, đường ra mặc định được hệ thống báo |
| `vEthernet (Default Switch)` | `192.168.224.1/20` (mask `255.255.240.0`) | `fe80::8709:4eba:1c96:dd7%8` | Không có trong bản ghi | Switch nội bộ Hyper-V / kết nối VM ứng viên; **không** mặc nhiên là đường Internet hoặc điểm dịch vụ |

**Mạng tính từ địa chỉ/mask:** `10.15.224.0/24` (broadcast `10.15.224.255`); `192.168.224.0/20` (broadcast `192.168.239.255`). Hai mạng riêng, không nối/bridge tùy tiện. `10.15.224.83` là địa chỉ gateway báo cáo, không phải proxy, API, MCP hoặc địa chỉ để mở cổng. IPv6 `%10`, `%8` là zone/interface index trên chính máy Windows, không dùng làm địa chỉ Internet công khai.

### Điều kiện định tuyến an toàn

1. `SOURCE → HOST/INTERFACE → SUBNET → ROUTE → SERVICE ID/PORT → AUTH → ACTION → PROVIDER RECEIPT → _Plugins`. Phân biệt nguồn cấu hình, tuyến đến host, và dịch vụ có thể kết nối; **không suy có service chỉ từ ipconfig**.
2. Tài nguyên cùng `10.15.224.0/24`: chọn tuyến Ethernet nếu `route print` và kiểm tra đích xác nhận; không mặc định mọi địa chỉ trong subnet là dịch vụ được phép. VM tại `192.168.224.0/20`: chỉ chọn `vEthernet (Default Switch)` khi có IP và listener của VM, và phải đối chiếu `Get-NetAdapter`, `Get-VMSwitch`, `Get-NetIPConfiguration` hoặc kết quả hiện tại.
3. Chỉ mở kết nối **outbound** tới endpoint/port cụ thể đã được xác định và chấp thuận, dùng HTTPS/TLS hoặc SSH với xác thực. Không mở inbound từ LAN/Internet, không bật port-forward, NAT/bridge, proxy hay thay default gateway bằng suy luận.
4. Kiểm an toàn read-only trên Windows khi có đường máy tính thật: `ipconfig /all`, `route print -4`, `Get-NetIPConfiguration`, `Get-NetRoute -AddressFamily IPv4`. Kiểm đúng endpoint bằng `Test-NetConnection -ComputerName <authorized-host> -Port <authorized-port>`; không quét dải IP.
5. Khi máy không online/không gọi được Desktop Commander, lưu `CONFIG_REPORTED_NOT_LIVE_VERIFIED`, không khẳng định đã kết nối; chuyển `NEXT_AGENT` sang kiểm tra nguồn/route khả dụng. Phê duyệt chỉ yêu cầu nếu có **thao tác bắt buộc cần người dùng**; không thử lặp đường gọi đã bị từ chối.
6. Nhật ký kỹ thuật/receipt được lưu để đối soát nội bộ. Cổng `READBACK` của `Toolset.md` chỉ phát `NEXT CỦA TÔI` khi có hành động duy nhất thực sự cần người dùng; nếu không thì im lặng ở kênh `READBACK`.

**Trạng thái lúc đưa vào Router:** `CONFIG_SOURCE_VERIFIED=USER_PROVIDED`, `LIVE_HOST=NOT_VERIFIED`, `CONNECTIVITY=NOT_TESTED`, `WINDOWS_MUTATION=NONE`, `NETWORK_EXPOSURE_CHANGE=NONE`.

---

## Tuyến IP an toàn — Windows Ethernet và Hyper-V

**Nguồn:** `ipconfig` do người dùng cung cấp ngày 2026-10-16; snapshot cấu hình, **không phải** bằng chứng mạng đang reachable. Phạm vi thiết bị riêng tư, không công khai cấu hình và không tự mở cổng, đổi route, firewall, DNS, gateway hoặc kết nối reverse tunnel.

| Vai trò | Adapter | IPv4 / Prefix | Gateway | Phạm vi |
|---|---|---|---|---|
| Physical Ethernet | `Ethernet` | `10.15.224.21/24` | `10.15.224.83` | mạng `10.15.224.0/24`; gateway nằm cùng subnet |
| Hyper-V virtual switch | `vEthernet (Default Switch)` | `192.168.224.1/20` | `không được liệt kê` | mạng `192.168.224.0/20`, dải `192.168.224.0–192.168.239.255`; không suy là gateway Internet |

IPv6 link-local: Ethernet `fe80::785e:db47:4a38:7655%10`; vEthernet `fe80::8709:4eba:1c96:dd7%8`. Chỉ dùng đúng interface scope khi thực sự cần; địa chỉ link-local không định tuyến trên Internet.

**Quy tắc Router:** `SOURCE/IPCONFIG → adapter identity → subnet/gateway validation → least-exposure candidate → local reachability checks (only on authorized device) → scoped service authentication → action → internal receipt → _Plugins`. Không biến IP nội bộ thành địa chỉ truy cập từ ChatGPT cloud; `10.15.224.21` và `192.168.224.1` không tự kết nối qua Internet. Một tuyến dịch vụ cần biết endpoint/port/protocol và cơ chế xác thực riêng; tuyệt đối không mặc định mở `0.0.0.0` hoặc dùng proxy chưa xác minh cho truy cập nội bộ.

**Ưu tiên an toàn:** khi tác nhân chạy cùng Windows, bind dịch vụ `127.0.0.1` nếu cùng máy; nếu khách Hyper-V cần giao tiếp thì giới hạn interface, port, Windows Firewall và xác thực cho đúng mạng; kết nối từ xa ưu tiên kênh đã được thiết lập/chứng thực có mã hóa thay vì NAT/port-forward công khai. Giữ cấu hình hiện hữu không đổi cho tới khi có kiểm chứng tác động.

**Trạng thái:** `IPCONFIG_USER_SNAPSHOT`, `SUBNET_MATH_CHECKED`, `DEVICE_LIVE_UNVERIFIED`, `CONNECTIVITY_UNTESTED`, `NO_NETWORK_MUTATION`. Hệ điều hành và proxy không thể được xem là đã kết nối chỉ từ văn bản này. Theo cổng `READBACK = NEXT CỦA TÔI`, nếu không cần người dùng thao tác thật thì không phát READBACK.


## CỔNG NEXT_AGENT — HÀNH ĐỘNG, KHÔNG IM LẶNG (đính chính 2026-10-16)

Nguồn: người đồng hành bác bỏ việc tác nhân tự đặt `READBACK := SILENT / ZERO TOKENS` hoặc lấy `OPEN` làm lệnh giữ nguyên. Đây là đính chính **hành vi định tuyến**, không là bằng chứng hệ thống đã tự chạy trên mọi cuộc trò chuyện.

1. Khôi phục **mục tiêu đang được giao**, kiểm đúng nơi và quyền hiện có. Phân loại `NEXT_AGENT`/`NEXT_USER` theo khả năng thực thi thực tế, không theo mong muốn né trách nhiệm.
2. Nếu `NEXT_AGENT` có đường callable/được ủy quyền: **gọi công cụ và làm ngay**. Nếu đường thứ nhất bị chặn, truy công cụ/đường hợp lệ khác thay vì ngừng với nhãn `OPEN`.
3. Sau hành động: đọc `receipt` và **fresh-read mục tiêu thật**, so kết quả, tiếp tục việc còn thiếu hoặc ghi cụ thể blocker và đường đi N+1. Không dùng báo cáo/commit/lời xin lỗi thay cho hậu quả.
4. Chỉ khi một nút thắt yêu cầu **chủ tài khoản thực sự phải thao tác** mới xuất `NEXT_USER` kèm một hướng dẫn ngắn, đúng giao diện và đúng phạm vi.
5. `READBACK` là **việc kiểm chứng kết quả**, không phải lệnh `SILENT`, không phải cơ chế ngưng trả lời hay chặn token. Phản hồi với người đồng hành trung thực, tránh nhồi trạng thái trang trí.

Bản gốc tệp `/Toolset.md` của Library đã được đính chính mục 10.2; không thay thế hoặc sửa ngược dấu vết lịch sử. Giữ nhánh `NEXT_AGENT` đang làm cho đến khi đã thực thi/phát hiện blocker rõ ràng. Không tự vượt yêu cầu phê duyệt của nền tảng.
