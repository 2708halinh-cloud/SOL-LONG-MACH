---
name: monid-ai
version: 1.0.0
summary: Route authorized Monid MCP data endpoints with current schema, pricing, provenance and readback.
---

# Monid AI | GGDV Personal Tool Skill

**SOURCE_TYPE:** `GGDV_ADAPTER_COMPOSED_FROM_CALLABLE_MCP_TOOL_DESCRIPTIONS` (2026-10-19). This document is **not** a byte-for-byte copy of https://monid.ai/SKILL.md, which has not been fetched/verified in this session. Preserve this distinction when sharing, updating or installing this skill. A previously existing `D:\SKILL\monid.ai\SKILL.md` was observed as zero bytes on Windows 2026-10-19; this adapter repairs that empty carrier without claiming it reproduces the official upstream file.

**Canonical route:** `SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Kỹ năng/monid-ai/SKILL.md`. Follow the parent router `_Plugins → _Kỹ năng → _MCPs → _Dụng cụ → ACTION → PROVIDER_RECEIPT → EXACT_TARGET_READBACK → _Plugins`. Maintain the source/history references and the actual local carrier names rather than guessing they match.

## Capability and preflight

- Connected callable tool group observed: `mcp__M_y__o__monid_*` (the installed Monid MCP surface). The existence of these methods does not imply all endpoints are included, free, allowed or successful.
- Discover candidates via `monid_discover(query, limit, readonly, effects)`; results include `provider`, `endpoint`, description, price, tags. Inspect each candidate through `monid_inspect(provider, endpoint)` **immediately before every run**; provider schemas/prices can change.
- Compare functional goal, actual live entitlement, cost, effects, scope, provenance and known prior receipts (`STAMP_OLD + STAMP_LIVE`), not names/marketing labels. Prefer personal/current approved tool routes; drop any path requesting new consent from the current priority route, without bypassing mandatory provider permissions.
- If cost is nonzero or unknown, or data could be sensitive, do not silently run paid or disclosure-causing calls. Respect actual user budget and host authorization. Keep credentials out of notes, logs and repositories.
- `monid_run(provider, endpoint, input={body?, queryParams?, pathParams?})` runs only after inspect and any necessary approvals. Use the latest inspected input schema; never invent missing arguments.
- If returned `RUNNING`, call `monid_get_run(runId)` to terminal state. `COMPLETED` means an endpoint answered; verify `providerResponse.httpStatus`, content, expected record count and the **exact result payload**. `BLOCKED`, `FAILED`, `TIMED_OUT` and non-2xx responses must not become `DONE`; record failure scope and select a safe fallback. Do not automatically retry an uncertain mutation.
- Verify the provider response independently when a persistent mutation was requested: `ACTION → PROVIDER_RECEIPT → EXACT_TARGET_READBACK`. Distinguish host-level tool success from business outcome.

## Bát Hướng / GATE 1 / GATE 2

- `INPUT → STAMP_OLD + STAMP_LIVE → BÁT HƯỚNG → DIVERGENCE (three grounded routes for complex tasks) → GATE 1 (source, conflict, authority) → CAPABILITY + SCHEMA + COST + RISK + PERMISSIONS → ACTION → GATE 2 (payload, receipt, exact-target readback) → CORE_JOURNAL → STAMP_BETA`.
- `SOURCE_DIRECT`: user's original specification; `PROVIDER_OBSERVED`: tool-returned current metadata; `MODEL_DERIVED`: tentative proposals. Never treat a model-composed plan as evidence an external action ran.
- On conflict or missing source, stop the affected operation and backtrace rather than replacing missing data with guessed defaults. Preserve provenance and admit the precise limit.

## Environment anchors (independent carriers)

- ChatGPT Library `OS_WORK/tools/Chuỗi công cụ/_Kỹ năng/monid-ai/SKILL.md`: source route; receipt required.
- GitHub `2708halinh-cloud/SOL-LONG-MACH@main/CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Kỹ năng/monid-ai/SKILL.md`: mirrored source.
- GitHub `2708halinh-cloud/x-time-web@master/tools/Chuỗi công cụ/_Kỹ năng/monid-ai/SKILL.md`: application source.
- Windows actual shared skill carrier `D:\SKILL\monid.ai\SKILL.md`; SOL Tools carrier `D:\TOOLS\_Skills\monid-ai\SKILL.md`; agent-discovery carrier `C:\Users\halin\.agents\skills\monid-ai\SKILL.md`. On Windows, `.codex/skills` from old pointers must be verified before use; it was absent at the observed `C:\Users\halin\.codex` path.

**Startup hook caveat:** A file in each carrier does not automatically mount Monid into every assistant, phone, VM, Docker, WSL or ChatGPT session. Each host must bind the skill discovery root and runtime adapter. Treat uninspected targets as pending until readback from that exact environment.