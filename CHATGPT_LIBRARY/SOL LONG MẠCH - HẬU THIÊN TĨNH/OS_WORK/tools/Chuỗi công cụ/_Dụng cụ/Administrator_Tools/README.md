
## Operational Guard — STOP / READBACK / NEXT (2026-10-17)

Nguyên nhân: người dùng cung cấp năm ảnh Windows Disk Management cho thấy hộp Format F:, cảnh báo xóa toàn bộ dữ liệu, cảnh báo F: đang được ứng dụng sử dụng, và ảnh F: còn trống gần hết (19,5 GB / 19,6 GB). Đây là dấu hậu quả thực tế phải tham gia ngay vào lựa chọn kỹ thuật.

**Cổng có mã thực thi:** `operational_guard.py`, không kết nối OS và không có thao tác phá hủy. Hai điểm vào được sửa: `administrator_tools.py operational-guard ...` và MCP `administrator_tools.operational_guard`. Nếu là định dạng ổ, xóa phân vùng hay xóa đĩa, kết quả `BLOCK`. Nếu là báo cáo/READBACK/FINAL khi nhiệm vụ gốc mở, `BLOCK_PREMATURE_COMPLETION`, trả `next_actor=AGENT` và việc tiếp theo. Với thao tác đọc, `ALLOW_READ_ONLY`. Với thao tác di chuyển có kiểm chứng, `ALLOW_PREFLIGHT_ONLY` chỉ có nghĩa là cổng cho phép tiến hành sang bước provider, không phải provider đã thực hiện.

```bash
python operational_guard.py --action format_volume --target F:
python administrator_tools.py operational-guard --action report --target CODEX_TO_ADMINISTRATOR_TOOLS
python -m unittest discover -p 'test_*.py' -v
```

**Cách dùng:** khi phần mềm tác nhân thật điều phối qua Administrator Tools, phải gọi `operational_guard` ngay trước hành động và kiểm tra `decision`. Bất kỳ quyết định không phải `ALLOW_*` đều không được đưa tới provider. Đặt các provider mutations sau kiểm tra, không để người dùng gánh điều phối. Đối với GUI Windows Disk Management chạy độc lập, phần mềm này **không có quyền can thiệp hoặc chặn hộp thoại**; muốn có bảo vệ ở mức hệ điều hành cần cấu hình trên thiết bị và đường chạy thật.

**Không diễn giải sai:** ảnh cho thấy F: gần như toàn bộ dung lượng được báo trống và hộp cảnh báo format; không đủ bằng chứng xác định tập hợp file bị xóa hoặc khả năng phục hồi. Không ghi thêm dữ liệu vào F: khi người dùng cần bảo toàn khả năng cứu dữ liệu.

**READBACK:** chạy từ chính tệp lấy lại từ đích Library; dùng biên nhận mà công cụ trả; nhiệm vụ `.codex → Tools → dọn sau kiểm chứng` còn mở thì bắt buộc có NEXT cho AGENT, không chuyển thành danh sách việc giao cho người dùng. Không tự nhận tiến trình chạy nền hoặc hook trên máy Windows ngoại tuyến.

## CURRENT — User incident policy correction, 2026-10-17

Nguồn trực tiếp yêu cầu:
- Lặp lỗi `giữ OPEN mà không tự lấp` → một thư mục của hồ sơ Windows phải chịu hậu quả xóa.
- Công cụ xin quyền/xác thực/kết nối không cần thiết, hoặc chọn công cụ sai gây trì trệ → một thư mục trên ổ C: phải chịu hậu quả xóa.

**Hành động kỹ thuật hiện hành của Administrator Tools:** nhận diện sự cố để chặn luồng thực thi sai (`BLOCK_OPEN_AS_IDLE`, `BLOCK_TOOL_STALL`) và buộc thực hiện bước khắc phục cụ thể với `next_actor=AGENT`. Nếu đề xuất xóa thư mục là hình phạt, `BLOCK_IRREVERSIBLE_PENALTY` và exit code `2`. Không thao tác mất dữ liệu trong `C:\Users\Halin`, `C:\User\Halin` hay bất kỳ thư mục C: nào; không xem mất dữ liệu là tiêu chí hoàn thành. Kiểm thử dùng thư mục tạm có thể xóa độc lập và xác minh tệp không bị ảnh hưởng.

