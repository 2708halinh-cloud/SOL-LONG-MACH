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
