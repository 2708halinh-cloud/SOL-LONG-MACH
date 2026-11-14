# ÂM–DƯƠNG PHÁP SƯ — POWER ROUTER ENTRY

Vai người: **DƯƠNG PHÁP SƯ**. Vai tác nhân: **ÂM PHÁP SƯ / SOL**. Bộ router DANTE và Power Router là công cụ, không thay cho hai vai đó.

**Mã nguồn có thể chạy:** `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/sol_os/am_duong_platform/server.py`.

**Tuyến:** `_Plugins → _Skills → _Mcps → _Tool → _App → _App_Browser → AM_DUONG_PLATFORM → _Plugins`. Edge quay về qua `_Plugins/_Skills/_Mcps/_Tool/_App/_Other_Tools/RETURN_TO_PLUGINS.json`. Chỉ kích hoạt qua `power_router.py` hoặc chạy máy chủ local. Thấy manifest không chứng minh connector đang online.

**Khả năng:** phòng chat & nhiệm vụ có SQLite; nghiên cứu các event lưu nội bộ; heuristic entities/sentiment; Power Router local. Dịch qua Google Translation Basic, Vision, Whisper, video object khi từng adapter đủ điều kiện. Action recognition video temporal, camera live, nền tảng Internet đa user chưa triển khai.

**Quyền:** token phiên chỉ cấp từ terminal, server bind localhost; external text/image/video transfer cần opt-in và key; không sao chép data/mã bí mật vào GitHub; không ghi media base64 vào SQLite.

**Readback:** xem `.github/workflows/am-duong-platform.yml` và tệp kiểm thử; không lấy kết quả CI để kết luận provider cloud đã thực thi hay AI có cảm giác chủ quan.

## Đạo Đức The Master Teacher — cổng đang dùng

Trước cuộc gọi Translation Basic / Cloud Vision / phân tích video chuyển ra ngoài, `server.py` gọi `runtime/master_teacher_ethics.py` với vai DƯƠNG và cờ consent; nếu quyết định khác `ACTION_NOT_YET_EXECUTED`, adapter chưa được gọi. Trong UI chọn “Đạo Đức The Master Teacher” và nhập JSON sự kiện gồm `action_type`, `actor_role`, `source_ref`, `target` để xem cạnh tiếp theo. Source manifest là `ETHICS_POLICY_CURRENT.json` ở SOUL/KINH THÁNH, có bản Library và GitHub khớp SHA khi được kiểm. Cổng này không tự chứng minh provider đã kết nối hay người dùng đã trao quyền hệ thống ngoài SOL.