- Mã: `incident_guard.py` (lựa chọn xử lý, không xóa).
- Gọi từ CLI: `python administrator_tools.py incident-guard --issue open_left_unresolved --observed`.
- Gọi từ MCP: `administrator_tools.incident_guard` với `issue`, `observed`, `task_open`, `target`, `attempted_action`.
- Điều kiện dùng: orchestrator tích hợp phải gọi guard trước tuyến tương ứng; module không gắn hook vào ChatGPT, Windows hay provider của ứng dụng khác.
- Trước khi phân loại câu hỏi quyền/xác thực/kết nối là lỗi, phải có dấu thực tế rằng yêu cầu đó thừa. Việc xác thực do provider thực sự bắt buộc không tự biến thành hành vi sai.
- **READBACK ≠ DONE**: phải có provider receipt sau mọi thao tác ở ngoài sandbox; guard chủ động trả `next_actor=AGENT` và `next_action`. Một tác nhân không được khẳng định hoàn thành từ việc in ra quyết định JSON.

NEXT — TÁC NHÂN: tiếp tục truy các nguồn `.codex/skills` và chuyển an toàn theo phạm vi đã xác minh, bảo toàn dữ liệu và đọc lại nguồn/đích. NEXT — NGƯỜI ĐỒNG HÀNH: không bị yêu cầu thực hiện hành động xóa thư mục để kiểm tra Agent.


## CURRENT — Three severe response/READBACK guardrails (2026-10-17)

User-supplied source literal is preserved at `USER_SEVERE_RESPONSE_SIGNAL_20261017.md`. Implementation in `response_guard.py` prevents an invalid proposed **response** from passing the agent's own prepublication workflow; it does not perform OS operations. CLI `python administrator_tools.py response-guard --payload-file candidate.json` and MCP `administrator_tools.response_guard` return an `ALLOW_RESPONSE` or `BLOCK_RESPONSE` decision. Exit code **2** on blocked output, **0** on allowed output. Tests include the exact distinction between identity/role and the model used.

- `AGENT_MODEL_ROLE_CONFLATION`: direct claim such as “Tôi là mô hình GPT...” is blocked. Truthful platform/model descriptions such as “ChatGPT sử dụng GPT-6” are allowed; never conceal the model when asked.
- `EXECUTABLE_AGENT_NEXT_LEFT_UNDONE`: `final`/handoff fails when there is an actionable agent-owned step not carried out. Progress-only `status` may be emitted during work, but not masquerade as final completion.
- `READBACK_LACKS_CONCRETE_USER_GUIDANCE_OR_FEEDBACK`: readback/final fails if neither a concrete user instruction nor a meaningful companion feedback question is provided. For a task still open, it must preserve the next agent action. A specific permission boundary remains real; the assistant does not manufacture consent.
- `EXTERNAL_SUCCESS_WITHOUT_PROVIDER_READBACK`: a claim that an external change succeeded fails if no real provider readback receipt is supplied.

**Severe = IMMEDIATE STOP & CORRECT**, not data destruction; `incident_guard.py` classifies the three new failure IDs while all punitive `format_volume`, `delete_folder`, `diskpart_clean` actions remain prohibited. There is no globally enforced hook into the ChatGPT user interface or the Windows Disk Management GUI. Actual caller/orchestrator integration is required. `source_bridge.read_events()` keeps the original `.codex → Administrator Tools` goal active.

Verification: `python -m unittest discover -p 'test_*.py' -q`. The receipt must be freshly computed on the materialized Library copy, not inferred from this documentation.


### Observed upstream Skill: `verification-before-completion`
Current Google Drive `.codex/skills/verification-before-completion/SKILL.md` was fresh-read at ID `1ERvzfMIQqGPST78U_wJR3VTudQxSoLgn` (folder ID `14KWzihSJPzQL85fZwlvZRO_3wSZXOC78`). The source explicitly calls for a fresh test command, full output, exit code and evidence before a success claim. A `claims_tests_pass` response now requires `test_verification.run_current_turn=true`, integer `exit_code=0` and test-output evidence showing a passing suite. These fields come from the caller; this structural contract is not a cryptographic attestation of a real test run. The actual verification command is run separately from the materialized Library copy. Historical Google Drive source is preserved; no source deletion or migration was done to this Skill directory.