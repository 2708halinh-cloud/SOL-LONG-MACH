# 02 — ZIP SOURCE_DIRECT

**Không cần khoanh vùng vòng vo**: `.zip` là gợi ý định dạng và chữ ký byte/`zipfile.is_zipfile()` xác nhận tệp ZIP thực. Đừng suy `ngày tạo` từ tên `20260708_091517`.

```powershell
python zip_source_inspector.py "D:\\path\\WINDOWS_LICENSE_B560_20260708_091517.zip" --max-total-mib 256
```

Mặc định: nhận diện → kích thước → SHA-256 archive → kiểm CRC/hash các thành viên → giải nén sang **thư mục MỚI** khi an toàn và vừa dung lượng → JSON report. Không thực thi bất kỳ file nào, không ghi đè, không xóa. Báo cáo: `SOURCE_DIRECT_ZIP_REPORT.json` với tên, kích thước, SHA, dấu hiệu định dạng, zip timestamps, đoạn xem trước văn bản đã che thông tin xác thực, thống kê.

Bỏ giải nén: `--no-extract`. Điều chỉnh trần bằng `--max-total-mib 1024` sau khi kiểm dung lượng vật mang. Mặc định 256 MiB uncompressed, tối đa 2.000 thành viên, mỗi file tối đa 100 MiB, ratio ≤1000. Nếu vượt giới hạn: ghi vấn đề, **không** tự vượt; chuyển qua runtime/tools có tài nguyên phù hợp.

`filesystem_created_at` chỉ ghi khi OS cung cấp `stat.st_birthtime`; nếu không là `null`. Thời gian nằm trong ZIP không phải thời điểm tạo tệp trên NTFS. `filename` không chứng minh thời gian hay chủ sở hữu.

**Đầu vào chính xác** `WINDOWS_LICENSE_B560_20260708_091517.zip` hiện chưa có byte được xác nhận trong phiên. Mọi báo cáo thử nghiệm phải dùng tên TEST, không nhận là file gốc.
