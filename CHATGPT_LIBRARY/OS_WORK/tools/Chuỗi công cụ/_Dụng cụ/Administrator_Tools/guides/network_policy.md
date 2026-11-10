# Network Policy — evaluate trước connect

Nguồn: `POWER_ROUTER.md` và `Network_Policy/README.md`. Mặc định module chính sách outbound chỉ đánh giá; chỉ connect khi có policy hợp lệ và đích được khai báo rõ. Không tự thêm toàn dải LAN; kiểm địa chỉ giao diện, chứng chỉ TLS, consent và đích. Loopback `127.0.0.1` là chính máy chạy client, không phải tự động IP nguy hiểm. `192.168.1.42:8080` là đầu mối user-provided, không chứng minh TCP reachability.

Không tắt firewall/DNS hàng loạt. Khi API/connector của nền tảng bị hạn chế, phân biệt lỗi provider/cloud với lỗi PC/WSL, không gán nguyên nhân một chiều.