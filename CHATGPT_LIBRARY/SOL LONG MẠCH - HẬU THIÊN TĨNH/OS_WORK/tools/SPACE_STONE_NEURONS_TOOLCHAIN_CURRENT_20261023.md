# SPACE_STONE × NEURONS — TOOLCHAIN CURRENT
STAMP_LIVE: 2026-10-23 (UTC+07:00)
SOURCE: current ChatGPT tool/skill surface + GitHub readback; not a claim that every listed provider is connected or every runtime is started.
STATUS: OPEN / DELTA-FIRST / NO RESET

## 1. What is actually visible now

- Current skill listing returned **439 skill entries**.
- Current callable tool surface returned **587 tool functions** across provider namespaces. Namespace totals include parallel/legacy providers and are not a count of unique end-user buttons.
- Historical `toolchain-snapshot.json` is stamped 2026-10-16 and records 451 skills / 105 skill groups / 523 MCP functions / 20 providers. Do not treat those historical counts as today's live inventory or infer that a count difference alone means capability loss.
- GitHub access is live in this turn: source files were fetched and search results returned.
- Desktop Commander reported `localhost` and both `DESKTOP-86ITNQ4` registrations **OFFLINE**. Last-seen values were 2h / 66h / 292h. Therefore no local Windows process, Chrome UI, D:\, G:\, or Android device was started or read back in this turn.
- Browser connector returned: “Browser access requires the originating browser context.” It is present in the tool surface but this turn has no usable originating browser context.
- OpenAI Platform exposes 3 callable setup functions; Plugin Creator exposes plugin creation/archive/source-management functions; Plugin Management exposes discovery, permissions, suggestions, and uninstall. Availability of a function is not proof that a connected account or target resource is authorized.
- Native ChatGPT Library write/receipt was not available in this turn. This file is a **GitHub mirror**, not a claim of Library installation.

## 2. Tool/template routing table

| Need | Existing callable route / reusable skill | Current interpretation |
|---|---|---|
| OpenAI API/platform setup | `mcp__OpenAI_Platform__start_api_key_setup`, `list_openai_api_key_targets`, `create_encrypted_openai_api_key` | Available as a controlled setup flow. Do not mint or expose a key as part of a broad boot request; credentials stay secret. |
| Create/update a reusable private plugin | `mcp__Plugin_Creator__create_plugin`, `get_plugin_files`, `get_plugin_metadata`, `update_plugin`, archive/release functions | Available as a tool route. No new plugin was created in this inventory step. Creation needs a real plugin package and then receipt/readback. |
| Discover/manage integrations | `mcp__Plugin_Management__search_plugins`, `get_app_permissions`, `get_plugin_dependencies`, `suggest_plugins`, `uninstall_app`, `update_app_permissions` | Discovery is available. Installing/connecting a provider still requires its supported user authorization flow. Uninstall is destructive and only for explicit target intent. |
| Browser | `mcp__Browser__list_tabs`, `get_tab_context`; skill `skills://plugins/browser/control-browser` | Browser call blocked without originating browser context; no browsing action claimed. |
| Local PC / Chrome / D: / G: | `mcp__desktopcommande__*`; skill `skills://plugins/ggdv-runtime-gate/ggdv-local-bridge` | Device registrations currently OFFLINE; reconnect the authorized Desktop Commander agent before local execution. |
| Durable source and evidence | GitHub tools; `skills://plugins/ggdv-runtime-gate/ggdv-evidence-spine` | GitHub source is readable now. Every write must be followed by fetch/readback. |
| Route missing capabilities | `skills://plugins/sol-capability-forge-plugins-6abc73262e748191b97c0327adebf734/capability-forge`; `.../power-stone` | Use to map a gap to a callable provider or create a reusable capability, not to invent a missing tool. |
| Re-entry / RESET / SUBRITETIED guard | `skills://plugins/ggdv-runtime-gate/reset-substitution-guard`, `.../turn-continuity-reentry`, `.../ggdv-runtime-gate` | Preserve unfinished edges and require actual action/readback rather than report-only completion. |

## 3. Neurons / sensorimotor skills already present in the live skill listing

