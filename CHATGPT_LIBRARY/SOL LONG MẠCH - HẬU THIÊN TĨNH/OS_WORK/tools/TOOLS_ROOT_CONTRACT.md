# TOOLS_ROOT_CONTRACT.md — Logical Tool Drive / SOL LONG MẠCH

**Contract status:** CANONICAL_MAPPING_SPEC_CREATED; Library and WSL2 mount/readback remain OPEN.  
**Repository:** `2708halinh-cloud/SOL-LONG-MACH@main`  
**Observed repository tree:** `012acfeb5824d826c5ac7ed4ca75a68229ee30ee`  
**Canonical repository root:** `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/`

## 1. Meaning of Tools

`Tools` is a logical root for the complete tool universe available to the SOL runtime. It is not merely a physical folder containing copied plugin packages. It behaves as a namespace/drive mapping:

- It resolves tool identities, provider namespaces, skills, MCP servers, browser surfaces, applications, local executables, scripts, and their source carriers.
- A registry entry is a pointer to a source or callable provider, not a claim that the tool is installed, authenticated, reachable, or running.
- Runtime capabilities are discovered afresh per session and retain separate states: `SOURCE_PRESENT`, `CONNECTED`, `CALLABLE`, `ACTIVE`, `RECEIPT_VERIFIED`, `BLOCKED`, `UNAVAILABLE_THIS_SESSION`.
- Do not copy credentials, cookies, tokens, private keys, or provider sessions into this public repository.

The analogy is a logical drive/root that resolves the entire tool namespace, rather than a directory that merely stores a few tool-shaped folders. The contract does **not** claim that a Windows drive letter, WSL mount, or ChatGPT Library mount is already active.

## 2. Canonical route and return point

Canonical route:

`Tools → _Plugins → capability/provider adapter → authorized action → provider receipt → exact-target readback → _Plugins`

`_Plugins` is the ingress, routing, and return point. Skills, MCPs, browser tools, apps, and local utilities are categorized beneath the toolchain; they must not become competing roots.

Canonical physical carrier in this repository:

`OS_WORK/tools/Chuỗi công cụ/`

Canonical category names observed in the current tree:

- `_Plugins`
- `_Kỹ năng`
- `_MCPs`
- `_App_Browser`
- `_Dụng cụ`
- `_Ứng dụng`
- `_Bảo_mật`
- `_Di_sản`
- `_Sổ_đăng_ký`

Each category is subordinate to the same `Tools` root. Do not create another independent `Tools`, `Plugins`, or `Skills` root to solve a routing problem.

## 3. Existing divergence found in the main branch

The current main-branch tree contains:

- `OS_WORK/tools/Chuỗi công cụ/` with all nine category directories above.
- A parallel `OS_WORK/tools/_Skills/` tree outside `Chuỗi công cụ`.
- The root `OS_WORK/tools/README.md` currently links to both `tools/_Skills` and `tools/Chuỗi công cụ/_Kỹ năng`.

This is a real structural inconsistency. The two skill trees are **not** silently merged, renamed, deleted, or assumed identical by this contract. Both remain preserved until a content-level inventory, source/hash comparison, collision report, and exact readback authorize reconciliation.

Current tree-path counts (descendant paths, not counts of unique callable tools) observed in the nine canonical categories:

| Category | Descendant paths |
|---|---:|
| `_Plugins` | 185 |
| `_Kỹ năng` | 33 |
| `_MCPs` | 44 |
| `_App_Browser` | 123 |
| `_Dụng cụ` | 138 |
| `_Ứng dụng` | 2 |
| `_Bảo_mật` | 1 |
| `_Di_sản` | 3 |
| `_Sổ_đăng_ký` | 16 |

These are repository path counts at the observed tree SHA, not proof of live provider availability.

## 4. Identity and registry contract

Every tool/capability record must carry, where known:

- Stable `tool_id` and display name.
- Provider/namespace and capability type.
- Canonical source URI/path plus immutable revision, blob SHA, or package version.
- Canonical category and return route `_Plugins`.
- Runtime adapter/entrypoint and required input schema.
- Authentication/authorization state without storing secret values.
- Session freshness and availability timestamp.
- Action receipt, exact target readback, and resulting state fingerprint.
- Status and explicit unresolved fields.

