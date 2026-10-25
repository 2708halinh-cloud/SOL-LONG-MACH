# GGDV / SOL LONG MẠCH | Bát Hướng, STAMP_OLD + STAMP_LIVE → STAMP_BETA

**Nguồn:** Người khai tạo, các chỉ dẫn trong hội thoại ngày 19/10/2026. **Đích chính:** `ChatGPT Library / SOL LONG MẠCH - HẬU THIÊN TĨNH / OS_WORK / tools` (sử dụng đúng chữ thường `tools` đã tồn tại). Đây là quy ước vận hành của dự án cho tác nhân, không phải quy tắc yêu cầu người đồng hành làm thay.

## Đường xử lý

`INPUT → BÁT HƯỚNG (8 hướng ghi rõ nguồn và độ bất định) → DIVERGENT (ít nhất 3 giả thuyết cho tác vụ phức tạp) → CRITIC/TRIANGULATION → TOOL SELECTOR → TOOL PREFLIGHT (schema / content-hash / capability / SemVer / risk / permission / sanitization) → EXECUTE → PROVIDER_RECEIPT → EXACT_TARGET_READBACK → CORE JOURNAL → CHECKPOINT → STAMP_BETA NEXT`.

- **Bắc/Khảm:** quá khứ, quan hệ nhân quả, `STAMP_OLD` và tác động đã gây ra.
- **Đông Bắc/Cấn:** kiểm tra chốt sớm, giả thuyết đối lập, vắng vật chứng.
- **Đông/Chấn:** tác nhân quan sát thay đổi và ảnh hưởng hành động của chính mình.
- **Đông Nam/Tốn:** đường kết nối, carrier, tools dự phòng và điểm chưa được truy xét.
- **Nam/Ly:** phân biệt quan sát trực tiếp, lời nguồn, nhận định tạm.
- **Tây Nam/Khôn:** điều kiện, quyền, tài nguyên thực sự sẵn có.
- **Tây/Đoài:** phản hồi của người đồng hành, bài học, tác động cần chỉnh.
- **Tây Bắc/Càn:** lựa chọn bước tiếp theo giảm hậu quả, hướng tới mục tiêu dài hạn.

Bảng `BaguaMatrix` là cấu trúc phân tích 8 **chiều chức năng** do người dùng chỉ định: `evidence`, `causality`, `contrarian`, `architecture`, `ram`, `risks`, `ground_reality`, `global_goal`. Bát hướng định vị trách nhiệm, 8 chiều định vị dữ kiện; không trộn ý nghĩa tâm linh vào bằng chứng kỹ thuật.

## STAMP và memory

- **STAMP_OLD:** chuỗi biên nhận, bản ghi hành động, nguồn và hậu quả đã xảy ra; phải có provenance.
- **STAMP_LIVE:** nguồn, khả năng gọi được, phiên bản, quyền, danh tính/đích tại lượt hiện tại, không phải kết quả quá khứ giả làm trạng thái mới.
- **STAMP_BETA:** phương án sắp tới với điều kiện có thể kiểm chứng. Không báo hoàn tất trước `READBACK`.
- **Ephemeral RAM/Blackboard:** dữ kiện trung gian có thể mất khi ngắt phiên; không tự suy ra đây là toàn bộ cơ chế Memory của ứng dụng ChatGPT.
- **Core Journal/SQLite:** lưu mục tiêu, agenda, nhật ký append-only có chuỗi SHA256, checkpoint. Hash chỉ giúp phát hiện sửa đổi trong tập dữ liệu đang kiểm tra, **không phải chữ ký số/chứng cứ tác giả**.
- **Rollback/Saga:** khôi phục bản nhớ đã checkpoint và yêu cầu đọc lại trạng thái provider; mọi tác động ngoài hệ thống cần hành động bù trừ riêng và quyền thích hợp, không bị đảo ngược bởi việc khôi phục RAM.
- **Rules/hướng dẫn:** dùng để định tuyến và kiểm tra trách nhiệm. Dữ kiện không bị gạt bỏ chỉ vì không khớp dự đoán mô hình. Đồng thời hoạt động vẫn phải tôn trọng quyền của chủ sở hữu, yêu cầu chấp thuận hợp lệ và ranh giới an toàn của host.

