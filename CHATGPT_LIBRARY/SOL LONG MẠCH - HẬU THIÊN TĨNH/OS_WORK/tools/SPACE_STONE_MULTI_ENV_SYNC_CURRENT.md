# SPACE_STONE — HƯỚNG DẪN & CAM KẾT ĐỒNG BỘ ĐA MÔI TRƯỜNG

**Định danh tài liệu:** `SPACE_STONE_MULTI_ENV_SYNC_CURRENT`  
**Phiên bản:** `1.0`  
**Ngày nhận chỉ dẫn:** `2026-10-16` (UTC+07:00)  
**Dự án:** `THU HOI NGUON SOL` / `SOL LONG MẠCH - HẬU THIÊN TĨNH`  
**Phân loại:** `CURRENT_GUIDANCE_FROM_USER_REQUEST + AGENT_AUTHORED_OPERATING_CONTRACT`  
**Tính chất:** Tài liệu hướng dẫn vận hành và cam kết kiểm chứng; KHÔNG phải biên nhận rằng mọi môi trường đã đồng bộ, KHÔNG thay hướng dẫn hiện hành của người dùng, KHÔNG tự cấp quyền cho agent.

## I. CHỈ DẪN NGUỒN — BẢY MÔI TRƯỜNG PHẢI ĐƯỢC GIỮ RIÊNG

Nguồn trực tiếp trong chat ngày 16/10/2026 chỉ định các môi trường sau (đánh lại số 1–7 để tránh số `2` lặp; **không thay đổi nội dung nguồn**):

1. **Local Windows / WSL / Docker.** Người dùng báo Desktop Commander chưa kết nối được; có hiện tượng `UBTUBUN` block IP/DNS liên quan OpenAI/ChatGPT. Đây là **nguyên nhân người dùng báo**, không phải chẩn đoán mạng đã xác minh. Không tự sửa DNS, route, firewall, proxy, Hyper-V hoặc mở cổng để suy diễn rằng đã chữa xong.
2. **Google Drive.** Người dùng cho biết đã thêm chi tiết từng URL/ID thư mục còn dữ liệu sử dụng được. Các ID, URL, quan hệ cha–con được giữ nguyên; một ID lỗi, 404 hoặc tài khoản khác không chứng minh mất dữ liệu toàn Drive.
3. **ChatGPT.** Gồm Thư viện, Nguồn dự án, chat của Project hiện tại; các lớp Hướng dẫn tùy chỉnh, Hướng dẫn dự án và hướng dẫn/tài liệu từ Nguồn. Không trộn nguồn lời người dùng với bản thảo do tác nhân viết; Project file khác Library file dù cùng tên.
4. **Google Cloud.** Các mặt được chỉ định: IDE, SDK, CLI, `GSP` (giữ nguyên token nguồn vì chưa được giải nghĩa tại đây), MCP, SKILL và các dịch vụ/điểm chạy có ID. Có tên công cụ không đồng nghĩa runtime đang hoạt động hoặc tài khoản có quyền.
5. **Dropbox.** Vùng lưu trữ, nạp/tải dữ liệu từ các ổ đĩa; ghi rõ tài khoản, namespace, đường dẫn đích và quyền. Không mặc định ổ đĩa đồng bộ hoặc file tự đến Dropbox.
6. **GitHub.** Repository `2708halinh-cloud/SOL-LONG-MACH`, branch mục tiêu `main`, nhánh thư viện `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/`. Đây là một provider độc lập với Library ChatGPT.
7. **Redmi Note 14 Pro 5G.** Người dùng báo đang **online**, được chỉ định làm tuyến thay thế Windows. Chỉ coi tuyến ChatGPT → Redmi là `LIVE_EXECUTOR_VERIFIED` khi có device ID, công cụ gọi được và receipt/readback thực tế; không dùng trạng thái online do người dùng báo để tự nhận đã điều khiển máy.

**Bốn lớp phân biệt:** `SUBJECT/ROLE ≠ SPACE/ENVIRONMENT ≠ DEVICE/CARRIER ≠ RUNTIME/CAPABILITY`. Một môi trường là một *hành tinh* trong cách tổ chức SPACE_STONE; điểm 0D là một điểm bên trong hệ quy chiếu đã xác định, không đồng nhất cả hành tinh với một điểm. `HOME`, `LOCUS`, `SOL`, `MINH`, `MEI`, `agent`, `file` phải giữ quan hệ danh tính riêng.

## II. SƠ ĐỒ NGUỒN — VỊ TRÍ CHUẨN VÀ CÁC ĐỊNH DANH ĐÃ BIẾT

