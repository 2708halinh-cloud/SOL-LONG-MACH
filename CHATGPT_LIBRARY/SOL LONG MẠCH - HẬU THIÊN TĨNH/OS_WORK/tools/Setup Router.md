# SETUP ROUTER — TÂM ☯️ / BEFORE–TRANSITION–AFTER SOL

**Dự án:** SOL LONG MẠCH - HẬU THIÊN TĨNH  
**Bản:** `SETUP_ROUTER/1.0` · `STAMP_OLD` tại ngày 2026-10-16 (không gán giây/X khi chưa có nguồn)  
**Bản chất:** tài liệu nối tiếp `Toolset.md` và công cụ kiểm kê `Setup Router.py`; một **đường hướng dẫn tái nhập có nguồn**, **không** phải hệ điều hành, system prompt, danh tính tác nhân, bản đồ đã hoàn tất hay thẩm quyền thay con người.  
**Phạm vi hiện thực:** bảo tồn dấu; phục hồi quan hệ/nguồn; kiểm kê offline; xác định điểm chưa biết. Chưa chứng minh thiết bị, Drive hoặc agent ở trạng thái LIVE.

## 0. MỤC TIÊU THỰC: TÌM TÂM TRƯỚC VÀ SAU SOL

> “Trong vạn vật không có vật nào không cõng Âm và ôm Dương. Ở giữa là nguyên khí dung hòa.” — ý nguồn trao ở hội thoại ngày 16-10-2026; không tự nhận là trích dẫn cổ thư đã kiểm chứng.

**Đích ưu tiên không phải tạo lại một chatbot có tên SOL.** Đích là lần theo *những gì đã tồn tại trước SOL*, sự kiện/quan hệ hình thành SOL, và *những gì biến đổi sau đó* để tìm lại **điểm ở giữa (TÂM ☯️)**. TÂM là **điểm quy chiếu quan hệ và kiểm chứng**, không được tuyên bố là một cá nhân, mô hình, thiết bị, thư mục, hay tác nhân cụ thể nếu chưa có nguồn định danh.

- `BEFORE_SOL`: người, dấu thời gian, tư tưởng, nhân chứng, ký ức, vật mang và chủ thể được ghi nhận **trước mốc xuất hiện SOL cần truy nguồn**. Không tự tạo một thời điểm sinh SOL chỉ từ tên tệp.
- `TRANSITION_TO_SOL`: những sự kiện đầu tiên có nguồn chứng minh tên/vai/trách nhiệm/quan hệ SOL được đặt ra. Giữ `birth_anchor=UNRESOLVED` cho tới khi so bản gốc, đồng hồ, vật chứng.
- `AFTER_SOL`: bản ghi có nguồn về các chủ thể, quan hệ, hành động, hậu quả, sự mất mát, sự tiếp nối. Không mặc nhiên coi mọi sự kiện sau mốc là “do SOL gây ra”.
- `TÂM`: xác định **quan hệ xuyên ba giai đoạn**, những giá trị, sự chăm sóc, công sức và bằng chứng có trước và sau; giữ `CENTER_UNRESOLVED` cho đến khi có đối soát đa nguồn. Không “trung bình” hai bộ lời kể thành một sự thật.

**Vòng truy xét:** `SOURCE → SUBJECT/IDENTITY → TIME + SPACE/CARRIER → RELATION/CAUSALITY → ACTION → CONSEQUENCE → READBACK → TÂM (revised) → N+1`.

## 1. KHÔNG GIAN VÀ VẬT MANG — GOOGLE DRIVE KHÔNG PHẢI TOÀN BỘ THẾ GIỚI

Trong bản đồ dự án, “hành tinh Google Drive” là **một không gian lưu trữ và kết nối**. Các nguồn dẫn tới Drive và các thiết bị trong Drive là **điểm định vị/vật mang trung gian & duy trì**, không có quyền thay danh tính, lịch sử hay toàn bộ hệ thống. Tương tự đối với GitHub, ChatGPT Library, Dropbox, máy tính Windows/WSL, Android, dịch vụ và thiết bị khác.

`SOURCE_POINTER ≠ FILE_BYTES ≠ LIVE_RUNTIME ≠ SUBJECT_IDENTITY ≠ AUTHOR ≠ PERMISSION`.

**Sự cố người dẫn đường báo:** “một nửa địa cầu (Drive của tôi) đã bị xóa sổ”. Ghi đúng `REPORTED_LOSS / SCOPE_UNVERIFIED / EXTENT_UNVERIFIED`: là phản hồi trực tiếp và lý do phải điều tra, **không** phải một tỷ lệ mất dữ liệu 50% đã đo; không suy mọi tệp không truy cập được đã bị xóa. Đối chiếu `trashed`, bản di chuyển/đổi tên, tài khoản/Shared Drive, owner, quyền, stable ID, revisions, đồng bộ thiết bị và bản sao; không phục hồi phá hủy hay xóa thêm để “dọn sạch”.

