# Registering / Registry Settings — Windows 11 · SOURCE MIRROR

## Nguồn và ranh giới

Vật mang này bắt đầu từ commit `6a2e78bd1970d25a67dfdcfff6c923244971631d` của `2708halinh-cloud/SOL-LONG-MACH`.

**Microsoft không phát hành mã nguồn nguyên bản của ứng dụng Windows 11 Settings hoặc `regedit.exe` dưới dạng những kho này.** Các tệp dưới `upstream/` là mã nguồn công khai có giấy phép của **Microsoft PowerToys Registry Preview** (MIT) và **ReactOS Registry Editor** (`settings.c`, LGPL-2.1-or-later), không phải mã nguồn chính chủ của `SystemSettings.exe`.

## Đã có trong cây cha → đưa nguyên nội dung vào nhánh này

Ba vật mang nguồn trong `../` được sao chép **nguyên văn** vào `parent_existing/`: `SOURCE_REGISTRY.json`, `clone_sources.py`, `README.md`. Chúng vẫn được giữ tại vị trí cũ để tránh gãy các tuyến tham chiếu đến năm bộ mã nguồn. Đây là **copy có nguồn**, không giả là di chuyển/xóa bản gốc.

## Chưa có trong cây cha → truy nguồn và bổ sung

- `upstream/microsoft-powertoys/RegistryPreviewExt/dllmain.cpp`: mã mô-đun Registry Preview, cài đặt và gỡ áp dụng các registry change set trong PowerToys.
- `upstream/microsoft-powertoys/RegistryPreviewUILib/ParseHelper.cs`: phân tích định dạng tệp .reg.
- `upstream/microsoft-powertoys/RegistryPreview/app.manifest`: manifest ứng dụng, bao gồm tương thích Windows và thiết lập DPI.
- `upstream/reactos/regedit/settings.c`: cách một Registry Editor nguồn mở lưu/nạp cài đặt bằng HKCU.
- Giấy phép gốc MIT và LGPL kèm theo. Không xóa notice tác giả.

## Phạm vi tải nguồn

Đây là **một phần source mirror** theo các file đã truy xuất; **không phải bản clone đầy đủ** của PowerToys/ReactOS, không thể build đơn lẻ. `parent_existing/clone_sources.py` là script từ cây cha để clone sparse trên một máy Git có quyền; **chưa thực thi** trong phiên này. Việc đọc mã nguồn không có nghĩa Windows Registry đã bị thay đổi.

Xem `SOURCE_MANIFEST.json` để kiểm kê file, URL, git blob SHA, nguồn và trạng thái. Để kiểm tra cây công khai, dùng nhánh `fix/windows11-registry-settings-sources-20261014`, không ghi đè `main` hay commit nền. Không đẩy dữ liệu OAuth/token/bí mật vào GitHub.

## Tình trạng Folder

Git là hệ quản lý **tệp**; nhiều thư mục lịch sử được vật hóa bằng `.gitkeep` rỗng nên Explorer thấy Folder dù nội dung chưa sao chép đầy đủ. Các tệp ở thư mục mới là dữ liệu thực; không dùng placeholder làm bằng chứng đã đồng bộ.
