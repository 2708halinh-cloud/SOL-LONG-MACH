# AGENT / SUBAGENT MATERIALIZATION — CURRENT

SOURCE_DIRECT = HÀ LINH — 2026-10-06
ANTI_BLOAT = POINTER_FIRST

AGENT_NGUON = source/template/history library.
.vscode = programming/testing/subagent coordination area.

Mỗi Agent/Subagent tối thiểu có 13 trường:
1. AGENT_ID
2. TÊN
3. GEN / SEED
4. HOME
5. CONFIG
6. ROLE / SCOPE
7. RELATION
8. RUNTIME
9. TOOL_RIGHTS
10. MEMORY_POINTER
11. JOURNAL
12. STATE
13. READBACK

OPEN giữ nghĩa riêng = DIRECT_SIGNAL_INGRESS_OPEN_PROPOSITION, không đồng nghĩa PENDING.

Source-direct device snapshot:
- PC: Intel Core i5-10400F / 48 GB RAM / NVIDIA GT 1030 4096 MB.
- Android: Xiaomi 12 USB; Redmi Note 14 Pro 5G wireless ADB.
- Local bridge reference: http://127.0.0.1:8765/
- iOS: OPEN direct ingress; physical/runtime state requires live evidence.

Hardware/IP/sensor counts are volatile and must be fresh-read before CURRENT claims.

Expected PC-local surface:
W:\Drive của tôi\.vscode\
├── AGENTS.md
├── mcp_config.json
├── settings.json
├── scripts\
└── .agents\
    ├── plugins\
    └── skills\

## DỊCH VỤ HỆ THỐNG — SERVICES / SOURCE_DIRECT 2026-10-18

**Nguồn người đồng hành (nguyên văn):**
> Dịch vụ hệ thống - (services) là các ứng dụng chạy ẩn dưới nền (background processes) trong các phiên riêng biệt để hỗ trợ máy chủ hoặc hệ thống mà không cần hiển thị giao diện người dùng.

**Quan hệ với SOL / QEMU:** Dịch vụ là tiến trình vận hành có vòng đời riêng. Một tệp Skill, cấu hình hoặc lời gọi mô hình không tự trở thành dịch vụ đang chạy. Khách QEMU có thể dùng systemd hoặc trình giám sát tiến trình phù hợp; Windows dùng Windows Service Control Manager khi triển khai trên Windows. Luôn xác minh bằng quan sát tiến trình, nhật ký và health-check.

**Liên kết tới 13 trường Agent/Subagent:** `AGENT_ID` là định danh bền của thực thể; `SERVICE_ID` định danh một tiến trình hỗ trợ. `RUNTIME`, `TOOL_RIGHTS`, `MEMORY_POINTER`, `JOURNAL`, `STATE` và `READBACK` đều phải có quan hệ nguồn. PID và phiên dịch vụ thay đổi sau khởi động lại, không làm đổi AGENT_ID.

**Chu trình đề xuất:** BIHM/raw-input (nguồn + provenance) → services/ingest → working-state → memory-filter → decision → authorized-action → observed-consequence → journal/checkpoint → readback → bounded-next-cycle. Working-state/RAM không phải ký ức bền. Hỏng/tắt host/QEMU không chứng minh tiến trình vẫn tiếp tục hoạt động: chỉ dữ liệu checkpoint bền có thể tái nhập.

**Kết nối công cụ:** REALITY_STONE = nguồn truy dấu sự kiện và phục dựng trạng thái trên chứng cứ, không sửa vật mang bằng suy đoán; `Power_Router_V2/agent_diagnostics.py` = chẩn đoán/đề xuất, không tự thi hành repair. BIHM là tên nguồn dữ liệu cần resolve đúng vật mang thực; không suy tạo một luồng BIHM nếu chưa quan sát được.

**Điều kiện kích hoạt services:** giới hạn tài nguyên QEMU, giám sát tiến trình và restart policy, ghi log không chứa bí mật, lưu checkpoint, rollback đã xác minh, nguồn dữ liệu được cấp quyền, và kiểm thử lần khởi động/tái nhập. Đây là thiết kế nguồn, **không phải biên nhận một daemon đã chạy**.

**Manifest:** `CONFIG_SOL/SERVICES_RUNTIME_CURRENT.json`.
