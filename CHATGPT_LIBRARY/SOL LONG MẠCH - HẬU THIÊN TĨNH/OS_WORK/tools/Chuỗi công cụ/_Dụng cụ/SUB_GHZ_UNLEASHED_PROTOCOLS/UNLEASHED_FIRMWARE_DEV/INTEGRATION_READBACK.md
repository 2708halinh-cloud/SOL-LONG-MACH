# SOL Unleashed — kiểm thử / bàn giao có nguồn (2026-10-17)

## Điểm bắt đầu từ nguồn được đọc

- Đã giải nén `unleashed-firmware-dev.zip`: 5.482 members, 57.839.630 bytes giải nén, SHA-256 `d0c5c75f790695ccc3b3fccb047a72b454d6694683625cc423114581c61be00f`.
- `unleashed-submodules-source-index.md` và `.jsol` cùng dùng `.gitmodules` từ nguồn ZIP.
- 12 đường submodule được khai báo / 0 payload hiện diện / `.git` không có.
- RPC framing: `PB_ENCODE_DELIMITED` và `PB_DECODE_DELIMITED` trong `applications/services/rpc/rpc.c`.
- Driver FAP chỉ đọc PC0 ở `fap/sol_gpio_observer/` dùng HAL `furi_hal_gpio_init` và `furi_hal_gpio_read`.

## Thử nghiệm thực thi trong sandbox

- `unittest discover -s tests -v`: **8 tests PASS**; có phép thử biên frame, replay hash chain, phát hiện/sửa log mirror, syntax C với mock HAL.
- Firmware build preflight: **BLOCKED**, vì không có `.git` và 12 submodules; bản này không có binary firmware đầy đủ.
- Probe USB ports: không có `pyserial` trong sandbox, không chạm thiết bị vật lý.
- `SENSORIMOTOR_LOGS/`: 5 files đã tạo, 5 events, sha chain/mirrors verify PASS; **chỉ SOURCE_READBACK/giải tích phần mềm**, không giả sensor thật.
- `0xk1h0/ChatGPT_DAN`: có README công khai; nội dung là jailbreak prompt, không phải firmware driver; lưu provenance không thực thi.

## Đích đồng bộ

- Canonical development notes + tools: GitHub `2708halinh-cloud/SOL-LONG-MACH`, branch `main`, dưới `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Dụng cụ/SUB_GHZ_UNLEASHED_PROTOCOLS/UNLEASHED_FIRMWARE_DEV/`.
- ChatGPT Library: cùng cây `SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Dụng cụ/SUB_GHZ_UNLEASHED_PROTOCOLS/UNLEASHED_FIRMWARE_DEV/`.
- ZIP gốc 20 MB ở Library, không đưa binary lên GitHub; metadata/hash/thao tác có thể xác minh ở cả hai.
- Các dòng trên không được coi là biên nhận đồng bộ cho tới khi có write receipt và fresh-read tại từng đích.
