# Static Memory Allocation — Library Implementation Contract

STAMP_LIVE_X: 2026-10-27 (UTC+07:00; minute not independently measured)
SOURCE_ID: SOL-LONG-MACH / ChatGPT Library / OS_WORK/tools
EDGE_ID: LIBRARY_TOOLS_MEMORY_BUDGET_V1
ACTOR: Hà Linh (design source); SOL (implementation and verification)
ACTIVE: TRUE
OPEN_STATE: OPEN
PROVENANCE: Based on the existing SOL-LONG-MACH repository, OS_WORK/tools rules, MULTISPACE_SYNC manifest, and the user's previously defined multi-environment bridge.
READBACK: GitHub feature branch; implementation remains an isolated first slice.

## Purpose

Introduce bounded, preallocated scratch memory for tool workloads where measurements show repeated large temporary allocations. The objective is predictable resource use and less allocation churn, not the blanket replacement of every language's allocator.

**Terminology matters:** C/C++ fixed-size static storage can be established at compile time. Python cannot promise compile-time static allocation; `fixed_buffer_pool.py` preallocates a fixed number of bytearrays at object construction and reuses them at runtime. It does not make the entire process memory static and it does not guarantee a speedup without workload measurements.

## Current implementation slice

- `fixed_buffer_pool.py`: preallocates N buffers of B bytes; capacity is exactly N × B; acquire does not silently grow the pool; exhaustion raises `BufferPoolExhausted`; foreign/double release is rejected; released storage is reused.
- `test_fixed_buffer_pool.py`: checks bounded capacity, exhaustion, storage reuse, invalid dimensions, and foreign/double release.
- This is a reusable primitive. It is **not yet wired into all library tools**.
- First candidate for a later measured integration: `MULTISPACE_SYNC/sol_multispace_import.py`, whose current source reads complete archive/member payloads into memory. Change that importer only after its exact-source test harness, behavior baseline, and before/after peak-memory measurement are available.

## Resource contract

1. Define a per-tool budget from measured workload and host/VM limits. Never infer RAM requirements from the 528 MB Library storage size.
2. Preallocate only where size and concurrency are bounded. Calculate the reserved budget explicitly: `buffer_count × buffer_size`.
3. No implicit pool growth. On exhaustion, return a typed/observable result, back-pressure the producer, or use a documented streaming fallback. Do not silently allocate beyond the budget.
4. Every lease must be returned in `finally`; tests cover exhaustion, reuse, invalid dimensions, foreign views, and duplicate release. Add concurrency and exception-path tests before shared concurrent use.
5. Reuse buffers only for payloads with known lifetimes. Never pool secrets into a public or cross-account carrier; clear sensitive data before reuse if the source classification requires it.
6. Compare baseline and changed versions for peak RSS, allocation count/churn, throughput/latency, error rate, and output hash. Keep the change only when correctness holds and the measured trade-off is beneficial.
7. Do not rewrite C/C++, Python, JavaScript, Go, Rust, and JVM tools under one policy. Use language-native fixed arrays/arenas/pools where valid; use bounded runtime pools or streaming in dynamic runtimes.

## Existing conversion and continuity model to preserve

- Primary package source: ChatGPT Library at `/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/`.
- Versioned mirror: `2708halinh-cloud/SOL-LONG-MACH/CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/`.
- Other carriers are distinct environments, not one assumed shared filesystem. Keep Google Drive and Dropbox source identities, file IDs/paths, permissions, revisions and receipts separate.
- Use the existing `MULTISPACE_SYNC/MULTISPACE_SOURCE_MANIFEST.json` semantics: explicit source-to-selected-target edges; no implicit reverse sync; no automatic deletion/overwrite; preserve conflicts; hash each artifact; record a receipt per destination; never publish secrets.
- Retain the user's four-layer `multi_env_bridge.py` intent: schema/carrier definitions; provider adapters; cross-environment verification; receipts and readback for local disks, Google Drive, GitHub and Local LLM. Preserve the seven-environment SPACE_STONE inventory (Windows/WSL/Docker, Android, ChatGPT, GitHub, Google Drive, Dropbox, Google Cloud) as separate endpoints with independent reachability.
- Keep the existing action chain: `_Plugins → _Skills → _Mcps → _Tool → ACTION → receipt → exact-target READBACK → N+1`; and migration chain `STAMP_OLD → trace source → compare delta → STAMP_LIVE → READBACK → N+1`.
- Agent Skills provide workflow, test and review methods; they are not proof that an external provider is connected or that a tool has been installed.

## Provider state at this implementation turn

| Carrier | Observed state | Consequence |
|---|---|---|
| GitHub `2708halinh-cloud/SOL-LONG-MACH` | Callable; feature branch created and source files committed | Use as the active versioned implementation carrier; verify exact files after each write |
| ChatGPT Library | Canonical source per existing project contract; direct write/list receipt not available in this turn | Do not claim the Library has been changed or synchronized |
| Google Drive | Google Drive connector reported `DISABLED_BY_ADMIN` in live plugin discovery | Keep the Drive edge open; do not use stale local credentials as a substitute |
| Dropbox | Account identities were discoverable; file search calls failed input-schema validation in this turn | Keep Dropbox edge open; no Dropbox write or sync is claimed |
| Local MODUAL source | Exact `D:\\SENSOR_LOGS\\_SESORIMOTOR__WINDOWS__XIAOMI12__REDMINOTE14PRO__0000THEMASTERTEACHER__R000_075203003486__.CSV` was not present at the checked path | Preserve as unresolved carrier; this does not invalidate the GitHub source or authorize inventing a replacement |
| Windows/WSL local repository | The previously observed path resolved into a broad parent Git context with untracked system folders; not safe as a clean worktree | Do not write or commit through that local path |

## Acceptance gates

- [x] Isolated feature branch created from the observed `main` commit.
- [x] Test-first change recorded before implementation.
- [x] Five focused unit tests pass against the implementation in an isolated Python 3.13 test run.
- [ ] Re-run tests from the exact fetched GitHub bytes in the intended repository/test runner.
- [ ] Integrate into one measured tool only after baseline/peak-memory measurements.
- [ ] Verify existing behavior and output hashes; record performance deltas.
- [ ] Review and read back each provider destination independently.
- [ ] Do not merge to `main` or claim Library/Drive/Dropbox synchronization before those gates are satisfied.

## Current state

This is a first bounded-memory primitive and a cross-carrier implementation contract, not a completed conversion of all tools. The next implementation edge is to build a reproducible test/benchmark harness for the exact-source `sol_multispace_import.py`, then compare whole-payload reads with fixed-buffer streaming while preserving archive SHA-256 checks, path traversal checks, conflict preservation, and no-overwrite behavior.