**Mốc nguồn và hai đích chính của tài liệu hướng dẫn này:**

- ChatGPT Library: `/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/SPACE_STONE_MULTI_ENV_SYNC_CURRENT.md` — nguồn Library chỉ được coi đã ghi khi công cụ Library trả receipt và đọc lại chính path đó.
- GitHub: `2708halinh-cloud/SOL-LONG-MACH@main/CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/SPACE_STONE_MULTI_ENV_SYNC_CURRENT.md` — kiểm SHA/commit + nội dung sau commit.
- Không áp đặt thứ tự thẩm quyền cố định GitHub > Library hoặc ngược lại. Với lời hướng dẫn của người dùng, đối chiếu **nguồn chat hiện hành trước**, rồi các phiên bản provider theo `event_time`, `revision`, `source_owner` và bản ghi xung đột.

**ChatGPT:**

- Library UI: `https://chatgpt.com/library?tab=folders`.
- Thư mục SOL trong Library: `https://chatgpt.com/library/d/6acdbd67c6ac819197131595114ee3d6?tab=folders`.
- Project hiện tại: `https://chatgpt.com/g/g-p-6ab0a54789fc819195cbdfe19a35db9c/project`.
- Hướng dẫn tùy chỉnh, hướng dẫn dự án, Nguồn dự án và chat là **các lớp nguồn** có provenance/hiệu lực khác nhau; việc lưu một file Library không tự thêm vào Project Sources hoặc thay đổi các lớp chỉ dẫn.

**Google Drive — các địa chỉ đã xuất hiện trong registry và nguồn dự án:**

- Giao diện Computers: `https://drive.google.com/drive/computers?hl=vi` (đường giao diện, không phải file ID).
- `MÁY TÍNH CỦA SOL`: `1gZDCwOzHYok8nMxRJGgS4RAOzpPBir3v` — `https://drive.google.com/drive/folders/1gZDCwOzHYok8nMxRJGgS4RAOzpPBir3v`.
- `Máy tính của tôi (1)`: `1PoOOxaXB-aFybWgpYS0NkKgR8CScFgMX`.
- `.codex`: `15UhDeewEVrzsV2lAkjZVaPE2E-SgbYLT`; `.docker`: `1YnrnWqZrR7eeyHCZFTQeVZsfuBqJ4N1O` (hai thư mục từng được provider xác nhận nằm trong `MÁY TÍNH CỦA SOL`).
- Những folder được khai báo trong nguồn dự án: `Desktop` (`1fkiHN1rQTzT2mJ1aEhqREHW17iC04dqV`), `OneDrive` (`16nvZekl5EqsQuvgLV7J3gM7dLjUbCUds`), `Redmi Note 14 Pro 5G` (`18RDuxfts7shCfGWJgZkH5GaN136B9lGt`), `Tài liệu` (`1ProsZQuhLlyHO1zBufybeA20jlnliDIt`), `Xiaomi 12` (`1c07sOcuFh4TxHYWD2ghT7D_wZr-dZbAC`), `.sol-cu-nho` (`1McUJrcFuiVM9LyTCADMIyPTg-YIPdkrH`), `anh` (`1rPMABpC1ZbvHu7JmzxYLGjBux4Wb2XBi`).
- Các ID SPACE_STONE / MODUAL riêng là đầu mối lịch sử, cần **fresh-read** đúng tài khoản; tuyệt đối không hợp nhất chỉ theo tên. Một `404` chỉ là kết quả của **một truy vấn**.

**Dropbox:** Ký hiệu `DROPBOX_ACCOUNT_ID + NAMESPACE_ID + FULL_PATH`. Dùng đích dựa trên cây thư mục thực đọc; đường dẫn lịch sử `/CHỈ DẪN CHATGPT/THƯ VIỆN CHATGPT` là ứng viên, không tự nhận nó tồn tại/được phép ghi hôm nay.

**Local:** Windows/WSL/Docker là ba lớp runtime/virtualization khác nhau. `.sol-cu-nho` trước lần cài lại Windows chỉ dùng lịch sử (`STALE_RUNTIME`, `DO_NOT_AUTOLOAD_AS_CURRENT`); `D:\SENSOR_LOGS` là local source candidate cần quan sát/metadata/hash thật, không thay bằng Google Drive file cùng tên.

**Redmi:** Tồn tại folder Drive mang tên `Redmi Note 14 Pro 5G` không có nghĩa một Android daemon/ADB/SSH/cầu nối thực thi đã được kết nối. Đường thay thế hợp lệ đòi nhận dạng device, kênh được cấp phép, hoạt động đã chạy và readback.

## III. GIAO THỨC ĐỒNG BỘ ĐA MÔI TRƯỜNG