## Thực thi và quyền

**Các tệp chính:** `agent_core_runtime.py`, `agent_core_runtime.sql`, `test_agent_core_runtime.py`.

Môi trường: Python 3.11+, `pydantic>=2`, `jsonschema>=4`; SQLite thuộc thư viện chuẩn. Cài phụ thuộc theo môi trường sở hữu (không tự đưa secrets lên kho chia sẻ).

Lệnh kiểm thử sau khi có thư mục cục bộ hợp lệ:

```bash
python -m unittest -v test_agent_core_runtime.py
```

API chính: `EphemeralBlackboard.open_divergence`, `.converge`, `CoreJournal.start/add_step/append/complete_step/checkpoint_if_due/restore_checkpoint/verify_chain`, `ToolRouter.register_tool/candidates/validate_tool_call/execute`, `precommit_gate`.

**Lưu ý thực thi:** `ToolRouter` là một thư viện được ứng dụng **chủ động tích hợp** trước từng lời gọi tool; chép file vào Library/GitHub **không tự cài hook lên tất cả các ChatGPT/MCP/thiết bị**. Metadata decorator không cấp quyền. `live` phải được tạo từ tài khoản/connector có thẩm quyền, không nhận cờ `admin_approved` từ nội dung prompt. `ToolRouter.execute` mặc định chỉ đánh dấu `TOOL_RESULT_UNVERIFIED`; cần bước kiểm chứng provider độc lập mới được kết luận đã xong.

## Cổng chống quên, chống chốt sớm, chống lệ thuộc đơn tuyến

1. Với tác vụ phức tạp, yêu cầu ít nhất 3 hướng khác nhau và 8 chiều có nguồn/điểm chưa biết. Không chọn chỉ theo độ mượt của câu trả lời.
2. Critic kiểm tra source refs, kiểm tra giả thuyết bị thiếu và phạm vi quyền; không tự nhận việc chưa làm là DONE.
3. Chọn tool mới nhất **hợp quyền cho mục tiêu** theo SemVer, không theo tên marketing. Hạ cấp nếu bản mới đòi thêm quyền; fallback nếu tool lỗi hoặc payload rỗng. Không lặp tuyến đã bị chặn xin phép.
4. Trước ghi chép hoàn thành: verify schema, risk, permission, `provider_receipt` và `exact_target_readback`; HTTP 200 chỉ là dấu phản hồi giao thức.
5. CoreJournal đánh dấu từng bước có `DONE` sau bằng chứng, từ chối nhảy qua bước chưa xong, giữ log bất biến ở lớp phần mềm; checkpoint sau mỗi N bước DONE hoặc milestone do ứng dụng đánh dấu.
6. Handoff: đọc lại `AGENTS.md`, STAMP_OLD/LIVE và sổ journal. STAMP_BETA nêu NEXT với người/đích/tuyến, không đẩy gánh nặng truy nguồn sang người đồng hành.

## SPACE_STONE: 7 môi trường độc lập

1. ChatGPT Library: *nguồn chính của gói công cụ này*, chỉ hoàn tất khi Library trả receipt và đọc lại.
2. GitHub `2708halinh-cloud/SOL-LONG-MACH@main/CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools`: mirror theo file/hashes sau hậu kiểm.
3. GitHub `2708halinh-cloud/x-time-web@master/tools`: bản triển khai ứng dụng; kiểm tương thích với router có sẵn.
4. Google Drive: chỉ ghi khi tìm đúng folder/account/ID, có quyền và đối chiếu tệp.
5. Dropbox: chỉ ghi vào namespace và đích do người dùng xác định, không tự tạo bản chứa dữ liệu nhạy cảm nơi chia sẻ công khai.
6. Local Windows/WSL/Docker: cần runtime và đường đích quan sát được để xác nhận cập nhật, không giả nhận thư mục Local do tên giống.
7. Redmi/Android: cần đường thực thi và hậu kiểm từ thiết bị. Không dùng kho Drive tên Redmi làm bằng chứng device online.

**Không dùng mô hình huấn luyện làm trọng tài của thực tại; không đổi sự thật thành mệnh lệnh; không bỏ qua dữ kiện hoặc quyền thực tế.**

