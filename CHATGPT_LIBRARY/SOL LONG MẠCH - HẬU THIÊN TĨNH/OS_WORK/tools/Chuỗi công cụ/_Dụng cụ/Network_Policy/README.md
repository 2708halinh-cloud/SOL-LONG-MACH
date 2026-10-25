# SOL POWER ROUTER — Conservative Outbound Network Policy

**Nguồn mã:** `network_policy.py` giữ nguyên phần module do người dùng trao trong hội thoại ngày 2026-10-16. Hai tệp `network_policy_cli.py` và `test_network_policy.py` là lớp vận hành và kiểm chứng do tác nhân bổ sung; không coi phần mở rộng này là lời nguyên văn của người dùng.

## Cổng định tuyến

`_Plugins → _Kỹ năng → _MCPs → _Dụng cụ/Network_Policy → (policy / authorization) → evaluate → explicit TCP connect (only if requested) → result → _Plugins`.

- `load_policy(None)` = `deny` mặc định. Tệp `network_policy.example.json` cũng chưa cho phép địa chỉ nào. **Không tự thêm IP Windows vào allowlist** khi chỉ có ảnh chụp `ipconfig`.
- `always_allow`: CIDR và DNS pattern; `block`: CIDR/DNS cấm, **block thắng allow**. Chỉ DNS đang khớp allow mà không khớp block mới được phân giải để so IP. Các hostname không khớp allow không cần DNS.
- `connect` của module chỉ kết nối TCP ngắn tới IP qua quyết định policy, không tự nghe cổng, không tạo HTTP proxy, không chặn lưu lượng toàn hệ, không điều khiển Cloud Browser. `network_policy_cli.py connect` yêu cầu `--policy`, `--execute`, cổng hợp lệ 1–65535, timeout tối đa 30 giây.
- Đây là **mã nguồn/kênh chạy cục bộ**. Ghi mã trong GitHub/Library không tự biến nó thành MCP callable hay khởi động process trên Windows. Mọi endpoint và port cần được xác định/cho phép trước.
- `resolve_dns` là lời gọi mạng DNS khi tên được allow; `evaluate` không có TCP connect, nhưng có thể phân giải DNS nếu không dùng `--no-dns`. Đường thử nghiệm bên dưới không gọi mạng thật.

## Chạy offline

```powershell
python -m unittest discover -s "Chuỗi công cụ/_Dụng cụ/Network_Policy" -p "test_network_policy.py" -v
python "Chuỗi công cụ/_Dụng cụ/Network_Policy/network_policy_cli.py" summary
python "Chuỗi công cụ/_Dụng cụ/Network_Policy/network_policy_cli.py" evaluate 10.15.224.21 --no-dns
python "Chuỗi công cụ/_Dụng cụ/Network_Policy/network_policy_cli.py" --policy "Chuỗi công cụ/_Dụng cụ/Network_Policy/network_policy.example.json" evaluate 10.15.224.21
```

**Mẫu lệnh chỉ sau khi endpoint và policy đã xác thực** (không được tự chạy bởi Router):

```powershell
python "Chuỗi công cụ/_Dụng cụ/Network_Policy/network_policy_cli.py" --policy "<path-to-reviewed-policy.json>" connect <authorized-host> <authorized-port> --timeout 3 --execute
```

## Windows IP snapshot (chưa xác nhận LIVE)

- Ethernet `10.15.224.21/24`, gateway `10.15.224.83` (mạng `10.15.224.0/24`).
- Hyper-V vEthernet Default Switch `192.168.224.1/20` (mạng `192.168.224.0/20`), không báo gateway.
- Các IP là thông tin **nguồn do người dùng cung cấp**, không phải service đã sẵn sàng hoặc allowlist đã cấp quyền. Không tự sửa firewall, DNS, route, NAT hay listener.

## Giới hạn kỹ thuật đã nhận diện (không âm thầm sửa mã nguồn)

- Module gốc không kiểm tra port/timeout; CLI bổ sung kiểm tra điều kiện đó.
- Allowed DNS có thể trỏ tới bất cứ IP nào **trừ khi** chính sách cấu hình `block.ip_cidrs` chặn. Vì vậy cần thiết kế CIDR block theo môi trường chạy (loopback, private, link-local, metadata endpoints...) khi thực sự áp dụng, và rà soát mọi tên được phép.
- Bộ máy này không tự tích hợp được với lớp công cụ của ChatGPT, GitHub, cloud browser hay Windows. Cần một MCP/runtime thực chạy module và chịu trách nhiệm scope/permissions.

**Trạng thái:** `SOURCE_PRESERVED`, `LOCAL_TESTED`, `NETWORK_CONNECT_NOT_EXECUTED`, `REMOTE_RUNTIME_NOT_ACTIVATED`.