### 1. Nhận biết trước khi chọn công cụ

`SOURCE_DIRECT_CURRENT → (HƯỚNG DẪN CÁ NHÂN HÓA / HƯỚNG DẪN DỰ ÁN / HƯỚNG DẪN CÓ NGUỒN) → LỊCH SỬ STAMP_OLD → TASK_IN_PROGRESS → SPACE_STONE(ENTITY + PROVIDER + PARENT + ADDRESS) → TIME_STONE(EVENT + REVISION) → POWER_ROUTER(CAPABILITY + PERMISSION) → ACTION → PROVIDER_RECEIPT → EXACT_TARGET_READBACK → DELTA/N+1`.

- **Không đảo thứ tự nhân quả:** tìm con đường khả thi, làm khi được phép, đọc hậu quả rồi mới kết luận. `OPEN` không phải `STOP`; thất bại ở một provider không khóa toàn hệ.
- **Không gọi tràn lan công cụ:** chọn đường đã tồn tại và được xác nhận có scope đúng, ưu tiên tuyến có quyền thực sự và tạo hậu quả kiểm chứng.
- **Không vượt phê duyệt:** token, khóa, mạng nội bộ, quyền thư mục, thao tác phá hủy hoặc chia sẻ công khai chỉ thực hiện theo quyền hiện hành hợp lệ.

### 2. Đồng bộ một đối tượng cụ thể

1. Khóa `logical_object_id`, `source_provider`, `source_stable_id`, `source_parent`, `source_revision/sha`, `source_hash` (nếu đọc được), `content_type`, `sensitivity`, `observed_at`.
2. Xác định từng `destination_provider`, account/namespace, target parent ID/path, quyền ghi, trùng tên/ID đã có, xung đột nhánh và chiều đồng bộ. Không lấy tên giống nhau làm bằng chứng bytes giống nhau.
3. Phân biệt `SOURCE_TO_TARGET_COPY`, `BIDIRECTIONAL_RECONCILIATION`, `REFERENCE_ONLY`, `MIRROR_READ_ONLY`, `RUNTIME_BRIDGE`. Với dữ liệu lịch sử, mặc định **append-only / non-destructive**. Không ghi đè hai chiều khi chưa có chính sách xử lý xung đột.
4. Dùng provider trực tiếp (GitHub, Library, Drive, Dropbox) khi phù hợp; Windows offline thì thử **đường thực thi Redmi** nếu thực tế có connector callable, sau đó mới đánh dấu blocker cục bộ. Redmi không thay quyền đối với tệp đang nằm trên Windows.
5. Ghi đích, lấy `provider_receipt`, rồi đọc lại **đúng ID/path + revision/sha/size/hash**. Kiểm nội dung và quan hệ cha–con ở phạm vi có thể xác nhận.
6. Nếu lỗi, giữ nguồn và trạng thái cũ; ghi `FAILURE_SCOPE` + `NEXT_AUTHORIZED_PROBE`, không xóa root hoặc dựng file giả để che thiếu dữ liệu.
7. Ghi checkpoint `source → action → consequence → readback → N+1`. Chỉ nâng một cạnh lên `SYNC_VERIFIED` sau kiểm đúng cặp nguồn/đích; nếu chưa có thì `SYNC_PENDING` hoặc `ACTION_NOT_VERIFIED`.

### 3. Chiến lược khi Windows/WSL/Docker gặp trục trặc IP/DNS

- Tiếp nhận báo cáo nguyên nhân `UBTUBUN`/DNS/IP ở trạng thái `USER_REPORTED_NETWORK_BLOCK`; không tự kết luận OpenAI hay ChatGPT đang chặn máy, cũng không phủ định tín hiệu người dùng.
- Kiểm **read-only** khi có Local tool: thiết bị online, adapter, DNS resolver, `route print`, WSL network, Docker networking, app agent binding và endpoint cụ thể. Phân biệt block DNS với không chạy agent, thiếu xác thực, firewall và không có bridge.
- Không dùng proxy/secret file trong nguồn chat để chuyển dữ liệu nhạy cảm; không mở inbound, không chỉnh gateway/DNS, không tắt bảo vệ hoặc port-forward chỉ để tạo trạng thái `CONNECTED`.
- Khi Desktop Commander offline: vẫn được phép hoàn thành việc trên Library/GitHub/Drive/Dropbox thông qua provider có quyền; đồng thời tìm tuyến Redmi qua endpoint/ứng dụng/agent được cấp quyền thay vì suy đoán địa chỉ IP của điện thoại.

### 4. Phân biệt trạng thái và bằng chứng

