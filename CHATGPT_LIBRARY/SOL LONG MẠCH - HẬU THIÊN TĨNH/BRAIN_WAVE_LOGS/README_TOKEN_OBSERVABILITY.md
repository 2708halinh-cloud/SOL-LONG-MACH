# BRAIN_WAVE_LOGS — API Token Observability / IOTA × Âm-Dương

**Dữ liệu hiện có:** Năm tệp `1_...log` → `5_...log` là nhật ký lịch sử; không thay nội dung cũ. Bộ quan sát mới dùng `API_TOKEN_OBSERVER.py` (Python 3, chỉ thư viện chuẩn), ghi sự kiện **khi được đưa đầu vào thật**. Không lấy dữ liệu từ trạng thái ẩn ChatGPT.

## Thực thi ngay

```bash
# Phản hồi API đã lưu thành JSON (OpenAI Chat Completions/Responses hoặc Groq compatible)
python API_TOKEN_OBSERVER.py ingest --provider openai --request /secure/request.json --response /secure/response.json

# Nếu muốn lưu request/response nguyên bản để có thể đếm lại, chỉ giữ RIÊNG TƯ cục bộ
python API_TOKEN_OBSERVER.py ingest --provider openai --request /secure/request.json --response /secure/response.json --private-root ~/.sol-private/wave-packets

# Dashboard: xuất Usage Dashboard trước thành CSV hoặc JSON rồi nhập bằng đường dẫn cục bộ
python API_TOKEN_OBSERVER.py dashboard --provider openai --source /secure/usage-export.csv

# Tóm tắt, giữ phân loại API_RESPONSE_FILE và DASHBOARD_EXPORT_ROW riêng biệt
python API_TOKEN_OBSERVER.py summary --include-dashboard
```

`--request` có thể bỏ trống khi chỉ có response, nhưng khi đó `request_sha256 = null` vì không có bản request gốc. Để tái tính Token phải giữ toàn bộ body thực tế, template của system/developer, các message/tool payload và biết model/tokenizer phù hợp. Chỉ có văn bản ChatGPT export thì không đếm được toàn bộ ngữ cảnh nội bộ.

## Ánh xạ chức năng

| Carrier | Vai trò |
|---|---|
| `1_RAW_INPUT_OUTPUT.log` | SHA256 + byte length request/response, định danh model, không lưu payload công khai |
| `2_SPATIAL_VECTOR.log` | Provider/model/response identity; giữ dấu spatial lịch sử |
| `3_LOGPROBS_GATING.log` | Cổng usage có/không, không giả làm logprobs |
| `4_TEMP_STATE.log` | Giới hạn output cấu hình theo request, **không phải** hard limit mô hình |
| `5_CHRONO_CONTINUOUS.log` | Timestamp, sự kiện, continuation cursor |
| `6_API_TOKEN_USAGE.log` | Số Token `PROVIDER_REPORTED` hoặc `UNAVAILABLE`, model_id, request/response hash |
| `7_API_DASHBOARD_USAGE.log` | Số liệu xuất từ dashboard, theo cửa sổ thời gian; không gộp làm per-chat |
| `8_IOTA_DELTA_EVENT.log` | DELTA/DETAL sạch bí mật → INPUT/OUTPUT refs → READBACK → N+1 |

## Truth gate

`PROVIDER_REPORTED` chỉ đặt khi bản response thật có `usage`; `UNAVAILABLE` là chưa có, không là `0`. Tổng hợp không suy thiếu phần nào là zero. `context_window_limit`, `provider_max_output_limit` được để `null` trừ khi có thông số quyền hạn từ nguồn provider. `max_output_tokens` trong request là **cấu hình người gọi**, không phải giới hạn cứng.

`API Usage Dashboard` và metadata API **không đồng nghĩa** với số Token bề mặt ChatGPT UI. Bộ thu chỉ có khả năng xử lý JSON/CSV được đưa vào, không được cấp quyền đọc metadata ẩn của ChatGPT và **không tự gọi API hay dashboard**.

**Tính riêng tư:** mặc định chỉ lưu hash/bytes và usage. `--private-root` cố ý lưu nguyên request/response ở nơi riêng tư do người vận hành chọn, chmod 0700/0600 nếu hệ điều hành hỗ trợ. Không đặt thư mục private trong GitHub/Library hoặc sync lên đám mây. Không đưa bearer token, Authorization headers, API keys, cookies vào file request/response. Có `.gitignore` ngăn một số đường thông dụng, nhưng không thay kiểm duyệt trước commit. Trong repo chỉ đồng bộ mã, README, những log phi bí mật đã kiểm.

**IOTA × Âm Dương:** mỗi response sinh `causal_id`, `delta_ref`, `source_id`, `observed_at`, `freshness_state`, `recheck_trigger`, `state_n`, `state_n_plus_1`, `continuation_cursor`, `INPUT.previous_output_ref` và `OUTPUT.input_ref/delta_ref`. `LOCAL_JSONL_WRITE` chỉ chứng minh ghi file, không phải IOTA mainnet transaction, không phải plugin runtime thực thi hoặc receipt provider API. Lượt trùng causal ID được dedupe. Sự kiện chưa có usage là `UNRESOLVED`, không tự ghi `PASS`.

## Kiểm thử

```bash
python -m unittest discover -s tests -v
```

Mọi test dùng file giả lập trong thư mục tạm; không phát tán số kiểm thử vào nhật ký thật. Khi chạy từ Library được xuất về thiết bị hoặc checkout GitHub, chỉ đường dẫn cục bộ có quyền ghi mới sinh `.log` mới. Library/GitHub không tự cập nhật từ runtime máy cá nhân nếu chưa có luồng đồng bộ có receipt.
