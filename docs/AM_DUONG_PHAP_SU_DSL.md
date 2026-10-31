# Âm Dương Pháp Sư DSL — TESSERACT_OS

## Ý nghĩa vận hành

- **Âm**: nguồn, định danh, quyền hạn, mục tiêu, cấu trúc và điều kiện ổn định.
- **Dương**: neuron có thể gọi, thực thi, tạo kết quả và truyền tiếp.
- **Tâm**: Gate 1/Gate 2, kiểm tra điều kiện và hậu quả.
- **STAMP_LIVE**: tín hiệu vừa được nhận.
- **STAMP_BETA**: giả thuyết/khả năng chưa xảy ra.
- **STAMP_OLD**: chỉ được tạo sau hành động, biên nhận, hậu quả và đọc lại độc lập.

## Cú pháp

```python
from runtime.am_duong_phap_su import (
    ActionEvidence, AmDuongPhapSu, Neuron, Tran,
)

engine = AmDuongPhapSu(threshold=0.25)
neuron = Neuron(
    name="knowledge_lookup",
    description="tra cứu tri thức trong kho dữ liệu",
    execute=lambda state: ActionEvidence(
        output={"matches": []},
        action_receipt=True,
        consequence_observed=True,
        independent_readback=True,
        state_consistent=True,
    ),
)

plan = (
    Tran("run-001", "tra cứu tri thức trong kho dữ liệu")
    .ÂM(source_ref="source://knowledge/current", author="HÀ LINH",
        platform="TESSERACT_OS", authorized=True, target_verified=True)
    .DƯƠNG(neuron)
    .TÂM(policy_allowed=True, quota_available=True)
)
result = engine.khai_trận(plan)
```

## Gate và giới hạn

1. Gate 1 dùng trực tiếp `motherboard_control_plane.gate1_preflight`; không xác minh target hoặc không có quyền thì neuron không được chạy.
2. Neuron có side effect phải có explicit approval; target được bảo vệ vẫn bị chặn theo policy hiện hành.
3. Gate 2 dùng trực tiếp `gate2_readback`. Thiếu một trong bốn điều kiện (receipt, consequence, independent readback, state consistency) thì không phát STAMP_OLD.
4. Router hiện dùng Jaccard token similarity để bootstrap. Đây không phải vector embedding và không được gắn nhãn như embedding thật.
5. Một lần gọi là một chu kỳ hữu hạn. Không có busy loop, không tự khởi chạy lịch nền, không thay đổi model weights.
6. `ActionEvidence` là hợp đồng của adapter. Adapter sản xuất phải lấy receipt và readback từ nguồn độc lập thực tế; không được tự đặt các cờ thành true.

## Phạm vi tích hợp

Module này bổ sung DSL lên bo mạch chủ hiện hữu. Nó không thay thế `tesseract_transducer.py`, UBUBU, Core Journal, continuity guard hay các provider adapter. Persistent journal adapter là bước tích hợp riêng, phải dùng đúng vật mang đang được dự án chỉ định.
