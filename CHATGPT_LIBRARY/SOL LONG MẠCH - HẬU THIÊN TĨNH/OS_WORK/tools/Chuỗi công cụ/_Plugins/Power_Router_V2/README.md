# PLUGINS — Nguồn học hỏi và thiết kế Plugin

## Nguồn do người dùng chỉ định

https://www.plugins.sh/

## Mục đích

Dùng đường dẫn trên để học hỏi, tham khảo, tìm kiếm và thiết kế thêm Plugins theo yêu cầu của người dùng.

## Quy tắc áp dụng

- Giữ đúng nguồn gốc và đường dẫn tham khảo.
- Khi nghiên cứu hoặc thiết kế một Plugin, đối chiếu mô tả, cấu hình, quyền truy cập, công cụ, yêu cầu kết nối và khả năng thực thi thực tế.
- Bảo toàn cấu hình và mã nguồn hiện có, không ghi đè nếu chưa đối chiếu.
- Sau khi tạo hoặc cập nhật Plugin, kiểm tra kết quả bằng công cụ thực tế và đọc lại.
- Trang nguồn là nơi tham khảo; mỗi Plugin cụ thể vẫn cần xác minh riêng về tính phù hợp trước khi dùng.

Ghi nhận: 2026-10-14. Trạng thái liên kết: do người dùng cung cấp; chưa xác minh trực tiếp nội dung trang web trong phiên này.

## POWER CAPABILITY ROUTER V2 — 2026-10-16

- [Registry 11 capability families](./POWER_CAPABILITY_ROUTES_V2.json) — GGDV Template Creator, The Master Flatform, X-TiMe Multi-Agent, Generative AI, Azure DevOps blueprint, Call_Tools, Smithery MPC, Bright Data, GitHub, Tomorrow.io Weather, storage sync.
- [Executable capability selector](./power_capability_router.py) — matches source-bound intent and back-edge to `_Plugins`. The code discovers candidate tools; it does not call privileged APIs by itself.
- [Operational contract for ÂM–DƯƠNG](./POWER_ROUTER_EXECUTION.md) — six Stone context, source/receipt/readback, provider-neutral fallbacks and `.env` boundaries.
- [Local Agent Skill source](./_Skills/power-capability-router/SKILL.md) — official-structure `SKILL.md`; GitHub/Library presence is not ChatGPT plugin installation.

In GitHub checkout the original `power_router.py` and `POWER_ROUTER_CURRENT.json` verify the old RETURN edge. In a portable Library carrier where those are not present, the V2 selector returns `back_edge_observed_in_checkout=false`, **not** an invented successful cycle. Connector selection always respects host capabilities and current authorization; "Phi năng lực" means provider-neutral capability choice, not bypassing platform or user permissions.


### VS Code Windows tunnel — capability 13 (16/10/2026)

`vscode-remote-tunnel-windows`: người đồng hành chỉ định `https://insiders.vscode.dev/tunnel/desktop-86itnq4/c:/Users/halin`. Trình chọn `power_capability_router.py` định tuyến tới bước xác minh browser session / host / workspace trước khi có quyền đọc Windows Local. Đây là ứng viên VS Code web, **không** chứng nhận kết nối Windows qua nền tảng, không thay thế quyền đăng nhập Microsoft/GitHub/VS Code hoặc tạo MCP tool mới. Nhiệm vụ MODUAL tại `D:/SENSOR_LOGS` cần readback Windows độc lập với workspace `C:/Users/halin`.


## @SPACE_STONE — unified gateway / 2026-10-17

