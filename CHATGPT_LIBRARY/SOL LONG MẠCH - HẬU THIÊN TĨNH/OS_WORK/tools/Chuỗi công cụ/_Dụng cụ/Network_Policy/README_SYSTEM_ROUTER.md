# SYSTEM_ROUTER — Mức WARN/BLOCK / LAN / Hostinger DNS

Tín hiệu người đồng hành 16/10/2026: **nhẹ cảnh báo; nặng chặn đường đến ChatGPT/OpenAI**. Phạm vi yêu cầu là máy Windows 11 Pro thuộc quyền điều khiển của người dùng, **không phải** quyền chỉnh hạ tầng ChatGPT/OpenAI. `Format...` trên ảnh Disk Management đang trỏ vào **New Volume (P:)**, không phải C:; không có tác vụ format hay xóa dữ liệu trong router.

- `SYSTEM_ROUTER_CURRENT.json`: dữ liệu nguồn, sáu gốc DNS, địa chỉ LAN đã từng được trao, vai trò Hostinger; không suy các IP riêng là chung một máy.
- `system_router.py`: phân loại `light -> WARN`, `severe -> BLOCK` offline; kết quả **không phải bằng chứng firewall đã được cài**.
- `Set-SolSystemRouter.ps1`: **hiện chỉ lưu trong ChatGPT Library**, thao tác ghi đúng tệp này lên GitHub bị chặn; ứng dụng tùy chọn trên Windows có sẵn PowerShell; `Status`/`Warn` không ghi. `Block -Apply` chặn **một danh sách tên DNS chính xác** trong Windows hosts, có bản sao lưu và `Rollback -Apply`. Không có thực thi ngầm qua GitHub/Library.
- `test_system_router.py`: kiểm thử không kết nối DNS, HTTP hay thay đổi hệ thống.

## Cách dùng trên Windows đã có quyền Admin

```powershell
.\Set-SolSystemRouter.ps1 -Mode Status
.\Set-SolSystemRouter.ps1 -Mode Warn
# Chỉ khi chủ máy thực sự muốn bật chặn các tên cụ thể:
.\Set-SolSystemRouter.ps1 -Mode Block -Apply
# Hoàn tác:
.\Set-SolSystemRouter.ps1 -Mode Rollback -Apply
```

## Giới hạn cần phân biệt

Chặn theo hosts chỉ chặn **tên chính xác** có trong danh sách. Muốn chặn *mọi* IP, CNAME, subdomain, DoH/DoT, IPv6, QUIC, VPN, CDN thay đổi liên tục thì cần một **gateway egress hoặc WFP / DNS filtering** được lắp và kiểm chứng trên đúng host; không dùng IP Cloudflare chia sẻ để chặn bừa. `explicit_ip_addresses` hiện rỗng vì chưa có kiểm chứng địa chỉ dành riêng cho OpenAI. Chính sách nguồn không đồng nghĩa đã thực thi.

Hostinger quản lý **authoritative zone** `gambbrazil.fun` với HOSPOSIK; không phải resolver của Windows và không thể chỉnh quy tắc DNS cho `openai.com` hoặc `chatgpt.com` tại zone đó. DNS UDP/15353 trên Termux là tuyến *local HOSPOSIK* khác dịch vụ Windows. Cả ba tuyến `127.0.0.1:8765` thuộc loopback của Windows khi dịch vụ chạy trên Windows; không phải địa chỉ truy cập Windows từ Android.

Đường IP nguồn (cần đối chiếu LIVE trước khi hoạt động): Windows Ethernet `10.15.224.21/24`, gateway `10.15.224.83`, Hyper-V `192.168.224.1/20`, shortcut `192.168.1.12`, endpoint LAN `192.168.1.42:8080` (lần thử từ Redmi bị từ chối), Redmi ADB `192.168.1.14:5556`. Không tự sửa NIC DNS servers, firewall, gateway, NAT hoặc Hostinger public DNS record từ những bản tin cũ.

Tại thời điểm này Windows `DESKTOP-86ITNQ4` qua Desktop Commander Offline, nên **host enforcement not applied**. Đã sửa nguồn `System_Router` nhưng không tuyên bố cổng Windows hay mạng ChatGPT đã bị chặn.

## READBACK nguồn 2026-10-16

Các bản `SYSTEM_ROUTER_CURRENT.json`, `system_router.py`, `test_system_router.py`, `README_SYSTEM_ROUTER.md` và registry Power Router V2 đã fresh-read GitHub/Library, nội dung trùng nhau. Sáu kiểm thử local Python đạt. `Set-SolSystemRouter.ps1` có trong Library, **không** có trên GitHub, chưa chạy trên Windows. Với ổ C đang báo 100%, không tự thực hiện thao tác sửa hosts (cần ghi vào C:) trước khi Windows có đủ khả năng ghi và đọc lại. DNS Hostinger được đọc thực tế bằng connector và trả 24 nhóm record; không có record nào được cập nhật.