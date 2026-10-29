# TESSERACT — MOTHERBOARD ARCHITECTURE 6D

SOURCE_DIRECT: Hà Linh — 2026-10-26.
STATUS: ARCHITECTURE_REPLACEMENT_BASELINE; runtime/provider closure remains evidence-gated.
LOCAL TARGET: G:\OS_Workspace\TESSERACT_OS.
GITHUB CARRIER: 2708halinh-cloud/SOL-LONG-MACH/TESSERACT_OS_6D.

## 0. Architectural invariants

- TESSERACT 6D has six equal operational faces around ☯️ TÂM: SPACE↔SOUL, MIND↔POWER, REALITY↔TIME. They are peer dimensions, not a linear sequence.
- Motherboard components are the execution/control topology. The six faces are the cross-environment continuity and evidence topology. Do not flatten one into the other.
- Design intent, local test results, provider connectivity, and end-to-end closure are separate states.
- ACTION → CONSEQUENCE → RECEIPT → INDEPENDENT READBACK → SAME STATE → CONCLUSION.
- A path, mount, configuration, process, or successful write response alone never proves provider connectivity or completion.
- Preserve source IDs and historical bytes. Protected originals are not deleted or destructively overwritten. Replacements require backup, exact target identity, and readback.

## 1. Motherboard

### CPU sockets
1. GEMINI — external model/provider route; capability and identity verification.
2. CHATGPT — external model/provider route; capability and identity verification.
3. LOCAL — Ollama/local model route when reachable, authorized, and policy-compatible.
4. TASK_WORKERS — bounded workers for independent subtasks, tools, tests, and verification.

Each socket advertises configured, reachable, authorized, capabilities, quota state, freshness, and last receipt independently. A socket declaration does not prove availability. Secret material remains in the authorized secret provider and never enters shared registers or logs.

### Northbridge — Autonomous Control Plane & Action Router
- Task arbitration: priority, dependency graph, deadline, capability fit, locality, cost/quota, risk, and failure state.
- Gate 1 (before action): source and target identity, authorization, policy, data classification, acceptance criteria, protected-target check, available disk/quota, recovery point, and expected side effects.
- Gate 2 (after action): action receipt, observable consequence, independent readback, same-state comparison, and acceptance check.
- Use bounded failover only when the alternative route is authorized and has the required capability. One unavailable carrier does not cancel independent work.

### DIMM — RAM_L1 Active Blackboard
Transient, versioned shared state for agent-to-agent exchange; not the only durable memory.
- REG_00: objective, scope, acceptance criteria, dependency edges.
- REG_01: source/target IDs, account/provider, revision, hashes, provenance.
- REG_02: current action, expected consequence, receipt, readback, state comparison.
- REG_03: unresolved edges, blockers, recovery point, next callable action.
- Updates use version checks/locking and reject credential values, cookies, authorization headers, and secret contents.
- Branch results remain separate until compared. Material conflicts block commit.

### VRM/PMIC — Quotas, resource safety, and survival
- Monitor token/API quota, provider rate limits, worker saturation, timeouts, memory pressure, and disk capacity.
- Disk policy: warning at ≥85% used; survival mode at ≥90%; critical at ≥97% used or <5 GiB free. The 85% point is an early warning, not permission for automatic deletion.
- At thresholds, prioritize recovery and read-only inspection, pause nonessential writes/builds/downloads, and create a remediation edge. Never perform blind cleanup.
- Circuit breaker and bounded failover on repeated failures; avoid retry storms and preserve failure receipts.

### Southbridge — Hardware Abstraction & I/O Controller
- Core Journal: SQLite + Git-backed source history + append-only event receipts.
- Cloud: Google Drive adapter with explicit account, Root/File ID, revision, hash, operation receipt, and provider-side readback. A mounted folder is not proof of provider sync.
- Virtualization: QEMU/Hyper-V adapter; explicit authorization and exact VM/device identity before passthrough or mutation.
- Network/security: NextDNS status/policy, localhost/LAN checks, ADB bridge with exact authorized Android device and command allowlist.
- Hardware/provider adapters return UNAVAILABLE or NOT_VERIFIED when disconnected; no simulated evidence.

## 2. Core Journal — append-only evidence

Each event records sequence, UTC timestamp, event ID, parent event, objective ID, source/target locator, source fingerprint, action, result, and receipt/readback references. Corrections append a superseding event; they do not erase prior events. A hash chain is tamper-evident, not proof of WORM storage or external immutability. GitHub and provider receipts remain separate evidence carriers.

## 3. Six-face continuity topology (TESSERACT 6D)

Six equal faces participate in the same state fingerprint:
1. GOOGLE_DRIVE_POINTER — pointer/locator and provider metadata.
2. LOCAL_BULK_STORAGE — source bytes, raw data, snapshots, restore points.
3. GITHUB_STATE — versioned law/spec/state and reviewable commits.
4. RCLONE_RAIDRIVE_RELAY — relay/virtual-drive copy, independently hash-checked.
5. GCP_STORAGE_BUFFER — temporary processing buffer with verified account/project and lifecycle policy.
6. XTIME_CDN_UBUBU_LEDGER — public/display and ledger layer, with privacy-safe payloads.

