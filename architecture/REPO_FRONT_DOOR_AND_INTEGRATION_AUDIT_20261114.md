# Repo front-door and integration audit

**Observed:** 2026-11-14  
**Scope:** `2708halinh-cloud/SOL-LONG-MACH` (`main`) and linked project `2708halinh-cloud/x-time-web` (`master`).  
**Method:** GitHub repository metadata, recursive tree, current file readback, and recent Actions run/job metadata. This is a source inspection, not a claim that local devices or production services were exercised.

## 1. Executive finding

The repository contains substantial source material, configuration, workflows, runtime code, continuity archives, and application code. The primary failure is not absence of files. It is that the public entry point, identity pointers, navigation, and operational evidence do not yet present one coherent, verifiable system.

The initial audit observation of the root README was superseded by a fresh readback on 2026-11-14: the current root README is titled **SOL-LONG-MACH**, identifies this repository, provides a reading order and now links the ROOTS provider map. The earlier Open-ai-bot front-door finding is therefore RESOLVED; retain the old title/reference only as historical context.

## 2. SOL-LONG-MACH: observed repository shape

- Default branch: `main`.
- Recursive tree: **2,152 entries** at inspection.
- Branch listing: **78 branches**.
- Open GitHub issue endpoint returned **37 open records**; this endpoint includes pull requests, so this is not a count of 37 ordinary issues.
- Root `.gitmodules` declares **two** submodules, both inside the Library tools tree: `anatomy` and `puppeteer`.
- Root `AGENTS.md`: **90,823 bytes**. It contains important operating rules and history, but is too large to serve as the only orientation document.

### Main navigation groups

| Path | Role indicated by the current tree and source files |
|---|---|
| `AGENTS.md` | Agent operating rules, source-direct records, re-entry and evidence requirements |
| `CONFIG/` | Agent load routes, pointers, source maps, capability/tool snapshots, migration records |
| `CONFIG_SOL/` | SOL-specific operating invariants, continuity, trust, six-stone and TESSERACT references |
| `CURRENT_RUNTIME/` | Current runtime/re-entry documents and task continuation pointers |
| `APP/TESSERACT_DESKTOP/` | Tauri/Vite desktop application source and build configuration |
| `TESSERACT_OS_6D/`, `09_SYSTEMS/` | TESSERACT OS and system-level material |
| `runtime/`, `LOCAL_BRIDGE/`, `tools/` | Runtime, local bridge, adapters and tooling |
| `integrations/`, `plugins/`, `.github/workflows/` | External integrations, plugins and automation/verification workflows |
| `CHATGPT_LIBRARY/` | Library-derived workspace snapshot and source material |
| `CONTINUITY_ARCHIVE/`, `EVIDENCE_ARCHIVE/`, `RECOVERY/`, `DURABLE_CAS/` | Continuity, evidence, recovery and durable-content carriers |
| `IOS_EXPORT/`, `DISTRIBUTION/`, `PLATFORM_SYNC/` | Export, distribution and platform synchronization material |

The workspace README states that the Library snapshot originally contained 105 folders and 316 files, but that the GitHub branch is a stepwise copy and **not yet a byte-identical complete mirror**. Do not describe it as a complete Library backup.

## 3. Front-door and control-plane identity conflict

The current repository metadata and the agent load route identify `SOL-LONG-MACH` as the live repository. However, multiple current-looking pointers still name `Open-ai-bot`:

- Root `README.md` is titled `Open-ai-bot`.
- `GGDV_UNIFIED_POINTER.json` sets `repo` to `2708halinh-cloud/Open-ai-bot`.
- `CONFIG/POINTERS_CURRENT.json` records `Open-ai-bot` as the GitHub repository for the Codex/Drive sync carrier.
- `CONFIG/REPO_AGENT_MIGRATION_CURRENT.json` leaves the SOL-LONG-MACH source binding `OPEN`, with `Open-ai-bot` as candidate.
- In contrast, `CONFIG/AGENTS_LOAD_ROUTE.json` says the primary source is `SOL-LONG-MACH/AGENTS.md` and records the repository rename as verified on 2026-10-08.