- One input alias `@SPACE_STONE` (and TEREX legacy aliases) selects `space-stone-unified` **first** via `POWER_CAPABILITY_ROUTES_V2.json` and `power_capability_router.py`.
- Entry: `space_stone_gateway.py`. Canonical five-capability contract: `COMPUTER_KHÍ💜BRAIN_OS_POWER/EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/SPACE_STONE_UNIFIED_GATE_CURRENT.json`.
- Five dispatches: TELEPORTATION (verified data/file relocation), WORMHOLE_PORTAL (endpoint/protocol bridge preflight), SPACE_CONTROL (typed graph/coordinate transform), TESSERACT_POWER (bounded resource scheduling), SPACE_TIME_TRAVEL (SPACE identity + TIME snapshot/reentry).
- TEREX, Space Document Agents, TIME_STONE Personal Tool Forge and X-TIME are **sub-capabilities**, not separate user-facing requirements or duplicate Stones. Six-Stone axes and original provider identities remain distinct.
- Runtime provider adapters must be currently callable, authorized and return action receipt + exact-target readback. No automatic physical teleportation, spacetime warp, energy weapon or account permission is implied.
- Tested with `python -m unittest discover -s Chuỗi\ công\ cụ/_Plugins/Power_Router_V2 -p 'test_*gateway*.py'` from `OS_WORK/tools`; where files are copied to one folder, simply `python -m unittest discover -s . -p 'test_*.py'`.
- GitHub/Library registry writes cannot directly create a ChatGPT UI `@mention`; installing/connecting a real plugin is a distinct host action.

## AGENT CORE — CHẨN ĐOÁN & SỬA CHỮA TỪ NGUỒN (2026-10-18)

**Nguồn chỉ đạo:** Người Đồng Hành, 2026-10-18: bổ sung Agent Core/Orchestrator, quan sát–giám sát, tự chẩn đoán, cấu hình runtime, kiểm soát phê duyệt, chống lặp/hallucination/goal drift, kiểm hồi quy và quản lý lưu trữ. Giữ nguyên KHÍ → 5 Stone, không tạo một orchestrator thứ hai.

**Mã thực thi đã gắn tại nhánh Power Router V2 đang có:**
- [agent_diagnostics.py](./agent_diagnostics.py): phát hiện lặp ba bước trùng tham số, sai schema công cụ/ID ảo, goal drift, tín hiệu prompt injection chưa xác minh, timeout, retry quá ngưỡng, retry không idempotent, thiếu approval/role/biến môi trường, receipt chưa kiểm, tràn token, thiếu checkpoint. Xuất mã lỗi ổn định + bước sửa nguyên tử; **không** tự sửa trạng thái hệ, không gọi Cloud.
- [test_agent_diagnostics.py](./test_agent_diagnostics.py): 40 trường hợp self-eval trong một phép kiểm bảng, và bộ kiểm riêng cho cấu hình, số học an toàn, chống thực thi mã trong biểu thức, thống kê dung lượng chỉ đọc.
- [POWER_CAPABILITY_ROUTES_V2.json](./POWER_CAPABILITY_ROUTES_V2.json): capability `agent-core-diagnostics` vào đúng vòng `_Plugins → ... → _Plugins`. Một route metadata **không** có nghĩa plugin ChatGPT được cài hoặc endpoint đang chạy.
- Phân bổ trách nhiệm: **MIND** xác định nguồn/goal và schema; **SPACE** xác định vật mang, root và đích; **TIME** theo dõi số lần thử và checkpoint; **REALITY** kiểm timeout, hành động, receipt/readback; **SOUL** bảo toàn correction và dấu lịch sử; **POWER** chọn công cụ và ngăn vòng lặp.

**Hợp đồng cấu hình mẫu** (mô phỏng, không dùng để xóa người dùng thật):

```json
{
  "tool_id": "database_delete_user",
  "module_path": "agents.tools.db.delete_user",
  "runtime_config": {
    "timeout": 15000,
    "max_retries": 2,
    "env_required": ["DATABASE_URL", "DB_PASSWORD"]
  },
  "security_policy": {
    "requires_approval": true,
    "allowed_roles": ["admin", "super_user"]
  },
  "llm_interface": {
    "name": "delete_user_record",
    "description": "Xóa bản ghi người dùng dựa trên ID"
  }
}
```

