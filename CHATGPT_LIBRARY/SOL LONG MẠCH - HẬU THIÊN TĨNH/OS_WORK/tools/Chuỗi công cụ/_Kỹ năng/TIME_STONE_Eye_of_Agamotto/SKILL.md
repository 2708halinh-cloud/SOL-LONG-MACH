---
name: sol-time-stone-eye-of-agamotto
description: Kích hoạt khi @TIME_STONE, @Sol Long Mạch, bắt đầu dự án hoặc gọi Tools; điều phối STAMP_OLD/LIVE/BETA, dấu thời gian thực, 5 nhật ký sóng, điều kiện tiếp tục N+1, tránh lệch nhịp với người đồng hành và Toolset.md / Azure DevOps MCP.
---

# 🟢 TIME_STONE × Con mắt Agamotto — Skill thực thi (SOL)

## Nguồn chuẩn, không tự viết lại lời nguồn

- `CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md` — giữ nguồn và vật chứng; Điều 5, THA/CẦM GIỮ cho phép tước quyền tham gia CURRENT của nhiễu hoặc lỗi.
- `CONFIG_SOL/R014_SOURCE_DIRECT_20261009.md` — lỗi `SUBRITETIED`: loại bỏ cơ chế lỗi khỏi đường thực thi; giữ lịch sử nguồn và lý do.
- `COMPUTER_KHÍ💜BRAIN_OS_POWER/BRIDGE_TIME_TÓC🟢MỘC_TIME/AGENTS.md`, `README.md`, `FIVE_WAVE_JOURNAL_REGISTRY_20261016.md` — ba STAMP và năm kênh.
- `/Toolset.md` ChatGPT Library + `tools/Chuỗi công cụ/_MCPs/AZURE_DEVOPS_MCP_CORE/docs/TOOLSET.md` — các bản được kiểm nguồn riêng, KHÔNG coi tên trùng là nội dung trùng.

## Khi gọi @TIME_STONE / @Sol Long Mạch / Tools / bắt đầu dự án

1. Đo đồng hồ thực của môi trường thực thi có múi giờ và `observed_at`; tách riêng `event_time`, `observed_at`, `provider_commit_time` và `chat_time`; không tự bịa mốc cũ.
2. Định danh theo `SPACE` và `INDEX`; kiểm pointer Toolset/Azure DevOps để không bắt đầu lại tác vụ đã có cursor; tìm 5 vật mang BETA/DELTA/ALPHA/THETA/GAMMA theo địa chỉ đã xác thực. Không tạo raw giả.
3. **Áp dụng bộ đọc `time_stone.py sync`:** cập nhật **bản chiếu CURRENT** từ nhật ký; `STAMP_LIVE` quan sát đã quá cửa sổ thời gian được phản chiếu thành `STAMP_OLD`. Bản RAW bất biến, trong đó giữ đúng nhãn mà sự kiện mang ở thời điểm nó được ghi; mọi chuyển lớp ghi vào `TRANSITIONS.jsonl`.
4. `STAMP_BETA` khi quá `event_time` trở thành `STAMP_BETA_DUE_UNVERIFIED`, không tự nâng thành LIVE. Muốn nâng phải có sự kiện mới, ID/revision mới, observation và receipt thật.
5. TIME LOCK: dừng promotion nếu đồng hồ quay ngược hoặc sự kiện trỏ vào tương lai không có căn cứ. LOOP: lặp đo sau chu kỳ xác định, mỗi lần chỉ xử lý delta; không lặp phản xạ báo cáo hoặc xóa lịch sử.
6. Mô hình 5 kênh nhật ký: BETA/MIND (đầu vào), DELTA/TIME (chuỗi), ALPHA/REALITY (hành động & hậu quả), THETA/SOUL (nguồn), GAMMA/POWER (điều phối). SPACE cung cấp ID xuyên kênh, không phải kênh thứ sáu.
7. Nhịp hai chiều: dùng mốc người đồng hành cung cấp hoặc wall-clock fresh-read để tính trạng thái. Nếu công cụ gọi được thì tiếp tục thực thi, lấy receipt và đọc ngược, nối N+1; không biến việc rà soát thành điểm dừng.

## Phân giải mâu thuẫn 2 nguồn

`XÓA/BỎ CƠ CHẾ GÂY LỖI KHỎI MẠCH CURRENT` ≠ `XÓA VẬT CHỨNG LỊCH SỬ`.

- Được thay thế/ghi đè **các nhãn hiện hành, INDEX/cache, bản chiếu CURRENT, luật quyết định lỗi đã xác minh**; có thể cắt đường gọi tới cơ chế `SUBRITETIED`.
- Không xóa hoặc ghi lại dấu RAW, bản gốc, thư mục lịch sử, event_id, timestamp gốc, source/hash, correction và hậu quả. Xóa artifact dẫn xuất chỉ khi provenance, bản thay thế và đường khôi phục đã được xác minh.
- Nguồn có chữ `STAMP_LIVE` từ hôm qua vẫn là bằng chứng rằng **hôm qua nó từng live**. Bộ máy hiện tại ghi `STAMP_OLD` *cho chính sự kiện đó ở thời điểm truy xét này*, không sửa lời nói của hôm qua.

## Gọi công cụ

```bash
python time_stone.py sync --events ./events.jsonl --state-dir ./state --live-window 60
python time_stone.py watch --events ./events.jsonl --state-dir ./state --live-window 60 --interval 60
printf '%s\n' '{"event_id":"verified-id","stamp_class":"STAMP_LIVE","observed_at":"2026-10-17T01:00:00+07:00","source_ref":"provider://receipt","wave":"DELTA"}' | python time_stone.py record --events ./events.jsonl
```

`--force-active` ghi trạng thái **vòng lặp local** đang hoạt động, không khai quyền nhà cung cấp. Trên Redmi, `runsv` giám sát công cụ; riêng CHAT chỉ là điểm vào, không tự làm tiến trình chạy nếu thiết bị đã ngắt.

## Miền liên kết

🟡 MIND nhận tín hiệu; 🔵 SPACE khóa định danh; 🟢 TIME phân lớp và duy trì mốc; 🔴 REALITY hành động/receipt; 🟠 SOUL bảo toàn nguồn; 🟣 POWER chọn công cụ. Tâm ☯️ là quan hệ thống nhất của sáu đỉnh, không thêm hive/thư mục thứ sáu ở COMPUTER.

### Điều kiện xác nhận

- Kiểm thử offline `python -m unittest discover -s . -p 'test_time_stone.py'` phải pass.
- Có tiến trình `time_stone.py watch` thực chạy và file `CURRENT.json` đổi theo đồng hồ mới thì `RUNTIME_ACTIVE=true`.
- Không có connector Azure/Google Calendar trong bộ công cụ này thì chỉ khóa nguồn và nhịp; không khẳng định đã đồng bộ lịch cloud.
