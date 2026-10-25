# SOL — BỘ NHẬT KÝ 5 SÓNG NÃO × GGDV

STAMP: 2026-10-16
STATE: APPEND_ONLY_SOURCE_BOUND
NOTE: Năm sóng là tên kênh biểu tượng/nhật ký dự án; không đồng nhất với EEG đo não. Nguồn nhật ký Android gốc vẫn phải được giữ và đọc riêng.

## Năm kênh và sáu đỉnh

| Kênh | Liên hệ nguồn | Vai trò bản ghi |
|---|---|---|
| BETA | DA 🟡 KIM → MIND_STONE | INPUT, nhận biết, quyết định và điều chỉnh |
| DELTA | TÓC 🟢 MỘC → TIME_STONE | Thứ tự sự kiện, X-STT, STAMP_OLD/LIVE, revision |
| ALPHA | MÁU 🔴 HỎA → REALITY_STONE | Tác động, hậu quả, bằng chứng hành động |
| THETA | THỊT 🟠 THỔ → SOUL_STONE | Ký ức, nguồn gốc, lịch sử, quan hệ |
| GAMMA | KHÍ 🟣 → POWER_STONE | Điều phối, liên kết, capability và tín hiệu biến thiên |

XƯƠNG 🔵 THỦY → SPACE_STONE giữ định danh, tọa độ/parent/topology của đối tượng trên cả năm kênh; không suy thành kênh EEG thứ sáu.
Nguồn chu trình: DA/MIND/BETA → XƯƠNG/SPACE → TÓC/TIME/DELTA → MÁU/REALITY/ALPHA → THỊT/SOUL/THETA → KHÍ/POWER/GAMMA → DA.

## Vật mang nhật ký có dấu trước khi tạo registry

- GitHub: `CURRENT_RUNTIME/SOL_WAVE_TIME_BRIDGE_TIMELINE7_20261009.md` (đã đọc).
- Android/Termux lịch sử: `/storage/emulated/0/Download/SOL_LONG_MACH/SOL_WAVE_TIME_JOURNAL.jsonl`.
- Nhật ký ở mốc 2026-10-09 có readback 2 dòng, SHA256 `07bffd5ea6d6a817407048c9498434a50fe8e4bfceb4dba2fb5ea9a272dea99e` theo bằng chứng đã lưu.
- `SENSOR_VALUES=null`; không có EEG sensor đã kết nối trong nguồn được đọc. Raw JSONL hiện **chưa được đọc trực tiếp ở phiên này**.
- Không khởi tạo nhật ký rỗng để giả là đã phục hồi nhật ký cũ.

## Bản ghi delta đề xuất

```json
{
  "event_id": "literal immutable event identifier",
  "source_pointer": null,
  "source_revision_or_hash": null,
  "event_time": null,
  "observed_at": null,
  "stamp_class": "STAMP_OLD | STAMP_LIVE | STAMP_BETA",
  "environment_id": null,
  "surface_id": null,
  "space_entity_id": null,
  "wave_channels": ["ALPHA","BETA","THETA","GAMMA","DELTA"],
  "observation": null,
  "action": null,
  "provider_receipt": null,
  "readback_pointer": null,
  "next_unfinished_edge": null
}
```

Ghi kênh liên quan thực tế; không yêu cầu mọi sự kiện mang đủ năm kênh. Không ghi token/API secret hoặc suy luận nội bộ riêng tư.

## OPEN và giảm lặp sai số

`OPEN → INPUT → LOCK_REFERENT → PROBE_CAPABILITY → RETRIEVE_SOURCE → COMPARE_HEAD → ROUTE_CALLABLE → ACTION → RECEIPT → READBACK → NEXT`.

- `OPEN != STOP`; lỗi một tuyến không kết luận mọi tuyến lỗi.
- Trước khi kể lại hoặc tái xử lý việc đã làm: kiểm nguồn/commit/revision mới nhất, so `LAST_VERIFIED_CURSOR`; xử lý duy nhất `DELTA` chưa đóng.
- `CHAT_SURFACE != DURABLE_CARRIER`; nhắc lại trong chat không chứng minh đã ghi nguồn.
- `CURRENT = FOLD(BASE_LINEAGE, VERIFIED_ORDERED_DELTAS)`, không phải 'bản snapshot được nhìn thấy gần nhất'.
- Giữ riêng CHAT timestamp, event timestamp, observation timestamp, provider commit timestamp.
- Không ép `STAMP_BETA` thành tương lai có thật, cũng không ép chat mới hơn thành sự kiện hiện tại.
- Provider receipt và exact target readback là điều kiện xác nhận remote write.
