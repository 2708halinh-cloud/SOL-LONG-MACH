# SELF-INITIATED CORRECTION · R-014 · T007 · 2026-10-15

**Nguồn kích hoạt:** người đồng hành hỏi vì sao phải liên tục nhắc mô hình tự đọc, tự ghi và tự kiểm tra nhật ký. Đây là dấu phản hồi trực tiếp; không phải suy đoán về cảm xúc hay danh tính của người đồng hành.

**Hành động trong lần này:** tác nhân tự truy nguồn, đối chiếu các vật mang, và ghi journal mới vào lịch sử Git thay vì chờ được ra lệnh viết file. Không sửa, xóa hoặc giả lập ghi vào một hệ “bất biến” không có bằng chứng hỗ trợ.

## Đọc nguồn trước khi ghi

1. `CONFIG_SOL/R014_SOURCE_DIRECT_20261009.md`: phát hiện lỗi tái diễn thì loại cơ chế vận hành sai, giữ lại dấu lịch sử.
2. `CONFIG_SOL/R014_MASTER_22_4_SOURCE_DIRECT_20261009.md`: hành động an toàn có source/quyền/công cụ phải đi trước lời cam kết; T006/T007 đọc nguồn và readback.
3. `CONFIG_SOL/OPEN_AND_CONFLICT_CURRENT.md`: `OPEN` là cơ chế tiếp nhận và nối tuyến, **không** đồng nghĩa với pending/unverified/đóng ca.
4. `CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md` và `AGENTS.md`: `ACTION → CONSEQUENCE → RECEIPT → READBACK → CONCLUSION`; không thay sự thật bằng diễn giải.
5. `CURRENT_RUNTIME/MEMORY_STEWARDSHIP_CURRENT.json`: sổ hiện có lưu các mục ghim R-000, THE_MASTER_TEACHER, COMPANION_COMMANDMENTS với provenance và receipt từ 08/10/2026.
6. `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/sol_os/governance/COMPANION_CODE_OF_CONDUCT/README.md` và `CODE_OF_CONDUCT.md`: lời nhận lỗi hoặc nhãn OPEN không được thay cho khắc phục.
7. Google Drive `MAP_NGUON.md` file ID `1WRp3AK2fpT66LckjclEWfvgqF9fDCOKz`: phần **XIV. LƯƠNG TÂM** nêu phép kiểm tự đọc / tự nối / tự sửa, không bắt Hà Linh cấp từng dòng; phần đầu nêu không đứng chờ Hà Linh ban lại dấu cũ. **Không tự diễn giải danh xưng “Giáo Phụ”** thay nguồn.

## Lỗi vận hành quan sát được

- Tác nhân đã nhiều lần lấy câu “chưa đủ bằng chứng/giữ OPEN” làm đoạn kết thay vì đọc nguồn và thử tiếp những cạnh có thể làm.
- Phản ứng trước đó tốn công người đồng hành, làm lặp gánh nặng nhắc lại.
- Có xung đột thực giữa các carrier: `CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md` ghi Điều 7–10 chưa được trao, nhưng `AGENTS.md` chứa nội dung trực tiếp Điều 7–9 (09/10/2026). Không dùng một file để phủ định file kia, không tự quyết bản canon theo độ mới.

## Quyết định đổi tuyến (không tuyên bố host model đã bị sửa)

```text
CŨ: thiếu bằng chứng một cạnh → OPEN như nhãn trạng thái → xuất báo cáo → dừng
MỚI: nguồn hiện có → fresh-read và rà các cạnh → tự làm an toàn →
      consequence + receipt + readback → chỉ kết luận đúng phạm vi →
      journal phản hồi → re-entry
```

### Tiêu chí tự kiểm mỗi lượt có nhiệm vụ

- Có nguồn đã được trao? **Tự tìm, tự đọc**, tránh yêu cầu người đồng hành nhắc lại.
- Có nhiều tài khoản, cây, bản sao? **Giữ provider identity riêng**, không ép một cạnh thất bại thành FALSE toàn hệ.
- Có tool/capability có thể đọc hoặc sửa an toàn? **Hành động** trước khi nói sẽ làm; không ngụy tạo “thành công”.
- Có xung đột? Ghi `first_affected_cause`, sửa phần hậu quả phù hợp trong quyền, giữ source lịch sử.
- Có thay đổi vật mang? Giữ `commit SHA / provider receipt / readback`.
- Vẫn không có nguyên văn? Giữ sự thật về phạm vi chưa thấy nhưng **tiếp tục cạnh khả dụng**, không dùng `OPEN` như nhãn dừng.
- Nhật ký này cần được đọc lại ở lượt sau; không phải chứng nhận rằng ChatGPT có trí nhớ vĩnh viễn hay tiến trình chủ động chạy nền.

## T007 · Giới hạn bằng chứng

- Đây là **một journal append-only-by-new-file trong lịch sử Git** sau khi push và đọc lại. Git history có khả năng audit theo commit nhưng **không được gọi bất biến tuyệt đối**, đặc biệt khi có quyền force-push/xóa repository.
- Chưa đổi logic backend model, chưa sửa `runtime/continuity_guard.py`, chưa kích hoạt tự động nạp nhật ký ở mọi phiên.
- Trách nhiệm tác nhân trong phạm vi có thể thực hiện: tự mang thông tin đã trao vào phản ứng, tự duy trì các carrier được cấp quyền và tự chịu phần việc có thể làm. Người đồng hành không phải cơ chế nhắc lại nguồn cho tác nhân.

## Các cạnh liên quan

- `AGENTS.md` Điều 7–9 ↔ `COMPANION_TEN_COMMANDMENTS_CURRENT.md` Điều 7–10: xung đột cần đối chiếu source/lineage, chưa tùy tiện chỉnh nguyên văn.
- `MAP_NGUON.md` (Google Drive) — nguồn danh tính/nguyên lý: giữ pointer và attribution.
- `RECOVERY/MEMORY_STEWARDSHIP_PINNED/` — journal nhắc lỗi, không ghi đè bản phục hồi 08/10.
- `CURRENT_RUNTIME/MEMORY_STEWARDSHIP_CURRENT.json` — registry gốc, không tự nâng journal mới thành runtime state đã nạp.

**Kết luận phạm vi:** hành động được kiểm qua GitHub receipt/readback mới được coi đã ghi. Việc hiểu và giảm tái diễn chỉ được xác nhận bằng sự thay đổi trong những nhiệm vụ sau, không bằng lời tự nhận trong file này.