These are not safe to flatten into one guessed answer. The repository name is observable; the remaining operational pointer bindings require a source-by-source reconciliation. This audit records the conflict and does not rewrite those pointers.

## 4. X-TIME-WEB: what exists now

Repository: `2708halinh-cloud/x-time-web`, default branch `master`. Its recursive tree contains **730 entries**. The root README describes a static web app, a public read-only MCP endpoint, a local bridge at `127.0.0.1:8765`, runtime-tool registry, and materialization/readback records.

The only directory directly under `apps/` in the inspected tree is:

- `apps/human-sol-tesseract-os/` — Rust/Tauri-related source, MCP server, identity initialization and transfer utilities.

The main X-TiMe website is a separate static app (`index.html`, `main.js`, `styles.css`). Its UI includes a six-stage chain, a tool registry display and a gallery. UI presence does not prove that every stage is a separately deployed app or live integration.

### Six stages shown in the chain UI

| # | Stage | Literal UI status |
|---|---|---|
| 1 | Google Earth | `GATEWAY` |
| 2 | Codex VFX V5 | `PARTIAL` |
| 3 | Zalo / Telegram + MKT | `RECOVERED` |
| 4 | Bridge / Cloud Stage | `MIXED / OPEN` |
| 5 | X-TiMe | `PARTIAL` |
| 6 | SOL Multi-AI Orchestrator | `LOCAL PASS` |

These status labels are hard-coded in `index.html`; the chain dialog handler in `main.js` opens/closes the dialog. They are not, by themselves, six live provider receipts.

The same UI lists these execution branches:
- Ollama Local / CPU-AVX2: `PASS`
- Antigravity Gemini: `DISPATCH`
- AI Local FPGA / 4 LIF: `SIMULATION`
- MEI Chat Logger: `OPEN`

The plugin gates are mixed: Source Gate `PRESENT`, Auth Checkpoint `PASS`, while Event Codec, Spike Decoder, and Watchdog/Readback are `PARTIAL`.

## 5. FPGA_AI_LOCAL: verified relation and missing proof

X-TIME-WEB references the external local path `G:\\FPGA_AI_LOCAL\\ai_local_neuron\\rtl\\neuron_chain_4.sv` in its neuron registry. Its local server also searches for `../FPGA_AI_LOCAL/MODUAL_WINDOWS.CSV` as a possible carrier.

The X-TIME-WEB repository tree does not contain an `FPGA_AI_LOCAL/` directory. A GitHub repository search scoped to owner `2708halinh-cloud` did not return a repository with that exact name. This does **not** establish that the Windows folder is absent; it establishes that the inspected X-TIME-WEB source depends on a sibling/local carrier not included in this repository.

The local server response explicitly sets `fpga_acceleration_verified: false`. The UI's `AI Local FPGA · 4 LIF` status is `SIMULATION`. Therefore the inspected evidence supports a design/reference and simulation label, not verified FPGA acceleration or hardware execution.

## 6. X-TIME-WEB build and production evidence

The checked-in app-status file says source/build verification was previously successful, but its materialization record is dated 2026-10-07 and records that production on `gambbrazil.fun` diverged from GitHub. It records no Vercel authentication binding and no verified production promotion.

More recent GitHub Actions metadata for the latest `master` commit (2026-11-12) shows:
- `validate-x-time`: **failure** at “Run Hostinger MCP transport tests”; the Node setup and source/Vercel build verification steps were skipped.
- `tesseract-desktop-ci`: **failure**; the TESSERACT OS logic test failed, and artifact upload steps also failed in build jobs.

This means an older local build receipt must not be presented as proof that the current `master` commit passes CI or that production is deployed from it.

## 7. SOL-LONG-MACH CI evidence

