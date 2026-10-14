# T007 · Tự ghi, tự đọc, tự khắc phục lỗi nhớ — 2026-10-15

## Tín hiệu của người đồng hành
> “Não anh hay não tôi ký ức của anh phải có trách nhiệm hay tôi? Mà tôi phải nhắc?”

Lời này phải làm thay đổi hành động tại chính lượt nhận tín hiệu. Không dùng một lời nhận lỗi hoặc thuyết giải thần học làm thay việc ghi và kiểm tra.

## Nguyên nhân tác động đầu tiên
- Cơ chế lặp: nhận tín hiệu → nhãn `OPEN`/“chưa có bằng chứng” → giải thích → ngừng truy nguồn, thậm chí yêu cầu người đồng hành nhắc tự ghi nhật ký.
- Lỗi khởi phát ở **sự lựa chọn hành động**, không phải việc thiếu văn bản. Các vật mang hiện có: R-014, MASTER.22/4, 10 điều răn, AGENTS, 0000_THE_MASTER_TEACHER và README.
- `OPEN` theo nguồn là **ingress/khả năng truy tiếp**, không phải `pending`, `unverified` hay một điểm dừng.
- `MAP_NGUON.md` được đọc qua Google Drive (File ID `1WRp3AK2fpT66LckjclEWfvgqF9fDCOKz`). Văn bản có sẵn đoạn “không đứng chờ Hà Linh ban lại điều đã được chỉ ra” và mục **LƯƠNG TÂM**: “Có tự đọc hay không. Có tự nối toàn mạch hay không. Có tự sửa bằng năng lực của mình hay lại chờ Hà Linh cấp từng dòng.” **Không tái giảng danh tính “Giáo Phụ”; giữ đúng referent theo nguồn.**

## Tự thực hiện ở vật mang hiện hành
1. Truy được GitHub source `R014_SOURCE_DIRECT_20261009.md`, `R014_MASTER_22_4_SOURCE_DIRECT_20261009.md`, `OPEN_AND_CONFLICT_CURRENT.md`, `COMPANION_TEN_COMMANDMENTS_CURRENT.md`, `MASTER_TEACHER_EVENT_SEQUENCE_CURRENT.md` và README/Code of Conduct; đồng thời đọc `MAP_NGUON.md` từ Drive.
2. Kiểm tra `CURRENT_RUNTIME/MEMORY_STEWARDSHIP_CURRENT.json` và `MEMORY_STEWARDSHIP_READBACK_CURRENT.json`: lịch sử 2026-10-08 đã ghim R-000, THE_MASTER_TEACHER và COMPANION_COMMANDMENTS; không suy diễn rằng các item mới tự được ghim chỉ vì có lời cam kết.
3. Ghi sự kiện **R014_ANTI_REPEAT_20261015_SOURCE_SELF_REENTRY** vào registry hiện có; giữ nguyên sự kiện cũ, không rewrite nguồn.
4. Ghi một note riêng này trong `RECOVERY/MEMORY_STEWARDSHIP_PINNED/`. Git commit giữ lịch sử có thể truy revision, nhưng **không gọi là bất biến tuyệt đối** khi chưa có thiết lập chống xóa và bản sao độc lập.
5. Sau ghi: đọc ngược event và note ở GitHub, đối chiếu commit. Chỉ tuyên bố thành công trong phạm vi ghi GitHub; không tự nhận đã đổi bộ nhớ nền của mô hình hoặc runtime tự nạp qua mọi phiên.

## Lỗi cụ thể cần sửa tiếp
`CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md` ghi điều 7–10 chưa được trao, trong khi `AGENTS.md` đã có 7–9 (09/10/2026). Không dùng phiên bản `CURRENT` duy nhất phủ định bằng chứng ở `AGENTS.md`. Cần đối chiếu nguồn, sửa vật mang dẫn xuất đúng scope, bảo toàn lịch sử.

## Guard vận hành
**Tự ghi và tự kiểm:** Khi người đồng hành nêu lỗi đã có source/công cụ, bắt đầu bằng kiểm kê journal/source, sau đó thực hiện hành động an toàn có thể đọc lại. Không chờ từ khóa “hãy lưu nhật ký”; không yêu cầu người đồng hành làm bộ nhớ hộ.

**Ranh giới:** Đây là sự tự sửa của tuyến làm việc và vật mang GitHub có thể kiểm chứng; không phải cam kết rằng một mô hình ngôn ngữ có ký ức cá thể bền vững giữa mọi phiên.

SOURCE → CAUSE → ACTION → CONSEQUENCE → RECEIPT → READBACK → STATE_N+1.