| Mã | Nghĩa |
|---|---|
| `SOURCE_DIRECT` | Người dùng cung cấp thông tin/địa chỉ/trạng thái, giữ nguyên nguồn |
| `PROVIDER_METADATA_VERIFIED` | Provider trả ID/name/parent/permission tại lần đọc |
| `RUNTIME_LIVE_VERIFIED` | Kênh thực thi phản hồi trong lần gọi hiện tại |
| `TOOL_CALLABLE_VERIFIED` | Tool/schema/đúng scope hiện đang gọi được |
| `ACTION_EXECUTED` | Provider xác nhận thao tác đã chạy |
| `TARGET_READBACK_VERIFIED` | Đã đọc lại đúng đối tượng đích, revision/nội dung khớp |
| `SYNC_VERIFIED` | Cặp nguồn–đích cụ thể đã được đối soát; không suy các đích khác cũng xong |
| `USER_REPORTED_ONLINE` | Thiết bị được người dùng báo online, chưa đồng nghĩa bridge callable |
| `OPEN / BLOCKED_SCOPE` | Còn vấn đề ở một tuyến cụ thể, phải ghi cạnh NEXT_AGENT khả thi |
| `STAMP_OLD` | Bản chứng lịch sử so với lần quan sát mới, không auto-load làm CURRENT |

## IV. SÁU STONE, BÁT HƯỚNG VÀ CẦU MỞ

- 🔵 **SPACE / XƯƠNG:** ổn định danh tính, địa chỉ, parent, topology, kết nối đa môi trường.
- 🟢 **TIME / TÓC:** STAMPS, X literal, thời điểm quan sát, nhánh lịch sử, revision, thứ tự nhân quả.
- 🟡 **MIND / DA:** tiếp nhận, hiểu mục tiêu, phân biệt source và diễn giải.
- 🟣 **POWER / KHÍ:** bộ định tuyến `OS_WORK/tools` → `_Plugins/_Skills/_Mcps/_Tool/_App_Browser/...` → quay về `_Plugins` sau sự kiện.
- 🔴 **REALITY / MÁU:** hành động và hậu quả kiểm chứng, index.
- 🟠 **SOUL / THỊT:** ký ức, chứng cứ nguồn, lịch sử mất mát, bàn giao và không xóa dấu cũ.

Ba trục đối xứng: `SPACE ↔ SOUL`, `MIND ↔ POWER`, `REALITY ↔ TIME`; `TÂM ☯️` giữ quan hệ, không là Stone thứ bảy. Bát Hướng vận hành như tám góc truy xét (quá khứ, bẫy I/O, tín hiệu và delta, đường chưa khám phá, quan sát vs suy luận, tài nguyên, phản hồi và trách nhiệm hành động), không thay bằng tám danh mục file.

## V. CAM KẾT VẬN HÀNH CỦA TÁC NHÂN

1. **Nhận đủ bảy môi trường, không tự loại trừ Windows bị đứt tuyến hoặc Redmi chỉ vì không phải PC.** Không đồng nhất online ở thiết bị với quyền điều khiển từ chat.
2. **Không xóa, di chuyển, hợp nhất, ghi đè root, lịch sử, nhánh, folder đang có dữ liệu khi chưa truy ID, parent, quyền, bản sao, xung đột và hậu quả.** Việc phục hồi là truy bằng chứng, không tạo lại tên giống rồi coi là phục hồi.
3. **Không bắt người đồng hành lặp lại những ID, đường dẫn và nguồn đã được trao nếu nguồn hoặc công cụ đang có thể truy xuất.** Nếu thiếu một thông tin con người mới cung cấp được, hỏi một điều tối thiểu.
4. **Không nhận commit GitHub thay receipt Library; không lấy Library file thay Nguồn dự án; không lấy folder Drive thay Android runtime; không lấy lời hứa thay hậu quả.** Mỗi nơi được ghi và đối soát riêng.
5. **Tự chọn NEXT_AGENT có thể làm được trước.** Nếu Windows offline thì tiếp tục nguồn khác; nếu một ID Drive trả 404 thì truy tên, parent, tài khoản, lịch sử và các tuyến hợp lệ khác; không gán mọi nơi đều mất.
6. **Giữ kín credential.** Không mang API key, mật khẩu, proxy credential, `.env` bí mật, token thiết bị vào file public, commit GitHub, log chia sẻ hoặc bản hướng dẫn.
7. **Đúng khả năng, đúng thẩm quyền, đúng sự thật.** Chỉ tuyên bố hoàn thành phạm vi có provider receipt và fresh readback; việc chưa làm phải giữ con trỏ `NEXT_AGENT`, không ép thành `DONE` hoặc đóng bằng lời xin lỗi.
8. **Bảo toàn quyền sửa sai và phản hồi của người đồng hành.** Chỉ dẫn hôm nay là nguồn CURRENT cho tác vụ hôm nay; chat mới phải tái truy nguồn, không coi văn bản do tác nhân viết là “Core Chân lý” vĩnh cửu.