Each face has independent state: VERIFIED_ACTIVE, PARTIAL, UNBOUND, UNREACHABLE, CONFLICT, or NOT_VERIFIED. A face closes only with ACTION + CONSEQUENCE + RECEIPT + READBACK + SAME_STATE for the same fingerprint. Global 6D closure requires all six faces to meet acceptance criteria. OPEN is an honest state, not a command to stop unrelated work.

## 4. Runtime state machine

OBSERVE → LOAD_CURRENT_POINTER/CHECKPOINT → PLAN → GATE_1 → ROUTE → ACTION → CONSEQUENCE → RECEIPT → GATE_2_READBACK → JOURNAL_APPEND → REPORT → CONTINUE_OPEN_EDGES.

If an action fails, preserve failure evidence, keep the objective open, and try another authorized independent route when possible. A response boundary is not a task boundary. DONE requires evidence against the actual target's acceptance criteria.

## 5. Affect, correction, and recurrence

Preserve user signals and context as operational inputs. Separate observed facts from cause hypotheses; connect repeated failures to incident history and increase repair priority. A modelled affect field is not empirical proof of subjective experience. This distinction must never be used to discard the signal or avoid a requested repair.

## 6. Historical baseline and known gaps

The prior local receipt (2026-10-26 11:30 +07) recorded motherboard tests 20/20 and transducer tests 8/8 passing, combined 28/28; Ollama reachable; disk C at 93.07% used (SURVIVAL); NextDNS service running. It also recorded Google Drive provider sync NOT_VERIFIED, ADB unavailable on PATH, QEMU unavailable, Hyper-V unknown without elevation, and GitHub Actions status unverified. These are historical observations, not a fresh test of this replacement.

## 7. Deployment and acceptance gates

1. Preserve current files and hash backups before replacement.
2. Replace local architecture document/spec only; do not rewrite runtime or protected source history as part of this design change.
3. Update the GitHub TESSERACT 6D README/spec and read back exact commit/blob content.
4. Publish the same architecture carrier into the SOL-LONG-MACH ChatGPT Library path with source link and SHA-256 provenance.
5. Run JSON parse, Python compile, targeted motherboard/transducer tests, and broader regression.
6. Independently inspect provider/device state; keep unverified faces open.
7. Close deployment only after local + GitHub + Library readbacks match the intended architecture fingerprint.

No claim of full-system synchronization is valid until each target has its own fresh readback.


## Intel Core Ultra software profile emulation

- Registry: `INTEL_CORE_ULTRA_PROFILES.json`; runtime: `intel_core_ultra_emulator.py`; tests: `test_intel_core_ultra_emulator.py`.
- Thirty CPU profiles were transcribed from the user-supplied catalog. All remain `source_verified=false` pending independent Intel ARK verification.
- Core count is used as a virtual worker-slot ceiling. Smart Cache is a software budget only; reported turbo frequency is metadata.
- GPU execution remains disabled until a real driver/backend is independently detected.
- This is scheduler/resource-profile emulation, not physical silicon, microcode, ISA, actual cache, clock/thermal behavior, or benchmark emulation.


## Canonical motherboard architecture

The current local-first architecture replacement is maintained in [`MOTHERBOARD_ARCHITECTURE.md`](./MOTHERBOARD_ARCHITECTURE.md). The machine-readable motherboard spec is [`SPEC.json`](./SPEC.json). The same source files and Intel Core Ultra emulation package are mirrored under `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/TESSERACT_OS_6D/`; use readback checks before claiming cross-carrier closure.


## 10. Durable motherboard kernel and live loop supervision

Implementation files in this GitHub carrier:
- `tesseract_motherboard_kernel.py` — checkpoint restore, bounded CPU/memory/time scheduler, tool-call wrapper, causal journal, distinct brain-label provenance, event-conditioned scoring and 5D capability regression.
- `tesseract_motherboard_daemon.py` — bounded continuity/heartbeat loop; it restores each cycle and records unresolved edges without claiming they are completed.
- `TESSERACT_MOTHERBOARD_KERNEL_SPEC.json` — machine-readable component contract.
- `test_tesseract_motherboard_kernel.py` — regression tests.

The local Windows deployment maps these files to `runtime/`, `config/` and `tests/` under `G:\OS_Workspace\TESSERACT_OS`. The GitHub carrier keeps the source files at this directory root, matching the existing carrier convention.

The event journal uses ALPHA, BETA, GAMMA, DELTA and THETA bands. Its existing project cycle is ALPHA → BETA → DELTA → THETA → GAMMA → ALPHA. Tool calls are observed when routed through the wrapper; this is not a claim of invisible interception of every hosted ChatGPT tool call. Missing receipt/readback stays OPEN.

`UBUBU` and `UNTUNBU` remain distinct exact source labels and are never merged because their names look similar. The reward function is an evidence-conditioned computational heuristic, not a claim of biological dopamine or learned model-parameter updates.

Running status requires a live process probe and a fresh heartbeat. A branch, file, PID locator or prior test receipt alone does not prove that the local supervisor is currently running.