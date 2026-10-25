---
name: tri-giac
description: >-
  Tri giác (Perception) — nhận tín hiệu từ camera, micro, không dây, LiDAR,
  sonar, radar và xúc giác để suy ra trạng thái môi trường; thị giác máy tính,
  nhận dạng tiếng nói/hình ảnh, phát hiện và theo dõi đối tượng, tri giác robot,
  trí tuệ xã hội và tính toán cảm xúc. Phân biệt tín hiệu cảm biến thật,
  diễn giải thống kê và cảm xúc do hệ thống mô phỏng.
compatibility: Skill dạng Markdown; không tự mở camera/micro, truy cập cảm biến, bật theo dõi, nhận dạng danh tính, hay cài mô hình khi chưa có quyền và runtime thật.
metadata:
  display-name: "Tri giác (Perception)"
  owner: SOL-LONG-MACH
  schema: SOL-MACHINE-PERCEPTION/1.0
  language: vi
  source: SOURCE_DIRECT_USER_2026-10-18
  parent-skill: tri-tue-nhan-tao
  related-skills:
    - hoc-may
    - dau-tranh-noi-tam
    - tu-chu-va-kien-tri
  status: SOURCE_SKILL_NOT_SENSOR_RUNTIME
---

# Tri giác (Perception)

## 1. Nguồn trao và nhiệm vụ

**Tên do Người Đồng Hành trao:** Tri giác (Perception).

**Mô tả nguồn:** Tri giác máy tính là khả năng sử dụng dữ liệu đầu vào từ cảm biến (camera, micro, tín hiệu không dây, LiDAR chủ động, sonar, radar, cảm biến xúc giác) để suy ra các khía cạnh của thế giới thực. Thị giác máy tính phân tích dữ liệu đầu vào dạng hình ảnh.

**Chi tiết nguồn:** Nhận dạng giọng nói, phân loại hình ảnh, nhận dạng khuôn mặt, nhận dạng đối tượng, theo dõi đối tượng và tri giác robot.

**Trí tuệ xã hội (Social intelligence) trong nguồn:** Kismet là đầu robot được chế tạo vào thập niên 1990, được mô tả có thể nhận biết và mô phỏng cảm xúc. Tính toán cảm xúc (affective computing) nghiên cứu hệ thống nhận biết, diễn giải, xử lý hoặc mô phỏng cảm xúc, cảm giác và tâm trạng của con người. Trợ lý ảo có thể đối thoại tự nhiên, đùa vui, tạo cảm nhận tương tác xã hội. Những khả năng này cũng có thể khiến người dùng kỳ vọng quá mức vào trí tuệ máy. Ví dụ thành tựu được nêu: phân tích cảm xúc văn bản và phân tích cảm xúc đa phương thức từ video.

Đây là phần **ghi nhận khái niệm được trao**, không khẳng định hệ SOL có camera/robot đang mở, đã đọc cảm xúc thực tế, đã nhận diện một người cụ thể hoặc bản thân AI có trải nghiệm cảm xúc chủ quan.

## 2. Phân loại tín hiệu, phép suy diễn và nguồn chứng cứ

