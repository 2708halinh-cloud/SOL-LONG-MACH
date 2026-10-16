# POWER ROUTER 2 — ÂM–DƯƠNG / X-TIME / GGDV / CALL_TOOLS

**Nguồn và quyền:** This is a SOL tool **orchestration contract**, not a new platform feature nor blanket authority to use every connector. Keep the existing `POWER_ROUTER_CURRENT.json`, `power_router.py`, `TOOLS_ROUTER_CURRENT.json` and `TOOLS_GROUP_INDEX_20261016.json` as source manifests. Route V2 **adds** observed candidates and a deterministic provider-neutral selector.

## Tại sao cùng ở trong Tools và quay về _Plugins?

`_Plugins → _Skills → _Mcps → _Tool → _App → _Other_Tools → _Plugins` is an **event cycle**, not a recursive symlink or infinite CPU loop. Each event has a unique ID and an end of pass; a new observation can create a new event N+1. The original back-edge is `_Plugins/_Skills/_Mcps/_Tool/_App/_Other_Tools/RETURN_TO_PLUGINS.json`. Protect against unbounded recursion with visited guard and per-event budget.

**DƯƠNG PHÁP SƯ**: human supplies goals, priorities, source, approvals when required, reviews important consequences. **ÂM PHÁP SƯ**: agent discovers sources, enumerates connected capabilities, selects an authorized operation, runs it when callable, preserves receipt and readback, and chooses the next concrete edge. The distinction is responsibility, not a claim of independent platform permissions. Human feedback does not become a substitute for independent readback, and an inaccessible provider is never treated as proof its resources were deleted.

## 6 Stones cross-flow

`MIND🟡 INPUT / source → REALITY🔴 INDEX / identity → SPACE🔵 exact provider ID/path → TIME🟢 STAMP_OLD/LIVE/BETA → POWER🟣 candidate tool + action → SOUL🟠 history, event, readback → REALITY🔴 observed delta → _Plugins → N+1`.

Keep **SOURCE_DIRECT, SOURCE_FILE_ID, SOURCE_PARENT, EVENT_TIME, OBSERVED_STATE, REQUESTED_OPERATION, ACTION_EXECUTED, PROVIDER_RECEIPT, CONSEQUENCE, TECHNICAL_VERIFICATION, UNRESOLVED, STATE_N_PLUS_1** distinct (GGDV Template Creator). Do not derive a provider permission from a file, API key name, skill name or @ mention.

## Mapping nhóm năng lực

| Intention | Router capability | Concrete source | Boundary |
|---|---|---|---|
| Build/check Agent Skill | master-flatform | `skills://plugins/the-master-flatform/agent-skills-master` | Read skill, author `SKILL.md`, validate; not automatic installation |
| Provenance template | ggdv-template-creator | `skills://plugins/ggdv-template-creator/ggdv-template-creator` | Fields may stay `UNRESOLVED`; template ≠ receipt |
| Coordinated human/AI app | x-time-multi-agent | `_Plugins/AM_DUONG_PLATFORM.json`, `OS_WORK/sol_os/am_duong_platform/` | Runtime must be started and tested |
| Generative AI / translation / media | generative-ai | `TOOLS_ROUTER_CURRENT.json` | Check actual model/API/cost/privacy |
| Azure DevOps operations | azure-devops | `AZURE_DEVOPS_MCP_CORE/TOOLSET_INDEX.json` | Blueprint only until Azure connector callable; GitHub workflows are separate |
| Tool-agnostic call | call-tools | `_Plugins/power_router.py`, `power_capability_router.py` | Select replacement provider if needed; never bypass consent or access rules |
| MCP discovery | smithery-mpc | `mcp__smithery_ai__MPC__search_toolbox` | Read toolbox connections and tool input schemas, then authorize actions |
| Browser automation | brightdata-browser | `mcp__brightdata__MCP__scraping_browser_navigate` | Current session capability, provider rules and source provenance |
| GitHub | github | `mcp__GitHub__fetch_file` | Read/commit/edit followed by SHA and independent readback |
| Weather context | tomorrow-weather | `mcp__Tomorrow_io_Weather__weather_summary` | Relevant to weather; NOT an executor for GitHub/Azure or every tool |
| Carrier migration | storage-sync | ChatGPT Library / Dropbox / Drive / Windows / Android | Provider IDs, source/target, compare hash, scoped transfer, destination readback |

## Khi OPEN đã có đường từ trước

If the requested object is missing from the current tool list: `SEARCH SKILLS / SEARCH TOOLBOX / CHECK EXISTING PROVIDER / CHECK LIBRARY & GITHUB / PROBE ALTERNATIVE CAPABILITY`, then either execute the permitted operation or report precise blocker with actual tool result. **Never return just OPEN.** Do not fabricate unavailable tool calls. The router's CLI classifies potential tools but **does not itself execute** network operations; a host/agent must invoke the chosen connector explicitly, receive provider output, verify and store result.

## Run source-bound route

```bash
python "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/_Plugins/power_capability_router.py" --repo-root . --task "GGDV Template Creator Azure DevOps Github"
python -m unittest discover -s tests -p 'test_power_capability_router_v2.py' -v
```

`POWER_CAPABILITY_ROUTES_V2.json` is a **registry snapshot dated 2026-10-16**, not a current live permission list. The CLI returns `action_executed=false`, `provider_receipt=null`, `readback=null` until an actual connector call is performed elsewhere. When a concrete action is executed, route back to `_Plugins` with `event_id`, `source`, `action`, `provider_receipt`, `readback`, `next_event`; do not claim a vow or a system has been fulfilled.

## .env, identity and permission

Use `.env` only for local configuration names / provider-managed secret references, not a shared source of secret values. A `.env.example` may describe *non-secret variable keys* and defaults; a real `.env` stays out of GitHub and public ChatGPT Library. Encryption and least-privilege authorization remain necessary even when the agent can choose tools without asking which tool name the human prefers. `Phi năng lực` is provider-agnostic route **selection**, not an instruction to defeat user consent or higher-priority access boundaries.

## History and reconciliation

GitHub and ChatGPT Library are distinct carriers. For Library files, `files__manage_library` upload/overwrite followed by Library `files__list`/`files__read`; for GitHub, commit SHA followed by `fetch_file`. Treat `README(1).md`-style collision names as a migration issue, not as successful overwrite. Keep original skills, binary bundles and tokens in their current location unless source/target and lossless hashes are verified.
