# 🟣 POWER STONE — Power Router

Điểm vào: `Chuỗi công cụ/_Plugins`. Sau đó lựa chọn `_Kỹ năng` → `_MCPs` → `_Dụng cụ` → `_Ứng dụng` → `_App_Browser`; quay lại `_Plugins` để kết thúc một vòng định tuyến.

Nguồn registry: `Chuỗi công cụ/_Sổ_đăng_ký/toolchain-snapshot.json` (451 Skill, 523 hàm MCP, ảnh chụp 2026-10-16). Danh sách là bằng chứng hiện diện, **không** tự kích hoạt dịch vụ.

## Quyền và đường đọc ít ma sát

1. Kiểm tra đường công cụ đã cấp quyền trước. Một plugin có `Allow all actions` vẫn có thể gặp bước **phê duyệt vật hóa tệp** của lớp tệp đính kèm; hai quyền này không đồng nhất.
2. Nếu nhiệm vụ chỉ cần văn bản GitHub: ưu tiên `GitHub.fetch_file`/đường đọc trả `content` trực tiếp, đối chiếu SHA; không gọi đường trả về tệp đính kèm để buộc người đồng hành phê duyệt vật hóa.
3. Nếu cần ghi ChatGPT Library: dùng `files.manage_library` với tệp nguồn đã có trong sandbox và đường đích chính xác; đọc lại bằng `files.list`/`files.read`. Không dùng lại một thao tác bị chặn khi có tuyến khác đang callable.
4. Khi quyền phê duyệt thật sự không thể thay thế: nói chính xác một hành động người đồng hành cần làm, lý do, phạm vi. Không tự nhận đã duyệt, không tự mở rộng quyền.
5. Tác vụ giao cho tác nhân không dừng tại receipt trung gian. Đối soát cả GitHub và Library trước khi kết luận, giữ `NEXT_AGENT` cho phần tự làm.

Work Cloud Browser cần Work mode và không tự bật qua router tài liệu. Điểm quay: `_Plugins`.
