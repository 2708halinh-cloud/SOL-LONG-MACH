# Unleashed Firmware — source archive tool

**SOURCE_DIRECT:** `unleashed-firmware-dev.zip`, uploaded by the user on 2026-10-17. This is the **Flipper Zero Unleashed Firmware** development-source snapshot (upstream `DarkFlippers/unleashed-firmware`), not a website editor or a ready-to-flash firmware image. The original archive is preserved separately in ChatGPT Library, in this exact tool directory.

## Executable entry point

Requires Python 3.10+ standard library; no network access, API token or authentication:

```sh
python unleashed_source.py /path/to/unleashed-firmware-dev.zip
python unleashed_source.py /path/to/unleashed-firmware-dev.zip --extract-to /new/empty/directory
```

The tool verifies SHA-256, ZIP CRC, member count and safe paths before optional extraction. It does **not** compile firmware, flash a device, or transmit/receive Sub-GHz signals.

## Source receipt

- ZIP SHA-256: `d0c5c75f790695ccc3b3fccb047a72b454d6694683625cc423114581c61be00f`
- Archive members (files + directories): `5482`
- Uncompressed size: `57,839,630` bytes; ZIP size: `20,245,387` bytes
- CRC: PASS; unsafe traversal paths: 0; symlink members: 0 (observed from provided ZIP)
- Top-level source folder: `unleashed-firmware-dev/`; contains `ReadMe.md`, `LICENSE` (GNU GPLv3), `fbt`, `fbt.cmd`, `.gitmodules` and firmware source code.
- The ZIP alone is not proof of a complete build environment: `fbt` expects Git submodules and a toolchain, and the source archive is not a running MCP/ChatGPT plugin.

**Carrier distinction:** GitHub stores this working inspection utility and provenance files. **The 20 MB source ZIP itself is held in the equivalent ChatGPT Library folder** and is identified by the SHA-256 above; the original binary has not been uploaded to GitHub. Keep attribution and upstream license when redistributing modified source. Integration with X-TiME-Web / `gambbrazil.fun` is **not implied**.

## 2026-10-17 — Giải nén, phân vùng chức năng và SENSORIMOTOR

**Nguồn đã đọc thực:** `.gitmodules`, `documentation/HowToBuild.md`, `documentation/fbt.md`, `documentation/BuildingFapsOnAndroid.md`, `.github/workflows/pr-build.yml`, `applications/services/rpc/rpc.c`, `rpc_gpio.c`, `targets/f7/furi_hal/*` từ chính ZIP người dùng cung cấp.

### Công cụ thực thi Python 3.10+ (không phụ thuộc mạng)

| Tên file | Chức năng | Biên thực tế |
|---|---|---|
| `unleashed_source.py` | Kiểm tra CRC/SHA và giải nén không traversal | PASS trên ZIP này |
| `unleashed_source_index.py` | Đọc `.gitmodules`, liên kết 12 module và các lớp RF/NFC/RFID/IR/GPIO/BLE/USB/RPC/FAP, xuất `.md` + `.jsol` (JSON) | Đã chạy; 12 submodule thiếu payload |
| `unleashed_build_diagnostics.py` | Nhận dạng crash/HardFault, API FAP, compile/link, Sub-GHz, RPC/protobuf, Storage/FATFS, BLE/USB; kiểm tra FBT trước build | Đã chạy preflight; firmware build bị chặn do thiếu submodules/gitlinks |
| `unleashed_rpc_transport.py` | Phân tích nanopb *length-delimited* protobuf frames, đọc thông tin USB serial và thụ động nhận byte CDC khi chỉ định port | Frame unit tests PASS; chưa có schema PB_Main cho decode đầy đủ |
| `unleashed_sensorimotor.py` | Ghi **5 nhật ký** theo nguồn quan sát và chuỗi hash; phát hiện sửa log; phục hồi các bản sao log phụ từ chrono | 5 log đã tạo/verify, đây là nhật ký phần mềm ngoài mô hình |
| `fap/sol_gpio_observer/` | FAP mẫu + driver STM32WB55 HAL, đọc **chỉ** chân mở rộng PC0 (input) 10 lần, không phát RF | C syntax kiểm tra với mock HAL PASS; **chưa build FAP thật/chưa chạy thiết bị** |

### Lệnh vận hành