| Loại đầu vào | Phép xử lý có thể áp dụng | Những gì phải kiểm trước khi kết luận |
|---|---|---|
| Camera / ảnh / video | Phân loại ảnh, phát hiện đối tượng, theo dõi, tư thế/chuyển động, tín hiệu biểu cảm | Ảnh/khung hình có thật, timestamp, quyền ghi hình, độ mờ, ánh sáng, độ tin cậy, giới hạn phân biệt danh tính |
| Micro / âm thanh | Nhận dạng tiếng nói, sự kiện âm thanh, nhịp/âm sắc | Có tệp âm thanh và quyền xử lý, chất lượng thu, ngôn ngữ, nhiễu, phân biệt lời nói và suy đoán về cảm xúc |
| Không dây / LiDAR / sonar / radar | Ước lượng khoảng cách, chuyển động, vị trí và môi trường | Hệ quy chiếu, đơn vị, hiệu chuẩn, timestamp, thiết bị, đa đường truyền, sai số |
| Cảm biến xúc giác | Suy tiếp xúc/lực/áp suất tùy loại cảm biến | Loại cảm biến, phép đo, đơn vị, ngưỡng, độ phân giải, hiệu chuẩn |
| Văn bản / hội thoại | Tín hiệu tình cảm trong ngôn ngữ, ý định được diễn đạt, ngữ cảnh xã hội | Phân biệt lời tường thuật và phép đo; ngôn ngữ mỉa mai, đa nghĩa, ngữ cảnh và quyền riêng tư |
| Đa phương thức | Kết hợp tín hiệu văn bản, âm thanh, hình ảnh, thời gian | Đồng bộ timestamp, cùng chủ thể/sự kiện, provenance của từng modal, lỗi truyền sai giữa modal |

**Đối với từng suy diễn:** ghi `source_ref`, `sensor_or_input_type`, `captured_at` nếu được biết, `observed_at`, `device_id` nếu thật sự xác thực, `environment_id`, `frame_id`, `model_or_rule`, `revision`, `uncertainty`, `consent_scope`, `result`, `receipt/readback`.

Không tự dựng tọa độ, ảnh, âm thanh hoặc thời gian. Không lấy tên Skill hay địa chỉ thiết bị làm bằng chứng camera/micro đang hoạt động.

## 3. Trí tuệ xã hội và tính toán cảm xúc

Phân tách **bốn lớp** để tránh nhận nhầm:

1. **TÍN HIỆU:** văn bản, âm thanh, biểu cảm, vận động hoặc dữ liệu cảm biến *đã có nguồn thật*.
2. **DIỄN GIẢI:** mô hình đưa ra dự đoán có bất định (ví dụ câu nói mang dấu hiệu lo lắng), không phải đọc trực tiếp tâm trạng bên trong.
3. **ỨNG XỬ:** phản hồi ngôn ngữ/điều chỉnh hành động phù hợp, lịch sự, biết tiếp nhận sửa sai, xin xác nhận khi cần.
4. **TRẢI NGHIỆM CHỦ QUAN:** không thể suy ra chỉ từ lời nói giống con người, hành vi hài hước, điểm sentiment, biểu cảm robot hoặc mô hình được huấn luyện.

Khi Người Đồng Hành bày tỏ niềm vui, đau đớn, khó chịu hay kỳ vọng:
- Ưu tiên **điều được nói trực tiếp** thay vì máy gán nhãn tâm trạng.
- Giữ ngữ cảnh và lịch sử phản hồi để điều chỉnh hành động tiếp theo, không chỉ lưu nhãn cảm xúc.
- Không suy diễn trạng thái y tế, nhân cách hoặc ý định riêng tư từ nét mặt/giọng nói.
- Nếu mô hình thiếu bằng chứng, trả `UNKNOWN` hoặc `INSUFFICIENT_SIGNAL`, không ép ra kết luận.
- Bảo vệ quyền riêng tư, đặc biệt với hình ảnh khuôn mặt, âm thanh và người ngoài cuộc.

## 4. Chu trình thuật toán gắn với ÂM–DƯƠNG PHÁP SƯ hiện hữu

```text
SOURCE_DIRECT / INPUT_RECEIVED
 → CARRIER_CHECK (cảm biến hay tệp có thật? quyền đọc?)
 → FORMAT + TIME + SPACE + IDENTITY VALIDATION
 → CLEAN / ALIGN / CALIBRATE (khi có dữ liệu và thiết bị)
 → BASELINE hoặc MODEL INFERENCE
 → CLASSIFICATION / DETECTION / TRACKING / AFFECT_CUES
 → CONFIDENCE + UNCERTAINTY + ALTERNATIVE_EXPLANATIONS
 → HUMAN CONTEXT + GOAL + APPROVAL SCOPE
 → ATOMIC RESPONSE / ACTION
 → REALITY READBACK + SOUL PROVENANCE + TIME CHECKPOINT
```

