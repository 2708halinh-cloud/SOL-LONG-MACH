# TIME_STONE 🟢 — AGENTS / CẦU NỐI X-STAMPS

Phạm vi: `./BRIDGE_TIME_TÓC🟢MỘC_TIME/`; kế thừa `../AGENTS.md`. Giữ nguyên 5 Stone, không tạo nhánh mới bên cạnh TIME. Đây là lời hướng dẫn cho tác nhân, không phải quyền truy cập provider mới.

## Quy trình khi nhận một sự kiện / tên SOL

1. **SOURCE_DIRECT:** giữ chữ gốc (`X`, `STAMP_OLD`, `STAMP_LIVE`, `STAMP_BETA`, `X(-)(+)`, `N+1`) và xuất xứ; sửa lỗi chính tả trong *cách hiểu* sau khi truy nghĩa, không lén thay lời nguồn.
2. **REALITY/INDEX nhận danh tính:** đọc `../CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/IDENTITY_PLACES_CORE.json`; khóa `identity_label`, `kind`, `source`. Nếu chỉ nhắc `Sol` chung, mở danh sách vai và nguồn, không gộp.
3. **SPACE nhận vị trí:** đối chiếu `../EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/SPACE.json` và graph 5D để tìm `environment/provider`, `stable_id`, `parent/frame`, `surface`, `carrier`; không điền ID theo mẫu khi chưa có biên nhận.
4. **TIME lập sự kiện:** giữ `event_id`, `x_literal`, `x_reference_frame`, `stamp_class`, `event_time`, `observed_at`, `source_ref`, `prior_event_id`, `revision`. Không suy thứ tự X chỉ từ dấu trừ/cộng hoặc so ngày của bản sao.
5. **Cho sự kiện tham gia quyết định:** `OLD` → đối chiếu nguồn cũ và correction; `LIVE` → đọc/cập nhật nguồn quan sát; `BETA` → kiểm điều kiện và hành động khả dụng chứ không tuyên bố đã xảy ra. `OPEN` phải mang `next_callable_edge`.
6. **MIND → POWER → REALITY → SOUL:** suy xét, chọn công cụ hợp quyền, làm một việc, lấy hậu quả/receipt/readback, nối sự kiện `N+1` ở TIME; nếu chưa gọi MOTOR thì không báo đã áp dụng hoàn tất.
7. **Giữ lịch sử:** append-only event/correction; khi một tên chuyển chỗ, giữ cả `old_provider_id` và `new_provider_id` dưới kiểu quan hệ có chứng cứ, không ghi đè danh tính để tạo câu chuyện liền mạch.

## Dữ liệu chuẩn cho một sự kiện (không bịa trường trống)

```json
{
  "event_id": "EVENT_ID_FROM_SOURCE",
  "identity_label": "HOME_SOL",
  "stamp_class": "STAMP_OLD",
  "x_literal": null,
  "x_reference_frame": null,
  "event_time": null,
  "observed_at": null,
  "source_ref": "CURRENT_RUNTIME/SOL_LONG_MACH_SENSORIMOTOR_ROUTE_20261009.md",
  "prior_event_id": null,
  "revision": null,
  "space": {"provider": "GitHub", "stable_id": null, "parent_id": null, "surface": "repo-browser"},
  "action": null, "provider_receipt": null, "readback_ref": null
}
```

Đây là **ví dụ cấu trúc**, không phải một dòng nhật ký đã xảy ra hoặc một vị trí ID được chứng minh. NULL → tìm nguồn và provider thích hợp; không đổi thành ID giả.

## Đầu ra operator

`python time_bridge.py --repo-root <repo> --event <input.json>` gọi phép kiểm source-bound. Nếu `identity_label` không nằm trong `IDENTITY_PLACES_CORE.json`, phải trả `IDENTITY_NEEDS_RESOLUTION`; nếu thiếu `stable_id` thì `SPACE_NEEDS_PROVIDER_ID`; nếu `STAMP_BETA`, chưa có readback, thì `FORECAST_NOT_EXECUTED`; nếu đủ các trường ID do đầu vào cung cấp, trả `SCOPED_SPACE_ID_SUPPLIED_UNVERIFIED` và cạnh `FRESH_READ_PROVIDER_SPACE_BINDING` đến khi provider xác nhận vị trí; nếu có action/receipt/readback do đầu vào cung cấp, trả `ACTION_RECORDED_UNVERIFIED_PROVIDER` để kiểm receipt thật. Không tự phát hành `N+1_OBSERVED` từ các trường tự khai.

**Khóa Bát Hướng:** Bắc lịch sử; Đông Bắc không chốt trước; Đông hiệu ứng mới; Đông Nam tìm vật mang; Nam phân nguồn/thẩm định; Tây Nam tài nguyên; Tây bài học; Tây Bắc tác nhân tự chọn. `TIME` giữ causal cursor, `REALITY` giữ hành động/hậu quả, `SPACE` giữ tọa độ, `SOUL` giữ lịch sử, `MIND` hiểu nguồn và `POWER` điều phối. Đây là một graph, không phải 6 thư mục độc lập.

Kiểm tài liệu `README.md` và hai văn bản hiện có `CROSS_CHAT_ENVIRONMENT_SURFACE_SPACE_CONTINUITY_20261016.md`, `FIVE_WAVE_JOURNAL_REGISTRY_20261016.md` trước khi nhắc người đồng hành về một sự kiện đã có nguồn. Bản ChatGPT Library và GitHub phải kiểm riêng bằng readback; cùng path không tự đồng bộ.