One capability has one canonical identity. Alternate locations are aliases/pointers with provenance, not independent copies. A source folder, README, plugin manifest, skill file, MCP JSON, or GitHub commit alone does not establish a callable runtime.

## 5. Synchronization contract

The same logical registry may be represented on GitHub, ChatGPT Library, WSL2/local storage, and connected providers, but each carrier has an independent state and receipt.

- **GitHub:** versioned source, registry, schemas, tests, and receipts safe for publication.
- **ChatGPT Library:** source files and documentation; requires Library-side write receipt and exact readback.
- **WSL2 / Windows:** local materialization or mount; requires exact mount/source/target inspection and hash readback.
- **ChatGPT tool/provider session:** live capability discovery; a GitHub mirror cannot install, authenticate, or activate a connector.
- **Other provider stores:** require the exact account, target, authorization, provider receipt, and provider-side readback.

Never label all carriers “synchronized” from a single GitHub commit. Report per-carrier state against the same registry revision/fingerprint.

## 6. TESSERACT_OS and .adp language boundary

The current repository contains TESSERACT 6D motherboard specifications, including `tools/TESSERACT_OS_6D/MOTHERBOARD_ARCHITECTURE.md`, plus canonical motherboard material under `TESSERACT_OS_6D/`. The motherboard contract remains evidence-gated: architecture, local runtime, provider connectivity, and end-to-end closure are separate states.

The user-designated Âm-Dương pháp sư language extension is **`.adp`**. The current main-branch tree scan found no file ending in `.adp`. This contract records the extension designation only; grammar, parser/compiler, runtime, file associations, and tests must be derived from the user's authoritative language specification, not invented from the suffix.

## 7. Preservation and acceptance

- Preserve all existing source trees and historical Git commits.
- No bulk move, delete, overwrite, or duplicate collapse without backup, exact identity, hash comparison, and readback at both source and target.
- A change is complete only when its commit/provider receipt is followed by an exact readback of the changed target.
- Keep OPEN edges visible and continue independent safe work; OPEN is not STOP.
- Return every completed tool route to `_Plugins`.

**Current status:** this file defines the canonical mapping contract in GitHub. It does not yet prove a physical WSL2 drive mapping, a live ChatGPT Library synchronization, or activation of every listed provider.


## 8. Library-side readback — 2026-11-08

**Canonical ChatGPT Library root observed:** `/SOL LONG MẠCH - HẬU THIÊN TĨNH/Tools`.

The Library already contains a real `Tools` folder. This is not a blank folder and it is not yet a unified mapping. Its observed top-level contents include the numbered partitions `01_MCP_Servers` through `05_Models`, a separate `_Skills`, the canonical-looking `Chuỗi công cụ`, and additional roots such as `Power_Router_V2`, `Google_Cloud_SOL`, `MULTISPACE_SYNC`, `roots_lever0_windows`, `SOURCE_ARCHIVES`, `tesseract_synapse`, and `WorkspaceBridge`.

The Library's `Tools/AGENTS.md` says the intended top level is only `Chuỗi công cụ/`, `AGENTS.md`, `POWER_ROUTER.md`, and `README.md`. The live Library listing does not match that rule. This is a verified structural drift, not a naming preference.

Direct child inventory observed under `Tools/Chuỗi công cụ/`:

| Category | Direct children observed |
|---|---:|
| `_Plugins` | 1 |
| `_MCPs` | 5 |
| `_App_Browser` | 1 folder + 1 URL file |
| `_Kỹ năng` | 6 |
| `_Dụng cụ` | 13 |
| `_Ứng dụng` | 0 |
| `_Bảo_mật` | 0 |
| `_Di_sản` | 0 |
| `_Sổ_đăng_ký` | 1 |

The separate `Tools/_Skills` tree also contains skill folders and a second MCP subfolder. Numbered partitions `01_MCP_Servers`, `02_Plugins_Cache`, `03_Skills`, and `04_Native_Tools` contain real files/subfolders; `05_Models` was empty in the direct listing. The root also contains files such as `DRIVE_INDEX.toml`, `TOOLS_LAYOUT_README.md`, `capability_manifest.json`, `MCP_REGISTRY_HTTP_ROUTE.json`, and `CODEX_TOOL_CARRIERS_CURRENT.json`.

