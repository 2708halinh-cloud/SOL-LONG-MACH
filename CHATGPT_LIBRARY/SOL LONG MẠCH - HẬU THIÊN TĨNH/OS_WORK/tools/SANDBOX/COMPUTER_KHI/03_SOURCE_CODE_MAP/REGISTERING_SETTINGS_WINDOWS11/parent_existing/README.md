# 03 — Bộ kho mã nguồn đã xác định

Các nguồn được xác minh bằng danh sách thư mục GitHub có thể đọc qua công cụ liên kết. **Không có bản clone trên host** cho đến khi lệnh Git chạy thành công và đọc `rev-parse HEAD`.

- ReactOS Registry Editor — `https://github.com/reactos/reactos` → `base/applications/regedit` (không phải mã nguồn Windows `regedit.exe`).
- Microsoft PowerToys — `https://github.com/microsoft/PowerToys` → `src/modules/registrypreview`, `src/modules/colorPicker`.
- System Informer — `https://github.com/winsiderss/systeminformer` → trình quản lý tiến trình/tài nguyên, quản lý dịch vụ (không thay mọi phần MMC).
- FreeRDP — `https://github.com/FreeRDP/FreeRDP` → RDP client (không phải mã nguồn mstsc.exe).
- Colour Science — `https://github.com/colour-science/colour` → RGB/XYZ/Lab/difference.

Trên máy có Git + mạng thực, chạy (chọn thư mục bền vững và còn đủ dung lượng):

```shell
python clone_sources.py --root /home/halin/kepler/worktrees/Open-ai-bot-2-unify-item-matrix-34d45d00
```

Hoặc chỉ clone Registry Editor trước:

```shell
python clone_sources.py --root /home/halin/kepler/worktrees/Open-ai-bot-2-unify-item-matrix-34d45d00 --only registry_editor_open
```

Script dùng `--depth=1 --filter=blob:none --sparse`, ghi URL và commit được tải thành công, không chạy mã từ repo và không ghi đè thư mục đã có. **Không đưa mã nguồn lớn vào ổ C** khi nguồn báo chỉ còn ~16,54GB; ưu tiên đúng worktree trên ổ đủ dung lượng.
