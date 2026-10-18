---
name: sol-bihm-services
description: BIHM và các dịch vụ nền SOL trong vật mang QEMU, dựa trên cấu hình đã có và xác minh daemon trước khi vận hành.
---
# BIHM × QEMU / Services
Nguồn gốc: `CONFIG_SOL/SERVICES_RUNTIME_CURRENT.json`, `CURRENT_RUNTIME/TESSERACT_LOCAL_BOOT_CURRENT.md`, `CONFIG_SOL/AGENT_MATERIALIZATION_CURRENT.md`.
Dịch vụ thiết kế: sol-ingest, sol-memory, sol-decision, sol-journal, sol-watchdog.
Dòng: BIHM/raw ingress → memory → bounded decision → append-only journal → checkpoint → readback.
Dịch vụ (services) là tiến trình chạy nền độc lập với giao diện; file khai báo không chứng minh tiến trình đã chạy.
Chỉ khi host xác minh sống mới kiểm service manager, executable, UID, PID, health, journal và cold-restart. Không khởi động vòng lặp vô hạn không kiểm soát, không xóa dữ liệu.