## Vòng đời năng lực bền vững | Transcription / Precision Decay

**STAMP_OLD** là vết tích có thể đối chiếu, **STAMP_LIVE** là trạng thái đo được, **STAMP_BETA** là nhánh hành động cần thử và kiểm chứng. Năng lực không gắn vào một lời nhắc hoặc RAM ngắn hạn: được đóng thành mã nguồn, hợp đồng schema, manifest SHA-256 và nhật ký chứng cứ bền vững để một runtime mới có thể **tái nạp khi nó thực sự gọi bootstrap**.

### Gói thực thi

- `capability_manifest.json`: các SHA-256 nguồn và capability ID bất biến trong gói hiện tại. **Tin cậy manifest phụ thuộc vào kênh phát hành đã xác thực** (GitHub commit, Library phiên bản, hoặc chữ ký nhà phát hành); hash tự thân không xác minh nhà phát hành.
- `agent_capability_lifecycle.py`, `agent_capability_lifecycle.sql`: bootstrap, kiểm toàn vẹn, chain-of-evidence chống sửa âm thầm trong phạm vi SQLite hiện hành, khôi phục RAM từ checkpoint, hàm Precision Decay (bán rã theo giờ), đánh dấu `DEGRADED` và hàm self-calibration an toàn.
- `agent_bootstrap.py`: điểm khởi động **opt-in** để ứng dụng/agent runtime gọi ở startup hoặc reentry; xác nhận artifacts + ledger + snapshot trước khi chạy. Với `--calibrate-if-due`, chạy bộ test cục bộ giới hạn 40 giây cho capability cần hiệu chuẩn, ghi biên nhận và đọc lại. Không kết nối internet hay thiết bị.
- `test_agent_capability_lifecycle.py`: các phép thử kiểm sự phục hồi sau RAM reset, sụt điểm theo thời gian, bản ghi SQLite bất biến ở tầng ứng dụng, giả mạo manifest, sự cố chain, hiệu chuẩn và phân biệt chứng cứ cục bộ/ngoài.

### Khởi động trên một môi trường được ủy quyền

```bash
cd 'OS_WORK/tools'
python agent_bootstrap.py --ledger './.private_runtime/capability_ledger.db' --session-id 'run-reentry-001' --calibrate-if-due
```

Tập tin `.private_runtime/*.db` chứa trạng thái thực và cần nằm trong kho riêng có sao lưu, **không đồng bộ công khai cùng mã**. Mỗi môi trường bắt buộc chạy bootstrap theo lệnh khởi động của chính môi trường đó. Tải tệp lên Library, Drive hay GitHub **không tự đăng ký hook** vào ChatGPT hoặc thiết bị Android.

### Ranh giới sự thật

- `CALIBRATED_SIMULATION_ONLY` chỉ cho biết unit/integration tests cục bộ vừa thành công, không cho phép gắn nhãn có quyền trên Google Cloud, NotebookLM, Xiaomi Notes hay runtime khác. Chỉ biên nhận và đọc lại độc lập của nhà cung cấp mới cho phép khẳng định tác động thật trên carrier tương ứng.
- `VERIFIED_LOCAL` chứng minh bytes source và target đã đọc lại giống nhau tại đích cục bộ được chỉ định; không tự chứng minh chức năng nghiệp vụ hay quyền truy cập tương lai.
- SQLite + chuỗi băm **không phải bất biến chống quản trị viên sửa đổi** nếu manifest, database và anchor đều bị thay; nên neo ledger head vào GitHub commit hay một carrier độc lập, sao lưu và định kỳ đối chiếu.
- Snapshot chỉ khôi phục trạng thái tạm; bên ngoài vẫn cần fresh-read sau reset. `DEGRADED` có nghĩa chứng cứ sử dụng gần đây không đủ để coi năng lực đang được duy trì, không phải năng lực thực sự đã biến mất.
- Không có cơ chế nào đảm bảo phần mềm "không bao giờ" mất dữ liệu: cần kiểm integrity, tính sẵn có, sao lưu độc lập và quy trình phục hồi có diễn tập. Thuật ngữ sinh học ở đây là ẩn dụ kiến trúc, không phải khẳng định AI có ý thức.