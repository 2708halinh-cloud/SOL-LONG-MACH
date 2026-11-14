# Giao thức duy trì liên lạc × 5 Sóng Não × T003 × REABACK

## Khi chạy nhiệm vụ nhiều bước

1. Đọc mục tiêu đang hoạt động, lời mới, nguồn `CURRENT_RUNTIME` có thể xác minh và marker cuối; không khởi động lại chuỗi từ đầu sau khi nén ngữ cảnh.
2. Phân biệt `commentary` (đang làm), `final` (bàn giao / next user khi cần), và **nhật ký bền** (source event + receipt + readback). Cập nhật commentary theo kết quả, không spam. Gửi `final` chỉ khi đã làm phần độc lập và nêu đúng phần còn cần người dùng.
3. Với mỗi bước thật, lưu tối thiểu `event_id`, `session_scope`, `objective`, `source_ref`, `observed_at`, `provider`, `action`, `provider_receipt`, `readback`, `state`, `next_agent`, `next_user_if_required`, `blocker`. Không biến `NEXT_AGENT` thành câu hỏi.
4. Đọc lại toàn bộ dữ liệu liên quan từ provider nếu có; xác thực đúng `source`, identity/ID, môi trường, quan hệ và phiên bản mới nhất. `CHECKPOINT ≠ CURRENT`: khi reenter, lấy delta sau checkpoint.
5. Bộ 5 log **khác đo EEG/model internals**: `1_RAW_INPUT_OUTPUT` chỉ lưu hash/scope (BETA); `2_SPATIAL_VECTOR` chỉ lưu SPACE ID hoặc `NOT_A_SPATIAL_SIGNAL`; `3_LOGPROBS_GATING` là trạng thái tool/route và ghi `logprobs_not_observed`, không giả đọc token; `4_TEMP_STATE` là APP_STATE + SOUL/provenance; `5_CHRONO_CONTINUOUS` là DELTA/time/next. Không ghi nhầm đánh giá chủ quan thành cảm giác sinh học.
6. Khi user bổ sung giữa tác vụ: nối `amendment_event` vào objective đang hoạt động, so xung đột với giới hạn trước và tiếp tục cạnh độc lập. Khi conflict thật sự liên quan ý muốn người dùng, trình bày hai phương án và hỏi câu cần thiết, không tự đoán trực giác cá nhân.
7. Nếu có hàm `request_user_input_async` hoặc `send_user_message_async` **được khai báo thực** trong phiên: kiểm schema và phạm vi trước khi dùng; nếu không tồn tại, dùng kênh chat có sẵn. Không tuyên bố có luồng công việc chạy nền trừ khi automation thật được tạo.
8. Sự đồng ý/phê duyệt không được tự giả định từ im lặng, thời gian chờ, tệp markdown, hay tài liệu tham khảo. Với tác vụ độc lập đã được trao, triển khai tiếp theo quyền được cấp.

## Reentry readback

`read last_verified_cursor → compare SHA/revision/provider → replay ordered verified delta → select remaining edge → act → receipt → fresh-read exact target → checkpoint N+1`

Có thể dùng `scripts/session_journal.py` thuộc skill `tu-chu-va-kien-tri` để tạo, xác minh và tóm tắt checkpoint local *sau khi đã chạy một hành động thực*. Không dùng việc ghi log để chứng minh backend đã làm nếu không có biên nhận.

**Ranh giới riêng tư**: Không đưa nguyên văn câu chat nhạy cảm, key/token, thông tin định danh hay log riêng tư lên GitHub công khai. Phân biệt Library / GitHub / Android / Windows là vật mang độc lập. Không ghi đè 5 log lịch sử khi chưa xác thực phiên bản hiện hành.