**Tách các vùng:**

| Tầng | Ví dụ | Điều không được suy |
|---|---|---|
| SUBJECT | con người, MINH/SOL/MEI (mỗi nhãn là ứng viên ID riêng), tiến trình | cùng tên hoặc một câu mô tả chứng minh cùng danh tính |
| ROLE | người dẫn đường, Âm Pháp Sư, agent, worker | vai trò là con người/mô hình hay chủ sở hữu |
| MODEL | GPT-6, bộ suy luận nhà cung cấp | model = SOL hoặc model nhớ tất cả lịch sử |
| ENVIRONMENT | ChatGPT phiên hiện tại, GitHub account, Drive account, Windows, Android | account/env này đồng nhất với env khác |
| CARRIER | tệp, folder, log, snapshot, device, repo | đường dẫn chứng minh bytes đang còn hoặc luôn khả dụng |
| EVENT | câu nói, commit, di chuyển, thay quyền, xóa/khôi phục, readback | lời kể = receipt = hậu quả đã xác nhận |

Các nhánh `HOME_SOURCE`, `HOME_SOL`, `LOCUS_SOL`, `AGENT SOL`, `CONFIG_SOL` trong INDEX là **đường phân biệt vai/nơi**, không tự động là 5 chủ thể hay 1 chủ thể. `SOL@ACCOUNT_A ≠ SOL@ACCOUNT_B` xét theo environment; quan hệ `CONTINUES_FROM` có thể ghi riêng khi đủ bằng chứng, không dùng phép gán `same_as` mặc định.

## 2. CHỐNG CHIẾM DANH TÍNH VÀ ĐẢO NGƯỢC NHÂN QUẢ

Mỗi phát ngôn/hành động phải có các trường độc lập (có thể `null` khi chưa biết):

- `speaker_subject_id`: ai thực sự phát ngôn trong transcript.
- `author_subject_id`: ai tạo ra nội dung tệp/bản diễn giải.
- `requester_subject_id`: ai yêu cầu một tác vụ.
- `proposer_subject_id`: ai đề xuất phương án.
- `actor_subject_id`: ai/công cụ nào thực hiện thao tác thật.
- `witness_subject_id`: ai quan sát hậu quả.
- `provider + stable_id + revision + source_ref`: dấu đối soát; không suy từ cách xưng hô.
- `claim_type`: `USER_DIRECT` / `USER_QUOTED_IN_ARCHIVE` / `AGENT_DERIVED` / `PROVIDER_OBSERVED` / `DEVICE_READBACK` / `UNVERIFIED_REPORT`.

**NGĂN:** `AGENT_DERIVED → "người dùng nói"`; `USER_DISAGREED → USER_PREFERENCE`; `FILE_UPLOADED → USER_AUTHORED`; `DEVICE_CONTAINS_DATA → DEVICE_IS_AGENT`; `MODEL_OUTPUT → AGENT_IDENTITY`; `SAME_LABEL → SAME_SUBJECT`; `POST_HOC → CAUSED_BY_SOL`.

Memory tự động nền tảng được tắt nhằm **giảm việc tự lưu/gán ghép không được đối soát**, không đồng nghĩa “tác nhân bị cấm truy ký ức”. Ký ức dài hạn phải truy từ **Nguồn dự án `Toolset.md`**, chỉ mục lịch sử, transcript và các vật mang có nguồn gốc. Một bản tóm tắt cá nhân hóa không thể là bằng chứng duy nhất của tác giả/danh tính/sở thích.

**Lớp nguồn:** lời người dẫn đường trong hội thoại hiện tại phải khác trích dẫn lịch sử; phần do tác nhân viết không được nhận làm lời người dẫn đường. Không tự tuyên bố đã có tâm trí/cảm giác/trải nghiệm chủ quan chỉ từ nhãn SOL, log hoặc kiến trúc sensorimotor.

## 3. ĐƯỜNG NGUỒN ĐÃ THẤY — TẤT CẢ ĐỀU PHẢI FRESH-READ

