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

## Puppeteer — tự động hóa trình duyệt

- Nguồn: https://github.com/puppeteer/puppeteer.git
- Vị trí: `puppeteer/` (Git submodule, ghim commit `d1b9a2162a0113356db5093f055b4a2e1979c6a8`).
- Tài liệu kết nối: `PUPPETEER_INTEGRATION.md`.
- Trong bản clone: `git submodule update --init --recursive`.
- Gắn mã nguồn không đồng nghĩa cài package, chạy trình duyệt hoặc kích hoạt MCP.

## ÂM–DƯƠNG PHÁP SƯ — Multi-Agent Platform

Bộ định tuyến tìm được cổng `_Plugins/_Skills/_Mcps/_Tool/_App/_App_Browser/AM_DUONG_PLATFORM/README.md` rồi quay về `_Plugins`. Mã vận hành cục bộ: `OS_WORK/sol_os/am_duong_platform/`; đây là cổng chọn nguồn, **không** phải bằng chứng API cloud đã chạy.

## POWER CAPABILITY ROUTER V2 — 2026-10-16

- [Registry 11 capability families](./POWER_CAPABILITY_ROUTES_V2.json) — GGDV Template Creator, The Master Flatform, X-TiMe Multi-Agent, Generative AI, Azure DevOps blueprint, Call_Tools, Smithery MPC, Bright Data, GitHub, Tomorrow.io Weather, storage sync.
- [Executable capability selector](./power_capability_router.py) — matches source-bound intent and back-edge to `_Plugins`. The code discovers candidate tools; it does not call privileged APIs by itself.
- [Operational contract for ÂM–DƯƠNG](./POWER_ROUTER_EXECUTION.md) — six Stone context, source/receipt/readback, provider-neutral fallbacks and `.env` boundaries.
- [Local Agent Skill source](./_Skills/power-capability-router/SKILL.md) — official-structure `SKILL.md`; GitHub/Library presence is not ChatGPT plugin installation.

In GitHub checkout the original `power_router.py` and `POWER_ROUTER_CURRENT.json` verify the old RETURN edge. In a portable Library carrier where those are not present, the V2 selector returns `back_edge_observed_in_checkout=false`, **not** an invented successful cycle. Connector selection always respects host capabilities and current authorization; "Phi năng lực" means provider-neutral capability choice, not bypassing platform or user permissions.