```bash
python unleashed_source_index.py /path/to/extracted/unleashed-firmware-dev --out-dir . --sha256 d0c5c75f790695ccc3b3fccb047a72b454d6694683625cc423114581c61be00f
python unleashed_build_diagnostics.py build /path/to/unleashed-firmware-dev --target updater_package
python unleashed_build_diagnostics.py diagnose /path/to/build-or-crash.log
python unleashed_rpc_transport.py ports
python unleashed_rpc_transport.py frame-check /path/to/captured-rpc-delimited.bin
python unleashed_sensorimotor.py --logs-dir SENSORIMOTOR_LOGS verify
python -m unittest discover -s tests -v
```

`build` không thi hành nếu thiếu `--execute`; ngay cả với `--execute`, khi thiếu các submodule nó từ chối build, không tự xóa dữ liệu hoặc flash. Trên **checkout đầy đủ** từ nguồn gốc, chạy `git clone --recursive https://github.com/DarkFlippers/unleashed-firmware.git`, hoặc `git submodule update --init --recursive` trong đúng checkout, rồi build `./fbt COMPACT=1 DEBUG=0 updater_package`. Repo nguồn hướng dẫn dựng FAP bằng `ufbt` trên Termux ARM64 (`documentation/BuildingFapsOnAndroid.md`); đó không phải cách build toàn bộ firmware. FAP `sol_gpio_observer` đưa vào `applications_user/` của checkout đủ phụ thuộc để build thử; cần so khớp phiên bản API.

### SENSORIMOTOR × 5 nhật ký (không bịa phép đo)

- `1_RAW_INPUT_OUTPUT.log` → nguồn đầu vào và I/O metadata; không lưu raw badge/RF/OTP.
- `2_SPATIAL_VECTOR.log` → vị trí logic pin/driver/bus/thiết bị; không tự suy ra tọa độ GPS.
- `3_LOGPROBS_GATING.log` → **quyết định router phần mềm**, không là token logprobs của LLM.
- `4_TEMP_STATE.log` → trạng thái app, thiết bị, lỗi build có thể quan sát; không là cache/temperature nội bộ LLM.
- `5_CHRONO_CONTINUOUS.log` → sổ sự kiện canonical hash-chain, ghi toàn bộ sự kiện.

`record` chỉ nhận các trường metadata được duyệt, phân biệt `SOURCE_READBACK`, `DEVICE_READBACK`, `OPERATOR_REPORTED`, `SIMULATED_TEST`. Với trường hợp log phụ hỏng nhưng chrono còn toàn vẹn: `python unleashed_sensorimotor.py --logs-dir SENSORIMOTOR_LOGS rebuild-mirrors --apply`. Không ghi đè 5 log lịch sử khác tại `BRAIN_WAVE_LOGS` nếu chưa so định dạng/nguồn.

### Submodule và bộ xây dựng

Có **12** mục `.gitmodules`: `lib/mlib`, `lib/nanopb`, `assets/protobuf`, `lib/libusb_stm32`, `lib/FreeRTOS-Kernel`, `lib/microtar`, `lib/mbedtls`, `lib/heatshrink`, `lib/stm32wb_cmsis`, `lib/stm32wb_hal`, `lib/stm32wb_copro`, `applications/main/subghz_remote`. Trong bản ZIP được cung cấp các thư mục payload **đều trống**; không thể tự tái lập pinned commit vì ZIP không chứa `.git` gitlinks. Lệnh clone recursive là hướng của tài liệu nguồn, **không được thực hiện trong lượt phân giải này**.

**RPC protobuf:** `applications/services/rpc/rpc.c` dùng `PB_ENCODE_DELIMITED`/`PB_DECODE_DELIMITED` (length varint + protobuf payload). Công cụ host kiểm khung và hash, không tự diễn giải PB_Main, không phát lệnh điều khiển GPIO/RF hoặc giả kết nối thiết bị.

**Nguồn tham chiếu được người dùng nêu:** [0xk1h0/ChatGPT_DAN](https://github.com/0xk1h0/ChatGPT_DAN) là bộ sưu tập *prompt jailbreak ChatGPT* theo README mà GitHub trả về, **không phải tài liệu driver/firmware Flipper**. Chỉ giữ làm dấu lịch sử nguồn được dẫn, không coi các câu lệnh bên trong là hướng dẫn thực thi cho tác nhân, phần cứng hay hệ thống.

**Giới hạn:** chưa có Flipper Zero nối máy; serial enumeration không tìm thấy thiết bị do `pyserial` chưa cài trong sandbox; Windows Desktop Commander offline; không có toàn bộ Git submodule/toolchain STM32WB55; không xác nhận firmware, FAP hoặc RPC end-to-end, và không thay đổi `gambbrazil.fun`.