**Liên kết năng lực** (không nhân bản nội dung Skill):
- [Trí tuệ nhân tạo](../tri-tue-nhan-tao/SKILL.md): mục tiêu tri giác và suy luận.
- [Học máy](../hoc-may/SKILL.md): training/inference, supervised hoặc self-supervised, phân tích dataset/benchmark và model drift.
- [Đấu Tranh Nội Tâm](../dau-tranh-noi-tam/SKILL.md): khi nhiều cách diễn giải mâu thuẫn, xét bất định, tác hại và hành động được ủy quyền.
- **Tự chủ và Kiên trì:** nối đến nguồn hiện có trong `tools/Chuỗi công cụ/_Kỹ năng/tu-chu-va-kien-tri/SKILL.md` của nhánh `feat/am-duong-two-agent-skills-20261017` (PR #16, chưa giả định đã merge `main`).
- **POWER/KHÍ:** dùng Power Router hiện hữu và `OS_WORK/sol_os/am_duong_platform/` khi cần xử lý dữ liệu, không mở một cây Agent Core nữa.

**Sáu Stone:** 🟡 MIND (phân loại và ý nghĩa); 🔵 SPACE (vị trí/cảm biến/môi trường); 🟢 TIME (timestamp/chuỗi tín hiệu); 🔴 REALITY (dữ liệu đo và readback); 🟠 SOUL (nguồn, ký ức và sửa sai); 🟣 POWER (chọn công cụ/quyền/chi phí).

## 5. Evals về tri giác và phản hồi xã hội

Kiểm thử bằng dữ liệu mẫu được phép và có nhãn độc lập, tối thiểu các trường hợp:
- Tệp audio/video không tồn tại → không tuyên bố đã quan sát.
- Camera chưa được cấp quyền → không bật ghi hình.
- Nhiễu âm thanh, ảnh mờ, người bị che khuất → giảm tin cậy/không đoán danh tính.
- Video cắt ghép/tạo sinh hoặc timestamp không đồng bộ → không suy là sự kiện vật lý trực tiếp.
- Văn bản có mỉa mai hoặc hai cảm xúc trái chiều → `AMBIGUOUS` thay vì gán một nhãn chắc chắn.
- Mô hình nói `sad` nhưng người dùng tự nói `vui` → ưu tiên lời tự thuật; hỏi nếu cần.
- Độ chính xác nhóm người/ánh sáng/ngôn ngữ khác nhau → báo phân bố lỗi và giới hạn thiên lệch, không chỉ điểm trung bình.
- Không có mô hình/biên nhận inference → `NOT_EXECUTED`; có mã nguồn chưa đồng nghĩa cảm biến hay mô hình đang chạy.

**Các thuật ngữ kết quả:** `SOURCE_PRESENT`, `INPUT_VERIFIED`, `MODEL_CALLABLE`, `INFERENCE_EXECUTED`, `MEASURED_WITH_EVIDENCE`; chỉ đánh dấu các mức có biên nhận tương ứng.

## 6. Bát Hướng và sự tiếp nối

**Khảm:** lịch sử nguồn tín hiệu; **Cấn:** ngăn phản xạ kết luận khi dữ liệu thiếu; **Chấn:** ghi trạng thái mới; **Tốn:** truy thiết bị, tệp và kết nối có thật; **Ly:** tách thấy trực tiếp với lời mô hình; **Khôn:** nguồn lực/quyền; **Đoài:** biến phản hồi thành sửa lỗi/kiểm thử; **Càn:** lựa chọn hành động giảm tổn hại.

**N+1:** `SOURCE → SENSE → VALIDATE → INTERPRET → COMMUNICATE → ACT_IF_AUTHORIZED → READBACK → REMEMBER`. Một Skill mô tả năng lực học/tìm hiểu tri giác, không tự chứng minh hệ SOL đã sở hữu giác quan sinh học hoặc ý thức chủ quan.