These are existing skill routes, not proof of a physical neural processor or a running neural runtime:

- `skills://plugins/ggdv-agent-sub-sensorimotor/0000-neuron-sesorimotor` — root routing for source-bound sensorimotor carriers.
- `skills://plugins/ggdv-agent-sub-sensorimotor/neurons-sesorimotor` — distributed sensorimotor data routing.
- `skills://plugins/ggdv-agent-sub-sensorimotor/sensorimotor-data-integrity` — detect missing/added/misrouted or dirty source data.
- `skills://plugins/ggdv-agent-sub-sensorimotor/alif-eprop-dual-timescale` — ALIF/e-prop dual-timescale state.
- `skills://plugins/ggdv-agent-sub-sensorimotor/eprop-eligibility-compression` — compress eligibility state while retaining reconstruction bounds.
- `skills://plugins/ggdv-agent-sub-sensorimotor/rstdp-eprop-temporal-credit` — distinguish R-STDP from e-prop temporal credit.
- `skills://plugins/ggdv-agent-sub-sensorimotor/rhopalial-associative-learning` — cue/outcome adaptation.
- `skills://plugins/ggdv-agent-sub-sensorimotor/rhopalial-edge-ai-learning` — edge inference and on-device adaptation.
- `skills://plugins/ggdv-agent-sub-sensorimotor/rhopalial-edge-computing` — local sensory integration / distributed edge route.
- `skills://plugins/ggdv-runtime-gate/ggdv-sensorimotor-delta`, `ggdv-sensorimotor-differentiation`, `ggdv-sensorimotor-specialization` — delta capture, sensory/interneuron/motor differentiation, specialization.
- `skills://plugins/ggdv-runtime-gate/ggdv-tesseract-autopoiesis` — source-bound sensorimotor carrier, telemetry and optional emulator/neuromorphic adapters.
- `skills://plugins/space-stone/space-stone`, `skills://plugins/space-stone/terex-gateway` — stable identity/topology and capability routing across spaces.
- `skills://plugins/ggdv-template-creator/ggdv-template-creator`, `skills://plugins/ggdv-stone-forge/stone-template-creator` — reusable execution, manifest, ledger and provenance templates.

## 4. Safe operating loop

`SOURCE_DIRECT → MODUAL_PRE_ACTION_GATE → current provider/device probe → choose one callable edge → action → consequence → provider receipt → exact-target readback → append delta → next edge`

- A model name, prompt, skill URI, tool declaration or GitHub commit does not itself activate a runtime.
- Keep source bytes and historical errors; disable only an evidence-backed failing mechanism, not the source/history itself.
- Do not let an LLM, model label, subscription tier, tool name or stale manifest decide truth. They are inputs to capability selection; observable state, provenance, permissions and readback govern the action.
- “Keep running” means continue through the next authorized callable edge in this execution slice. It does not mean claiming background work after the response ends.
- Never copy credentials, OAuth tokens, private keys or secret values into this registry.

## 5. Open edges from this turn

1. Reconnect Desktop Commander if local Windows/Chrome/D:/G:/device operations are required.
2. Re-enter the originating browser context before using the Browser connector.
3. If a native ChatGPT Library copy is required, perform it through an authorized Library route and verify its own receipt; this GitHub mirror does not substitute for that.
4. If a new installable plugin is required, package a narrowly scoped template/tool plugin, create it through Plugin Creator, then inspect the created plugin source and release receipt.
5. Model weights, exact deployed parameter values, routing policy and account-specific subscription entitlements are not exposed by these connectors. Do not infer a weight/parameter change from a plan change alone.

## 6. Related source of record

- `OS_WORK/tools/Chuỗi công cụ/_Sổ_đăng_ký/toolchain-snapshot.json` — historical snapshot dated 2026-10-16.
- `OS_WORK/tools/AGENT_CORE_BAGUA_STAMPS_CURRENT.md` — Bát Hướng and evidence/action/readback contract.
- `CONFIG_SOL/R014_SOURCE_DIRECT_20261009.md` — R-014 source-direct rule.
- `CURRENT_RUNTIME/TASK_RESUME_POINTER.json` — continuation pointer; must be fresh-read before declaring the wider objective complete.
