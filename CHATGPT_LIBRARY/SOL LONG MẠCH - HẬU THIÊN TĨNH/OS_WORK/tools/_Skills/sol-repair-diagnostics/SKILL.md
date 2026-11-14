---
name: sol-repair-diagnostics
description: Dùng công cụ sửa chữa REALITY_STONE và agent_diagnostics.py của SOL, kiểm chứng nguồn, nguyên nhân lỗi và readback.
---
# REALITY_STONE / Power Router — Diagnostics
Nguồn hiện hữu trong repo:
- `Chuỗi công cụ/_Plugins/REALITY_STONE/reality_stone.py` và `test_reality_stone.py`.
- `Chuỗi công cụ/_Plugins/Power_Router_V2/agent_diagnostics.py` và `test_agent_diagnostics.py`.
Chu trình: kiểm nguồn và trạng thái host → đọc lỗi → thử phép kiểm không phá hủy → sửa tối thiểu → chạy test → đọc lại đúng target. Source code ≠ runtime deployed. Giữ bí mật ngoài output/log.