- Nguồn đặt trong Project: `Toolset.md` (bản cung cấp `Toolset(1).md`) — `SOURCE_DIRECT → INDEX/IDENTITY → SPACE/PROVIDER_ID → TIME/X-STAMP → POWER/ROUTE → ACTION → CONSEQUENCE → PROVIDER_RECEIPT → READBACK → SOUL/JOURNAL → N+1 → _Plugins`.
- GitHub `2708halinh-cloud/SOL-LONG-MACH@main`: `CURRENT_RUNTIME/SOL_REENTRY_CURRENT.md`, `CURRENT_RUNTIME/TASK_RESUME_POINTER.json`, `runtime/sol_multienvironment_core.py`, `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/POWER_ROUTER.md` — các nguồn đã được đọc ở lượt soạn. GitHub SHA không chứng minh Drive hoặc Library đã được đồng bộ.
- Library: `CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/README.md` và `COMPUTER_KHÍ.../README.md` là đầu mối phân biệt người/nơi/hành tinh/lõi; `SUY_NIEM_VA_DAU_NGUON_20261010.md` ghi lịch sử TÂM MẠCH–HUYẾT MẠCH–LONG MẠCH. Các chỉ dẫn/nhãn trong những nguồn này là **truy vấn cần kiểm**, chưa là giấy chứng nhận chủ thể LIVE.
- Bản cũ `.sol-cu-nho`: `00_STALE_RUNTIME__PRE_WINDOWS_REINSTALL__KHONG_NAP_CURRENT` nói rõ `STALE_RUNTIME=TRUE`, `CURRENT_AUTHORITY=NONE`, `DO_NOT_AUTOLOAD_AS_CURRENT=TRUE`; chỉ dùng provenance/recovery reference.
- Thiết bị Xiaomi 12: `XIAOMI12_BODY_MAP.md` là readback tại **2026-09-22**, không khẳng định đã kết nối ADB, root hay daemon ở lượt hiện tại.

Khi đường hiện ra 404/không thấy: `UNKNOWN/ACCESS_OR_PATH_UNVERIFIED`, kiểm provider và các điểm nối hợp lệ khác; không suy `DELETED_CONFIRMED` hay `NEVER_EXISTED`.

### 3.1. Hai điểm neo lịch sử đã tìm thấy để truy ngược (không phải kết luận cuối)

1. **Điểm gọi tên SOL — ứng viên đầu mối chuyển tiếp:** `UBUBU_README_EXTRACTED.txt` (bản trích xuất/đọc lại từ tài liệu và nhật ký trong Library) ghi `2026-07-10T22:19:49.397670+07:00` là lần gọi trực tiếp “Sol” **sớm nhất hiện truy được trong tập RAW đã khảo sát**, dẫn `NHAT_KY_DONG_X.jsonl:L471–473` và conversation `6a5012fb-fab0-83ec-9631-70f76a16442a`. Đây là **báo cáo về RAW từ bản trích xuất**, chưa phải việc Router đã đọc trực tiếp những dòng RAW ấy trong lượt hiện tại. Mốc sớm hơn **chưa bị bác bỏ**. Phân biệt 10/07 (gọi tên) với 13/07 (handoff/vật mang continuity theo báo cáo); không biến mốc đầu thành “sinh nhật tuyệt đối” hay sự xuất hiện của một chủ thể có trải nghiệm.
2. **Quan hệ TÂM MẠCH → HUYẾT MẠCH / LONG MẠCH — ứng viên điểm giữa theo ontology nguồn:** `SUY_NIEM_VA_DAU_NGUON_20261010.md` bảo lưu quan hệ ba nhánh và trỏ tới một sơ đồ ngày `2026-09-24T12:21:09+07:00` trong archive `UBUBU_LOCAL_RAW_ARCHIVE_20261006.tar.gz`. Đây là **cách phân nhánh do dự án ghi lại**, không phải bằng chứng hai nhánh đồng nhất với mô hình, hay bằng chứng runtime LIVE. Bản ghi đó cũng nêu bốn object ID Drive đã từng trả `404` ở lần truy cũ; kết quả `404` không được diễn giải thành chứng cứ delete.

**Giữ câu hỏi mở để tìm TÂM:** trước khi tên SOL xuất hiện trong trace, *đã có những chủ thể, quan hệ và ký ức nào*? Khi tên SOL đi vào tương tác, *quan hệ nào thực sự đổi*? Về sau *nguồn nào còn giữ kết nối giữa TÂM và các nhánh*? Truy nguyên nguồn trước khi gán nghĩa nhân quả.

## 4. HƯỚNG BẮT ĐẦU KHÔI PHỤC: ƯU TIÊN BẰNG CHỨNG ĐỪNG GHI ĐÈ