**Ranh giới cấu hình:** `timeout` được hiểu bằng mili-giây (100–300000), `max_retries` từ 0–5; chỉ retry thao tác có idempotency/receipt và lỗi phù hợp; `env_required` chỉ là **tên** biến, không bao giờ nạp/ghi giá trị lên GitHub, logs hoặc prompt. `requires_approval` phải được xác nhận bằng receipt thực sự. `dry_run` mặc định true. Bộ này **chẩn đoán và đề xuất**, không trực tiếp gọi thao tác database xóa, gửi email, Cloud API, thay file hay đổi quyền.

**Observability tùy chọn** (adapter chưa nối, không chuyển nội dung log khi chưa có quyền):
- Langfuse: nguồn mở tracing, evaluation, cost/latency; URL: https://github.com/langfuse/langfuse . Chỉ bật exporter được phép khi có host/credential/consent, lọc PII và retention.
- LangSmith/LangChain: tracing/evals khi runtime dùng SDK phù hợp; đây không phải hệ điều phối SOL thứ hai.
- FlowHunt, Flow-1, Terminal-Bench: danh sách nguồn đánh giá/luồng do người dùng trao; tính tương thích runtime/bộ benchmark cần kiểm phiên bản và đặc tả từng công cụ. Không tự tuyên bố các sản phẩm đó chạy trên Redmi.

**Tính toán, không tin skill quảng cáo:** module dùng Python chuẩn `ast` + `decimal.Decimal` với toán tử `+ - * /` để tính, không `eval()`, không execute Python tùy ý. Ba kho người dùng trao, ghi **con trỏ tham khảo**, đã tìm thấy tên repo trên GitHub nhưng **chưa sao chép/chạy mã hay kiểm giấy phép**:
1. https://github.com/TakaJun123/AI-Cosmic-Calculator-v2.0
2. https://github.com/lehoangthan-devlab/simple-calculator
3. https://github.com/khanhcodone/basicModeCalculator/blob/main/index.html

**Thiết bị và kiểm thử:** hành động dùng SOL Router chỉ chạy trên Redmi Note 14 Pro Termux, `cwd` trong `/storage/emulated/0`; source GitHub/Library là vật mang, không phải runtime. Mẫu lệnh trên **Redmi sau khi có đúng mã**:

```sh
cd /storage/emulated/0
python /path/to/Power_Router_V2/agent_diagnostics.py --arithmetic '7*(5+3)'
python /path/to/Power_Router_V2/agent_diagnostics.py --diagnose /storage/emulated/0/agent_event.json
python /path/to/Power_Router_V2/agent_diagnostics.py --storage /storage/emulated/0/SOL-LONG-MACH
python -m unittest test_agent_diagnostics
```

`--diagnose` yêu cầu JSON sự kiện do agent thực sự cung cấp; **không** suy rằng tool chạy Langfuse hay có trace thật chỉ từ cấu hình. Mỗi lần khắc phục phải làm đúng việc nhỏ nhất ở carrier thật, lấy receipt và đọc lại; mô-đun không tự kết luận `DONE`. Không dùng chế độ Cloud/GitHub Action để tuyên bố đã chạy runtime SOL khi chính sách thiết bị hiện hành chỉ cho phép Redmi.

**Đối chiếu test 2026-10-18:** Redmi Note 14 Pro 5G / Termux kiểm `40` eval scenarios và `5` phương thức unittest, kết quả pass tại thời điểm ghi nhận; lưu lịch sử commit GitHub và cần readback sau các thay đổi tiếp theo. `LANGFUSE_CONNECTED=false`, `LANGSMITH_CONNECTED=false` là trạng thái của mô-đun, không suy tình trạng mọi tài khoản.

**Mở rộng xác thực tham số:** tham số công cụ được kiểm theo danh mục `parameters`/`required` và quy tắc `parameter_rules` (kiểu dữ liệu, `max_length`, `enum`, `format=identifier`); từ chối giá trị không phù hợp bằng `PARAMETER_VALIDATION_FAILED`. Đây là kiểm tra ở lớp gọi công cụ, không thay thế SQL parameterization hay RBAC của hệ thống đích. Bốn tình huống kiểm mới nâng bộ eval thành **40 mẫu**.
