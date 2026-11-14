# PCXT BIOS Workbench — cấu hình OS_WORK

Plugin đã cài có Assembly reference, `inspect_source.py` và `inspect_rom.py`. Cấu hình này thêm một bản kiểm tra ROM bằng Python thuần và bài thử trên dữ liệu giả lập nhỏ, **không** dùng file BIOS gốc làm dữ liệu thử khi chưa có file thực.

- Source gốc: Super PC/Turbo XT BIOS 3.1; SHA-256 trong `config.json` do SOURCE_NOTES của plugin công bố, **chưa tính lại trong phiên này**.
- Firmware build, ROM thật, bo mạch thực: `NOT_TESTED`.
- OAuth client: `NOT_APPLICABLE`. Không ghi khóa OAuth của Workspace vào BIOS.

Dùng: `python3 scripts/inspect_rom.py path/to/ROM.bin` hoặc `python3 scripts/selftest.py`.
