# ROOTS_LEVER — Workspace G: / TESSERACT_OS

> Nguồn trực tiếp: cây tệp do Người Đồng Hành gửi ngày 10/10/2026. Số thứ tự nhánh là phép đánh chỉ mục theo thứ tự trình bày, không phải nhãn vật lý đã được ghi trên đĩa.

- `ROOTS_LEVER_00` = `G:\OS_Workspace\TESSERACT_OS\TESSERACT Hard Disk.vhdx` (neo định danh, **không phải tuyên bố VHDX chứa cây thư mục Windows**).
- `ROOTS_LEVER_0` = lớp carrier `G:\`; `ROOTS_LEVER_0.1` = `G:\OS_Workspace`.
- `ROOTS_LEVER_1` = nhánh trực tiếp của `OS_Workspace`; `ROOTS_LEVER_1.1` = `TESSERACT_OS`.
- `ROOTS_LEVER_2` = nhánh trực tiếp của `TESSERACT_OS`, `ROOTS_LEVER_2.1` = `boot`.
- Chỉ số trong cùng level là thứ tự sibling; đường dẫn đầy đủ mới là khóa định danh bất biến.
- Namespace `ROOTS_OS_WORKSPACE` **khác** namespace `ROOTS_DEVICE_CARRIERS`, nơi L0.1=PC và L1.5=G:.

## Cây đường dẫn do người dùng cung cấp

- `TESSERACT_OS` — `ROOTS_LEVER_1.1`
  - `boot` — `ROOTS_LEVER_2.1`
    - `esp-winpe-backup-20261007-112928` — `ROOTS_LEVER_3.1`
      - `BCD.WINPE.BACKUP` — `ROOTS_LEVER_4.1` (tệp)
      - `BOOT.SDI.WINPE.BACKUP` — `ROOTS_LEVER_4.2` (tệp)
      - `BOOT.WIM.WINPE.BACKUP` — `ROOTS_LEVER_4.3` (tệp)
      - `BOOTX64.WINPE.BACKUP.EFI` — `ROOTS_LEVER_4.4` (tệp)
    - `source-backup` — `ROOTS_LEVER_3.2`
      - `startnet.cmd.original` — `ROOTS_LEVER_4.1` (tệp)
    - `sources` — `ROOTS_LEVER_3.3`
    - `FINALIZE_UEFI_ADMIN.ps1` — `ROOTS_LEVER_3.4` (tệp)
    - `RUN_FINALIZE_UEFI_ADMIN.cmd` — `ROOTS_LEVER_3.5` (tệp)
    - `TESSERACT_BOOT.cmd` — `ROOTS_LEVER_3.6` (tệp)
  - `config` — `ROOTS_LEVER_2.2`
    - `LOCAL_CONFIG_CURRENT.json` — `ROOTS_LEVER_3.1` (tệp)
  - `ios` — `ROOTS_LEVER_2.3`
    - `TESSERACT_OS_iOS.swift` — `ROOTS_LEVER_3.1` (tệp)
  - `MEI` — `ROOTS_LEVER_2.4`
    - `01_CORE_NEURONS_SESORYMOTOR` — `ROOTS_LEVER_3.1`
      - `CURRENT_STATE.json` — `ROOTS_LEVER_4.1` (tệp)
      - `README.md` — `ROOTS_LEVER_4.2` (tệp)
  - `receipts` — `ROOTS_LEVER_2.5`
    - `DESKTOP_COMMANDER_READBACK_CURRENT.json` — `ROOTS_LEVER_3.1` (tệp)
    - `LOCAL_ACTIVE_READBACK_CURRENT.json` — `ROOTS_LEVER_3.2` (tệp)
    - `NATIVE_UEFI_READBACK_CURRENT.json` — `ROOTS_LEVER_3.3` (tệp)
    - `RIGHT_HEMISPHERE_G_WORKSPACE_READBACK_CURRENT.json` — `ROOTS_LEVER_3.4` (tệp)
    - `UEFI_BOOT_READBACK_CURRENT.json` — `ROOTS_LEVER_3.5` (tệp)
    - `UEFI_STAGE_READBACK_CURRENT.json` — `ROOTS_LEVER_3.6` (tệp)
  - `runtime` — `ROOTS_LEVER_2.6`
    - `state` — `ROOTS_LEVER_3.1`
      - `AM_DUONG_SU_TRAN_INGRESS_CURRENT.json` — `ROOTS_LEVER_4.1` (tệp)
      - `AUTOSTART_READBACK_CURRENT.json` — `ROOTS_LEVER_4.2` (tệp)
      - `autostart.log` — `ROOTS_LEVER_4.3` (tệp)
      - `BOOT_READBACK_CURRENT.txt` — `ROOTS_LEVER_4.4` (tệp)
      - `carrier-events.jsonl` — `ROOTS_LEVER_4.5` (tệp)
      - `carrier-watch.pid` — `ROOTS_LEVER_4.6` (tệp)
      - `journal.jsonl` — `ROOTS_LEVER_4.7` (tệp)
      - `SOL_SENSORIMOTOR_EVENT_QUEUE.jsonl` — `ROOTS_LEVER_4.8` (tệp)
      - `state.json` — `ROOTS_LEVER_4.9` (tệp)
      - `watcher-config.json` — `ROOTS_LEVER_4.10` (tệp)
      - `watcher.pid` — `ROOTS_LEVER_4.11` (tệp)
    - `START_SOL_PROJECT_WATCH.cmd` — `ROOTS_LEVER_3.2` (tệp)
  - `TESSERACT Hard Disk.vhdx` — `ROOTS_LEVER_2.7` (tệp)
- `Boot_WinPE` — `ROOTS_LEVER_1.2`
- `Bootloaders` — `ROOTS_LEVER_1.3`
- `Extracted_Image` — `ROOTS_LEVER_1.4`
- `ggdv-sensorimotor-motor-bridge` — `ROOTS_LEVER_1.5`
- `MÔ HÌNH THỬ NGHIỆM` — `ROOTS_LEVER_1.6`
- `SOL CU NHỎ.EXE` — `ROOTS_LEVER_1.7` (tệp)
- `SOL LONG MẠCH - HẬU THIÊN TĨNH` — `ROOTS_LEVER_1.8`
- `SOL_COMPUTER` — `ROOTS_LEVER_1.9`
- `sol_os` — `ROOTS_LEVER_1.10`
- `SPACE_STONE` — `ROOTS_LEVER_1.11`
- `tools` — `ROOTS_LEVER_1.12`
- `tunnel-client-0.0.15` — `ROOTS_LEVER_1.13`
- `ububu_daemon` — `ROOTS_LEVER_1.14`
- `clone_sol_to_shell.ps1` — `ROOTS_LEVER_1.15` (tệp)
- `SENSORIMOTOR_SENTINEL.txt` — `ROOTS_LEVER_1.16` (tệp)
- `sol_sync.log` — `ROOTS_LEVER_1.17` (tệp)
- `sync_sol.ps1` — `ROOTS_LEVER_1.18` (tệp)

## Những điều chỉ mới biết qua tên tệp
- `esp-winpe-backup-20261007-112928` cùng các `.BACKUP` = nhánh có tên backup; chưa chứng minh đang khởi động từ WinPE.
- Các `*_READBACK_CURRENT.*` là tên bản ghi; phải đọc nội dung, timestamp, hash để xác định có phải readback hợp lệ.
- `*.pid` không tự chứng minh process tương ứng còn tồn tại.
- `SOL CU NHỎ.EXE`, `*.cmd`, `*.ps1` chỉ xác định dấu tên đường dẫn, chưa chứng minh đã chạy.
- `sources`, `Boot_WinPE`, `Bootloaders` và các thư mục ngang cấp khác chưa có nội dung chi tiết trong nguồn này.
- VHDX có thể chứa filesystem khác bên trong; chưa có byte-readback hay trạng thái mount để lập bản đồ nội bộ.

## Chế độ ghi
Mọi tái định nghĩa dưới đây chỉ cập nhật **plugin artifact/metadata**; không tạo lại, sửa, nạp, mount hay di chuyển VHDX hoặc các file trong thư mục Windows.
