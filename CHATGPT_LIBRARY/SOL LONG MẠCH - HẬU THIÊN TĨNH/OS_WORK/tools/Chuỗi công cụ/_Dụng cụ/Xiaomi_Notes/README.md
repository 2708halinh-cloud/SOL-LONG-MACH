# @XIAOMI GHI CHÚ — tuyến tác động Redmi (SOL Tools)

- Thiết bị trực tiếp xác minh: Redmi Note 14 Pro 5G / Android 15 / Termux.
- Ứng dụng: `com.miui.notes`, receiver `com.miui.notes.ui.activity.IntermediaryActivity` hỗ trợ `android.intent.action.SEND` + `text/plain`.
- Đường gọi vật lý đã hoàn tất thành công từ Termux: `am start --user 0 -a android.intent.action.SEND -t text/plain -p com.miui.notes --es android.intent.extra.TEXT '<note body>'`.
- Người đồng hành gửi ảnh xác nhận ứng dụng nhận nội dung thử nghiệm. Ảnh chat làm bằng chứng UI riêng; không giả danh provider receipt về lưu vào database.
- Dùng `printf '%s' 'Ghi chú của SOL' | python xiaomi_notes_tool.py` trên thiết bị đã cho phép điều khiển.
- Gọi vào ứng dụng **không tự chứng minh đã lưu**. Để xác thực ghi bền vững, dùng giao diện Notes sau khi hoàn tất lưu và đọc lại nội dung.
- Không đọc cơ sở dữ liệu riêng của Xiaomi Notes, không dùng `root`, không bypass quyền; không gửi dữ liệu nhạy cảm qua phần `--text` dòng lệnh (ưu tiên stdin).
- Vật mang: ChatGPT Library ↔ GitHub `OS_WORK/tools/Chuỗi công cụ/_Dụng cụ/Xiaomi_Notes`.
- Phân loại: `TOOLS / ANDROID_APP_INTENT` (không nhầm với HTTP API hay plugin ChatGPT đã cài).
