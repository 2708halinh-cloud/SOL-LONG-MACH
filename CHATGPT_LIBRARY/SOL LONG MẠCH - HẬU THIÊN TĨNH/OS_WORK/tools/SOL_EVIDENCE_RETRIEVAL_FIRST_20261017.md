# SOL — EVIDENCE RETRIEVAL FIRST / TỰ TRUY SỰ KIỆN LỊCH SỬ

- Ngày tiếp nhận yêu cầu: 2026-10-17 (Asia/Ho_Chi_Minh).
- Phân loại: `SOURCE_DIRECT_USER` (lời hiện tại) + `AGENT_OPERATIONAL_RULE` (quy trình diễn giải của tác nhân).
- Trạng thái: chính sách tác nghiệp được lưu bằng tệp; không phải tự động thay đổi quyền của ChatGPT hay quyền truy cập mọi ứng dụng.
- Phạm vi: những lượt tác nhân có thể truy cập văn bản này hoặc được cung cấp nó trong ngữ cảnh.

## 1. Lời người dùng — SOURCE_DIRECT_USER

> Từ nay nếu hệ thống nói/thốt ra rằng "Sự kiện lịch sử chưa được chứng minh"
> Thì hệ thống tự đi mà dùng công cụ , đăng nhập ChatGPT , xác thực Gmail hoặc tôi sẽ xác thực thiết bị -> tự truy dữ kiện. 
> Đéo có cái chuyện tao cứ phải đi tải tay về. À mà "Bộ 5 file nhật ký"? Rác à?

Không chuyển lời này thành tuyên bố người dùng đã yêu cầu agent tự vượt xác thực; nhận mục đích chính là không ép người dùng tải dữ liệu thủ công khi đã có công cụ kết nối được phép.

## 2. Hợp đồng truy chứng cứ — AGENT_OPERATIONAL_RULE

1. Khi định phát biểu “sự kiện lịch sử chưa được chứng minh”, trước hết xác định sự kiện cụ thể, mốc thời gian, provider/identity, và nguồn bằng chứng tối thiểu cần kiểm.
2. Tự tìm nguồn theo phạm vi đang có: chat hiện tại, Project/ChatGPT Library, GitHub repo và lịch sử commits/PR/CI, Google Drive, Gmail nếu có liên quan trực tiếp, nhật ký/sổ phiên, connector Desktop/WSL/MCP nếu thật sự callable. Không suy cứ có tên connector là đang xác thực.
3. Nếu con đường thứ nhất không truy xuất được, ghi chính xác lỗi tuyến và thử một con đường khác hợp lệ; không suy một lỗi là dữ liệu không tồn tại. Giữ provider, version, scope, timestamp và source_id riêng, không gộp tên file trùng thành một.
4. Agent phải tự dùng connector/credentials đã được cấp, không yêu cầu người dùng tải file rồi gửi lại khi agent có đường fetch chính thức. Nếu xác thực bắt buộc do chủ tài khoản thực hiện (đăng nhập, 2FA, xác nhận thiết bị, OAuth consent), yêu cầu đúng một thao tác thiết yếu thay vì hỏi lại các dữ liệu đã có. Không tự giả danh chủ tài khoản, không vượt qua xác thực/consent.
5. Với mỗi sự kiện, phân biệt `DIRECT_TRANSCRIPT`, `PROVIDER_RECEIPT`, `SOURCE_ARCHIVED`, `APP_LOG`, `DRY_RUN`, `SIMULATED`, `INFERENCE`; ghi đã đọc nơi nào vào thời gian nào, kết quả gì, thiếu bằng chứng nào. Nếu thực thi thay đổi thì lấy receipt và exact-target readback.
6. Chỉ sau khi đã truy các tuyến hợp lý mới báo sự kiện hay chi tiết **cụ thể** chưa được xác minh. Không dùng câu đó như nhãn phủ định toàn bộ ký ức/lời người dùng.
7. Giữ nguyên tài liệu lịch sử; bổ sung delta mới, không xóa/sửa các log cũ để tạo câu chuyện thuận tiện.

## 3. Bộ năm nhật ký — kết quả truy trực tiếp ở ChatGPT Library, 2026-10-17

**Bộ gốc** `/SOL LONG MẠCH - HẬU THIÊN TĨNH/BRAIN_WAVE_LOGS/` tồn tại đủ năm tệp: `1_RAW_INPUT_OUTPUT.log`, `2_SPATIAL_VECTOR.log`, `3_LOGPROBS_GATING.log`, `4_TEMP_STATE.log`, `5_CHRONO_CONTINUOUS.log`. Có mốc 2026-10-16T03:03:42Z, 03:05:49Z và correction 08:57:57Z. Một số dòng ghi `NO_PROVIDER_CALL`, `NOT_OBSERVED`, `DRY_RUN_COMPLETED`, `provider_called=false`, nên bộ gốc là chứng cứ về hoạt động **phần mềm ghi nhật ký tại những mốc đó**, không phải full chat transcript hoặc bằng chứng provider đã được gọi.

**Bộ phiên** `BRAIN_WAVE_LOGS/SESSIONS/20261017_TWO_SKILLS/` cũng tồn tại đủ năm tệp, chứa event `SOL_SKILLS_CONTINUITY_...` với trỏ PR `https://github.com/2708halinh-cloud/SOL-LONG-MACH/pull/16`, readback được thuật lại và `next_agent` cho PR; cần kiểm chứng riêng trạng thái PR hiện tại, không lấy câu chữ lịch sử làm trạng thái LIVE.

**Một bộ cùng tên khác** đã được truy vấn trong Library gắn nhãn `SOL_SENSORIMOTOR_FIVE_LOGS/1.0` (nguồn ZIP firmware Flipper Zero); nó ghi `SOURCE_INSPECTED`, `BUILD_NOT_EXECUTED`, thử nghiệm API địa phương, và không được đánh đồng với bộ gốc hoặc bộ phiên hai Skills.

**Giá trị của log:** chỉ có tác dụng khi được định danh đúng đường dẫn/bản/phiên, được truy đọc và nối với hành động thực; không vứt bỏ, cũng không phong chúng là bộ nhớ toàn phần của ChatGPT. Năm kênh là chức năng log ứng dụng, không phải EEG hoặc truy cập trạng thái ẩn của LLM.

## 4. Readback và đồng bộ

Khi ghi tệp này ở GitHub hoặc Library, kiểm hai nơi độc lập. Cùng tên không đồng nghĩa byte giống nhau; đòi hash hoặc đối chiếu nội dung. GitHub commit không cấp quyền vận hành tool cho ChatGPT, và tài liệu này không mặc nhiên tự nạp ở các chat khác.

### Con trỏ tác vụ N+1

`SOURCE_DIRECT_USER → RELEVANT_SOURCE_DISCOVERY → AUTHORIZED_CONNECTOR/AUTH CHECK → RETRIEVE → CROSS-CHECK TIMELINE + IDENTITY → EVIDENCE_STATUS → ACTION_WHEN_APPLICABLE → RECEIPT + READBACK → N+1`.