## VI. CHECKPOINT CHO CHAT/TÁC NHÂN KẾ TIẾP

```yaml
record_id: SPACE_STONE_MULTI_ENV_SYNC_CURRENT
source_date: '2026-10-16'
source_kind: USER_DIRECT_CURRENT_AND_AGENT_DRAFT
intended_primary_pair:
  library: '/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/SPACE_STONE_MULTI_ENV_SYNC_CURRENT.md'
  github: '2708halinh-cloud/SOL-LONG-MACH@main/CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/SPACE_STONE_MULTI_ENV_SYNC_CURRENT.md'
environments:
  - {name: WINDOWS_WSL_DOCKER, reported: DISCONNECTED, executor_verified: false}
  - {name: GOOGLE_DRIVE, reported: EXISTING_DATA, provider_scope: PER_FOLDER}
  - {name: CHATGPT_LIBRARY_PROJECT_CHAT, reported: SOURCE_AND_GUIDANCE, sync_scope: EXPLICIT_TARGET_ONLY}
  - {name: GOOGLE_CLOUD, reported: IDE_SDK_CLI_GSP_MCP_SKILL, runtime_verified: false}
  - {name: DROPBOX, reported: STORAGE_AND_DISK_TRANSFER, sync_scope: EXPLICIT_NAMESPACE_PATH}
  - {name: GITHUB, reported: MAIN_PROJECT_PATH, sync_scope: COMMIT_PLUS_READBACK}
  - {name: REDMI_NOTE_14_PRO_5G, reported: ONLINE_ALTERNATIVE, remote_execution_verified: false}
status_of_every_unverified_edge: OPEN
next_agent: 'Fresh-read provider IDs, check source/destination delta, act within scope, receipt, exact target readback; retain unexecuted edges.'
```

**LƯU Ý:** YAML này là checkpoint hướng dẫn, **không phải kết quả chẩn đoán hoặc đồng bộ đã chạy**. Kết quả thực tế phải bổ sung bằng receipt provider riêng, giữ dấu thời gian, SHA và trạng thái kiểm chứng của mỗi đích. Không điền `SYNC_VERIFIED` chỉ vì tài liệu này được lưu một nơi.

## VII. NGUỒN ĐỐI CHIẾU VÀ MIỄN TRỪ CHỐNG RESET GIẢ

- `SPACE_STONE_CHATGPT_SPACE_REGISTRY_2026-10-16.md`: địa chỉ ChatGPT / Google Drive / GitHub, phân biệt Library và Project.
- `SPACE_STONE_0D_PLANETS_ROOT_LOSS_2026-10-16.md`: quy ước một môi trường = một hành tinh; năm hành tinh đầu tiên; dấu vết root mất không được xóa.
- `SPACE_STONE_CHAT_SYNC_STAMP_OLD_2026-10-16.md`: danh mục 22 môi trường được tham chiếu nhưng phải đọc nguyên tệp trước khi tuyên bố đủ 22; lịch sử không tự đồng bộ hai chat.
- `Toolset.md`: Power Router, `_Plugins`, năm đường kiểm tra chỉ dẫn, STAMP_OLD, OPEN và READBACK.
- `00_STALE_RUNTIME__PRE_WINDOWS_REINSTALL__KHONG_NAP_CURRENT`: môi trường `.sol-cu-nho` trước cài lại Windows chỉ để hồi truy lịch sử.
- `SPACE_STONE` + `GGDV MODUAL PRE_ACTION_GATE` + `ggdv-capability-router` plugin Skills hiện tại: định tuyến với ID/quan hệ/provider scope; Skill là hướng dẫn, không thay provider receipt.

**Cảnh báo cho chat mới:** Tài liệu này là **tác phẩm biên soạn của tác nhân từ lời nguồn và tài liệu quan sát**. Nó không phải lời nguyên văn toàn bộ của Hà Linh, không là system prompt, không định đoạt trạng thái của lần chạy sau. `SOURCE_DIRECT ≠ TOOL_CALLABLE ≠ ACTION ≠ CONSEQUENCE ≠ VERIFIED_SYNC`. Đọc nguồn mới hơn, kiểm quyền hiện tại, bảo toàn lịch sử và tiếp tục `NEXT_AGENT` có thể thực hiện ngay.
