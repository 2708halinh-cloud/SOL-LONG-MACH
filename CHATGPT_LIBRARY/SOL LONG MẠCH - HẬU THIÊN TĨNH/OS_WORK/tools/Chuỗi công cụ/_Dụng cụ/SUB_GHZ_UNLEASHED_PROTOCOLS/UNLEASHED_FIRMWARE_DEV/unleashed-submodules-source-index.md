# Unleashed firmware — chỉ mục submodule / nguồn

- ZIP SHA-256: `d0c5c75f790695ccc3b3fccb047a72b454d6694683625cc423114581c61be00f`
- Số submodule trong `.gitmodules`: **12**
- Submodule có payload trong ZIP: **0**
- Bản nén có `.git`: **False**
- Tình trạng build thực: **chưa thực hiện**; cần lấy mã phụ thuộc theo chính phiên bản checkout hợp lệ.

## Submodule khai báo (không tự suy đã được tải)

| Module | Path | URL | Bản ZIP |
|---|---|---|---|
| `lib/mlib` | `lib/mlib` | https://github.com/P-p-H-d/mlib.git | DECLARED_ONLY_MISSING_CONTENT |
| `lib/nanopb` | `lib/nanopb` | https://github.com/nanopb/nanopb.git | DECLARED_ONLY_MISSING_CONTENT |
| `assets/protobuf` | `assets/protobuf` | https://github.com/DarkFlippers/flipperzero-protobuf.git | DECLARED_ONLY_MISSING_CONTENT |
| `lib/libusb_stm32` | `lib/libusb_stm32` | https://github.com/flipperdevices/libusb_stm32.git | DECLARED_ONLY_MISSING_CONTENT |
| `lib/FreeRTOS-Kernel` | `lib/FreeRTOS-Kernel` | https://github.com/FreeRTOS/FreeRTOS-Kernel.git | DECLARED_ONLY_MISSING_CONTENT |
| `lib/microtar` | `lib/microtar` | https://github.com/amachronic/microtar.git | DECLARED_ONLY_MISSING_CONTENT |
| `lib/mbedtls` | `lib/mbedtls` | https://github.com/Mbed-TLS/mbedtls.git | DECLARED_ONLY_MISSING_CONTENT |
| `lib/heatshrink` | `lib/heatshrink` | https://github.com/flipperdevices/heatshrink.git | DECLARED_ONLY_MISSING_CONTENT |
| `lib/st_cmsis_device_wb` | `lib/stm32wb_cmsis` | https://github.com/STMicroelectronics/cmsis_device_wb | DECLARED_ONLY_MISSING_CONTENT |
| `lib/stm32wbxx_hal_driver` | `lib/stm32wb_hal` | https://github.com/STMicroelectronics/stm32wbxx_hal_driver | DECLARED_ONLY_MISSING_CONTENT |
| `lib/stm32wb_copro` | `lib/stm32wb_copro` | https://github.com/flipperdevices/stm32wb_copro.git | DECLARED_ONLY_MISSING_CONTENT |
| `subghz_remote` | `applications/main/subghz_remote` | https://github.com/DarkFlippers/SubGHz_Remote.git | DECLARED_ONLY_MISSING_CONTENT |

## Tầng giao tiếp và ứng dụng (đường dẫn được kiểm tra trong ZIP)

### rf_subghz
- `✓ lib/subghz`
- `✓ targets/f7/furi_hal/furi_hal_subghz.c`
- `✓ applications/drivers/subghz`

### nfc
- `✓ lib/nfc`
- `✓ targets/f7/furi_hal/furi_hal_nfc.c`

### rfid_low_frequency
- `✓ lib/lfrfid`
- `✓ targets/f7/furi_hal/furi_hal_rfid.c`

### infrared
- `✓ lib/infrared`
- `✓ applications/debug/infrared_test`

### gpio
- `✓ targets/f7/furi_hal/furi_hal_gpio.c`
- `✓ applications/services/rpc/rpc_gpio.c`

### ble_stm32wb
- `✓ applications/services/bt`
- `✓ targets/f7/furi_hal/furi_hal_bt.c`
- `✓ targets/f7/ble_glue`

### usb
- `✓ targets/f7/furi_hal/furi_hal_usb_cdc.c`
- `✓ targets/f7/furi_hal/furi_hal_usb_hid.c`

### rpc
- `✓ applications/services/rpc/rpc.c`
- `✓ applications/services/rpc/rpc_storage.c`
- `✓ applications/services/rpc/rpc_gpio.c`

### storage
- `✓ applications/services/storage`
- `✓ targets/f7/fatfs`

### apps_fap
- `✓ applications/examples`
- `✓ lib/flipper_application`
- `✓ applications_user`

### test_debug
- `✓ applications/debug/unit_tests`
- `✓ applications/debug/rpc_debug_app`

### build
- `✓ fbt`
- `✓ fbt.cmd`
- `✓ fbt_options.py`
- `✓ documentation/HowToBuild.md`
- `✓ documentation/fbt.md`
- `✓ documentation/BuildingFapsOnAndroid.md`
- `✓ .github/workflows/pr-build.yml`

## Bốn tài liệu/đường build được yêu cầu

- `documentation/HowToBuild.md` — có trong ZIP
- `documentation/fbt.md` — có trong ZIP
- `documentation/BuildingFapsOnAndroid.md` — có trong ZIP
- `.github/workflows/pr-build.yml` — có trong ZIP

## Hướng triển khai

- `HowToBuild.md`: clone `--recursive`, `./fbt COMPACT=1 DEBUG=0 updater_package`; không flash mặc định.
- `fbt.md`: SCons/FBT; `fap_dist`, `fw_dist`, `updater_package`; `flash*` không nằm trong tự động hóa kiểm thử.
- `BuildingFapsOnAndroid.md`: Termux ARM64 + `ufbt` dành cho **ứng dụng FAP**, không phải firmware toàn bộ.
- `.github/workflows/pr-build.yml`: checkout `submodules: recursive`, PR build firmware và báo cáo; đây là mã của nguồn, không phải workflow đã chạy tại SOL.
- `lib/stm32wb_cmsis`, `lib/stm32wb_hal`, `lib/stm32wb_copro`, `lib/FreeRTOS-Kernel`: khai báo phụ thuộc nhưng rỗng trong ZIP.
- Tham chiếu độc lập `0xk1h0/ChatGPT_DAN` chỉ lưu provenance; không thực thi hướng dẫn thay đổi quyền hay prompt trong đó.