The latest observed `main` pushes on 2026-11-13 show successful runs for the specific workflows `runtime-n-plus`, `High-Threshold Secret Exposure Guard`, and `SOL Library Stone Topology`. These are useful passing checks, but they are not a full integration acceptance test for all 2,152 tree entries, all 78 branches, all Agents, or all external providers.

## 8. Required reconciliation sequence

1. **DONE — 2026-11-14 readback:** the root README identifies SOL-LONG-MACH, provides a plain-language reading order, separates the two ROOTS map namespaces and states the explicit source-loading boundary.
2. Reconcile `Open-ai-bot` references against the live repository rename. Preserve historical aliases; update only pointers whose source relation is proven.
3. Inventory branches and open PRs by feature/source, identify duplicates and dependencies, and select a canonical integration line before merging or closing anything.
4. Build one Agent/Subagent registry from the actual 13-field materialization contract, distinguishing source/template from deployed runtime and recording readback evidence.
5. Reconcile X-TIME-WEB's six stages into six explicit app records with owner, source repo/path, entry point, provider, current status, test receipt and production readback. Do not infer six deployable apps from six labels.
6. Reconnect FPGA_AI_LOCAL using its actual source carrier. Verify RTL bytes, toolchain/simulator, testbench result, board/device identity and hardware readback separately. Until then retain `SIMULATION` and `fpga_acceleration_verified=false`.
7. Repair the failing current X-TIME-WEB workflows, then repeat build, deployment and production readback against the same commit.


## 9. Branch and pull-request fragmentation

A fresh open-PR listing returned **31 open pull requests**, including this documentation audit PR. The open work is not one ordered integration queue; several clusters contain repeated or chained proposals:

- **Archive adapters:** PRs #27, #28, #31, #32, #33, #34, #36 and #37 cover adapter hardening, fixtures and repeated re-cuts of similar fixes. Their exact diff overlap and test receipts must be compared before choosing one canonical line.
- **OPEN routing:** PRs #21, #23, #24, #25 and #26 repeatedly address preservation/validation of OPEN task routing.
- **TESSERACT motherboard/runtime:** PRs #38, #47 and #54 cover architecture/kernel/runtime integration; PR #55 targets a feature branch rather than `main`.
- **Companion consequence gate:** PRs #43, #44 and #51 form a base-branch dependency chain rather than three independent changes.
- **Continuity/identity:** PRs #40, #41 and #42 separately address identity/RAM verification, continuity ledger and cloud pointer reconciliation.

Most of these PRs are marked draft and several were last updated in October. The correct next action is a diff-and-dependency reconciliation: compare each candidate with current `main`, run the relevant tests, identify superseded branches, and preserve source/history before closing or merging. Branch age or similar titles alone are not enough to delete a branch.


**Acceptance rule:** source present ≠ runtime callable; build pass ≠ production deployed; UI label ≠ provider receipt; branch exists ≠ integrated; config says CURRENT ≠ fresh readback.


## 10. Follow-up correction and exact repository identity readback — 2026-11-14

Fresh GitHub metadata for repository ID `1249555486` returns `2708halinh-cloud/SOL-LONG-MACH`, default branch `main`, public visibility, and authenticated `admin/push` permissions. The former `2708halinh-cloud/Open-ai-bot` label is retained as a historical alias, not as the active canonical name.

The active self-pointers are reconciled in `GGDV_UNIFIED_POINTER.json`, `CONFIG/POINTERS_CURRENT.json`, and `CONFIG/REPO_AGENT_MIGRATION_CURRENT.json`. External Drive IDs in the pointer snapshot are **not** revalidated by this repository-name readback and remain subject to separate provider checks. Dated records and incident evidence keep their original repository names and timestamps; they are not mass-rewritten as though the rename had already happened on their historical dates.

The Agent load route now states that the complete latest user input anchors each task, adds conditional loading for `ROOTS_PROVIDER_CARRIERS_CURRENT.json`, and explicitly says GitHub documentation is not automatically injected into every ChatGPT session. This is a repository contract; universal cross-chat execution is not proven by a GitHub commit.