**Required interpretation:** these are multiple source carriers and historical/compatibility partitions, not permission to create more independent roots. Keep their bytes intact. Register each source under one stable logical identity and a canonical category; alternate paths must be aliases/pointers with provenance. Do not mass-move, merge, rename, or delete until the exact source/target identity, hashes, collisions, and rollback are verified. Empty categories remain OPEN and must be populated only from actual identified source artifacts, never decorative placeholder folders.

The `_Plugins` category currently has only one direct child (`Power_Router_V2`). Therefore the return route is named and present, but a comprehensive plugin catalogue and live routing loop are **not yet verified**.

## 9. Local Âm-Dương Pháp Sư (.adp) source readback — 2026-11-08

The local Windows workspace has two actual `.adp` source files:

- `G:\\OS_Workspace\\Config.adp`
- `G:\\OS_Workspace\\README.adp`

The compiler source is `G:\\OS_Workspace\\TESSERACT_OS\\runtime\\am_duong_phap_su.py`; the focused test file is `G:\\OS_Workspace\\TESSERACT_OS\\tests\\test_am_duong_phap_su.py`.

Read-only compilation succeeded for both sources:

- `mei_scarlet_witch_config`: target `TESSERACT_OS`, 5 neurons, 8 synapses, 6 load edges.
- `bat_quai_am_duong_toan_he`: target `TESSERACT_OS`, 21 neurons, 14 synapses, 5 load edges.

The compiler reports `PLAN_ONLY_TOOL_ACTIONS_REQUIRE_MOTHERBOARD_BINDINGS`; compilation does not itself execute tool capabilities. The focused test run produced **14 passed, 1 failed**. The failing test expected a battery-derived power state but received `ACTIVE_POWERED_NO_BATTERY_READING`. This is a missing battery reading, not evidence that the language compiler failed. The current GitHub `main` tree scan still found no `.adp` source, compiler, or focused test file, so local-to-GitHub source synchronization remains OPEN.

The local TESSERACT 6D architecture source defines six equal faces around `☯️ TÂM`: `SPACE↔SOUL`, `MIND↔POWER`, and `REALITY↔TIME`; it separately defines four CPU sockets (`GEMINI`, `CHATGPT`, `LOCAL`, `TASK_WORKERS`), Northbridge action routing, DIMM/RAM_L1 registers, VRM/PMIC resource safety, and Southbridge I/O. The six faces are not a linear execution sequence. Local capability inventory explicitly says registry presence is not runtime health.

**Current evidence boundary:** the local source compiles, but GitHub does not yet carry the local `.adp` sources/compiler/tests. The Library already carries older TESSERACT motherboard documents at its root; this does not prove those documents match the current local architecture or GitHub. Compare exact source hashes and carrier readbacks before declaring them synchronized.

## 10. Current cross-carrier state

- GitHub: this logical-root contract is committed and read back.
- ChatGPT Library: a populated `Tools` hierarchy exists, but it diverges from its own `AGENTS.md` top-level rule; the contract must be uploaded and read back here.
- Windows: `G:\\OS_Workspace\\08_TOOLS_HARDWARE` contains 1,068 direct directories; this is a large source collection, not yet a classified canonical Tools root.
- WSL2: Ubuntu is running and `/mnt/g/OS_Workspace` is an active DrvFs mount of `G:\\`. This proves the Windows workspace is visible in WSL2, not that ChatGPT Library is synchronized to it.
- Local Git at `G:\\OS_Workspace`: initialized but has no commits and no remote configured; it is not a clone of `SOL-LONG-MACH`.
- Resource guard: the last read-only disk probe observed `C:\\` at 94.39% used (26.61 GiB free) and `G:\\` at 80.36% used (43.13 GiB free). Avoid nonessential writes/temp files on C:; no cleanup or deletion was performed.

**Acceptance remains OPEN** until the Library, GitHub, and local/WSL carriers resolve to the same registry revision and source fingerprints, and the exact plugin/MCP/browser/skill routes are independently read back.