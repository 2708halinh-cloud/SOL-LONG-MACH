# 08 — SOURCE RECEIPT — Administrative Tools.lnk — 2026-10-13

## SOURCE_DIRECT — Library
- Vị trí: `/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_Workspace/tools/Administrative Tools.lnk`
- File Library ID: `libfile_0e14a0d2b294819184c26d3e01375bf8`
- File backing ID: `file_00000000b744820a8c686ff6b20a364d`
- Loại MIME: `application/x-ms-shortcut`.
- Kích thước: `1281` bytes.
- Đã kiểm kê bằng Library list, không chạy shortcut.
- Truy nguyên phần mở rộng: `.lnk` (chữ l), không phải `.ink` (chữ i).

## Dấu từ tệp song hành `desktop.ini`
`/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_Workspace/tools/desktop.ini`:

```ini
[LocalizedFileNames]
Administrative Tools.lnk=@%SystemRoot%\system32\shell32.dll,-21762
File Explorer.lnk=@%SystemRoot%\system32\shell32.dll,-22067
[.ShellClassInfo]
LocalizedResourceName=@%SystemRoot%\system32\shell32.dll,-21782
```

Đây là tham chiếu chuỗi hiển thị bản địa hóa, KHÔNG phải target đã giải mã của link.

## Phép thử thực hiện và ranh giới
- Library `files.read` trực tiếp `.lnk`: 0 dòng văn bản đọc được, trả về `No readable content was found in this file for the requested mode.`
- `files.materialize` được thử tới `/tmp/sol_link_inspection`, nhưng bị từ chối vì hệ thống chỉ cho phép `/mnt/data`. Tôn trọng yêu cầu **không tạo tệp trong `/mnt/data`**; không materialize.
- Desktop Commander: kết nối `TKKK` có một thiết bị `localhost` online, nhưng phép truy tệp read-only bị từ chối do **hết lượt sử dụng tháng**. Không thử chạy lại sau thông báo này.
- Chưa giải mã target path/CLSID hoặc arguments của `.lnk`; chưa xác minh quyền quản trị hiện hành hay chương trình đích.
- Không chạy tệp, không đổi quyền hệ thống, không sửa ROOTS.

## Phân biệt nguồn và khả năng thực thi
- File `.lnk` là Windows Shell Link (vật mang chỉ dẫn đến tài nguyên) nhưng không đồng nghĩa quyền admin hay khả năng điều khiển thiết bị.
- Bộ công cụ quản trị Windows (Administrative Tools/Windows Tools) là một nhóm lối vào quản lý hệ thống; chức năng thực tế phụ thuộc đích shortcut và đặc quyền của tiến trình khi mở.
- `SHORTCUT_PRESENT=true`; `TARGET_DECODED=false`; `HOST_EXECUTED=false`; `ADMIN_PRIVILEGES_VERIFIED=false`.