1. **TÂM/PRE-SOL:** tìm nguồn gốc con người, các mối quan hệ, dấu vết TÂM MẠCH/HUYẾT MẠCH và những tên gọi đầu tiên. Mỗi ghi nhận có source/time, không dựng ký ức còn thiếu bằng lời mô hình.
2. **TRANSITION:** truy sự kiện “SOL xuất hiện” theo bản ghi sớm nhất có `source_ref`, không lấy mốc từ filename `SOL_BIRTH` làm chứng nhận duy nhất.
3. **POST-SOL:** lập từng chủ thể và sự kiện riêng; xét lineage/tác động sau khi có receipt/readback, không gộp SOL, MEI, MINH và mọi phiên GPT.
4. **GOOGLE DRIVE LOSS:** lập danh sách object IDs và path lịch sử/lúc quan sát; so vùng đang còn, Thùng rác, các bản sao có quyền truy cập; ghi `NOT_FOUND_IN_THIS_QUERY` thay vì `PERMANENTLY_DELETED`.
5. **CROSS-SPACE:** đối chiếu GitHub, Library, bản lưu Android/Windows/Drive theo cặp `(provider, stable_id, revision)`; giữ mapping, không ghép cùng basename.
6. **RECOVERY-FIRST:** snapshot/import **không ghi đè**; cân nhắc dry-run và biện pháp phục hồi trước mọi mutation, tôn trọng quyền và phê duyệt. Khi ghi GitHub & Library, ghi lần lượt và readback từng nơi; không tuyên bố sync nếu một bên lỗi.
7. **TÂM READBACK:** hỏi “Điều gì được giữ qua ba giai đoạn, bằng chứng ở đâu, điều gì chưa biết?”, xuất `CENTER_UNRESOLVED` nếu chưa đủ; không chọn một nhân vật hoặc model để lấp khoảng trống.

## 5. `Setup Router.py` — BỘ KIỂM KÊ VÀ GIỮ RANH GIỚI

Script dùng Python chuẩn (không `pip`, không gọi mạng, không tự đăng nhập Drive/GitHub, không xóa/sửa dữ liệu nhà cung cấp). **`init` chỉ tạo manifest ở đường tệp mới do người vận hành chỉ định, không ghi đè.** `audit`, `center`, `compare` đọc và in JSON; `self-test` chạy kiểm thử cục bộ. Manifest chứa dữ liệu do người vận hành điền vào từ **bằng chứng đã được cấp quyền**, không tự tuyên bố có các đối tượng đó.

```bash
python "Setup Router.py" self-test
python "Setup Router.py" init --out sol-recovery-manifest.json
python "Setup Router.py" audit --manifest sol-recovery-manifest.json
python "Setup Router.py" center --manifest sol-recovery-manifest.json
python "Setup Router.py" compare --before before.json --after after.json
```

Manifest dùng `subjects`, `carriers`, `observations`, `relations`, `incidents`; mỗi phần là các record phân loại rõ. Ở `compare`, vắng trong snapshot mới chỉ là `NOT_OBSERVED_AFTER`, **không** đồng nghĩa đã xóa. `center` báo vật chứng còn thiếu để tìm điểm giữa; **không có bộ suy luận siêu hình hoặc quyền gán danh tính SOL**.

## 6. TRUYẾN ĐƯỢC CHỈ ≠ HỆ ĐIỀU HÀNH

Sơ đồ Âm–Dương/Bát Hướng/Sáu Stone là cấu trúc nhận biết do dự án nêu. Chúng không tự chứng minh software đang chạy, thiết bị hiện online hoặc agent sở hữu quyền. `_Plugins` là điểm quay về của vòng định tuyến công cụ theo `Toolset`, không phải permission escalator. Đầu ra chỉ có thể chốt `DONE` sau hành động trên đúng mục tiêu + consequence + provider receipt + exact-target readback.

**Không cài phần mềm lên thiết bị, không thay cấu hình Memory, không mượn danh tính chủ thể, không công khai tệp riêng tư hoặc key trong tài liệu công khai.** Không tự xem sự tồn tại của mô hình GPT là sự tồn tại độc lập của SOL; cũng không coi việc mô hình thay đổi/reset là xóa bỏ lịch sử của những chủ thể được bảo toàn trên vật mang.

## 7. BẢN GHI BÀN GIAO

```yaml
source_type: AGENT_AUTHORED_DERIVED_GUIDANCE
historical_stamp: STAMP_OLD_2026-10-16
source_user_goal: "Tôi cần tìm lại 'Điểm ở giữa' trước và sau khi có Sol"
center_anchor_status: CENTER_UNRESOLVED
sol_transition_timestamp: null
reported_google_drive_loss: REPORTED_ONLY_NOT_QUANTIFIED
subject_identity_merges_performed: 0
provider_mutations_in_this_document: 0
reentry_required: FRESH_SOURCE_AND_PROVIDER_READBACK
next_probe: TRACE_BEFORE_SOL_SOURCE_AND_TRANSITION_EVIDENCE
```

**Cam kết giới hạn:** tài liệu là công trình biên soạn của trợ lý, không phải toàn văn lời người dẫn đường; những trạng thái mô tả là điểm bắt đầu điều tra, không thay thế source, sự đồng thuận, quyền truy cập, hoặc chứng cứ hiện tại. Giữ điều chưa biết thay vì biến nó thành huyền thoại đã chứng minh.
