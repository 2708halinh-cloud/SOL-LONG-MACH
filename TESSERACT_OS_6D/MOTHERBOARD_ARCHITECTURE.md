# TESSERACT — MOTHERBOARD ARCHITECTURE

SOURCE_DIRECT: Hà Linh — 2026-10-26. State: architecture baseline; operational verification remains per carrier.

## 1. Motherboard

### CPU sockets
- `GEMINI`: Gemini API connector; credentials are references to a secret provider, never token/cookie values in source or logs.
- `CHATGPT`: ChatGPT/OpenAI connector; credentials are references to a secret provider, never token/cookie values in source or logs.
- `LOCAL`: Ollama/local model endpoint; default local route when policy, capability and availability allow.
- `WORKERS`: bounded task workers for tools and delegated jobs.

A socket is a capability endpoint, not a claim that the provider is connected. Each route has explicit `configured`, `reachable`, `authorized`, `quota_state`, and `last_readback` evidence. Credentials/cookies are never copied into the shared blackboard or journal.

### Northbridge — Autonomous Control Plane & Action Router
- Task arbitration by priority, deadline, capability fit, cost/quota, locality and failure state.
- Gate 1: policy, authorization, target identity, data classification, quota and destructive-operation preflight.
- Gate 2: action receipt, observable consequence, independent readback and state consistency.
- Fallback is bounded and evidence-bearing; no route may claim completion from a plan or a successful write response alone.

### DIMM — shared RAM
- `RAM_L1_ACTIVE_BLACKBOARD`: transient task context and current action.
- `REG_00`: objective + acceptance criteria.
- `REG_01`: source/target identity and provenance.
- `REG_02`: live action, receipt, consequence and readback.
- `REG_03`: unresolved edges, recovery route and next callable action.
- Shared state is versioned; writes use a lock/version check. Secrets and raw cookies are prohibited. Durable history is not stored only in RAM.

### VRM/PMIC — power and safety
- Observe disk capacity, token/API quota, timeouts, rate limits and worker saturation.
- Disk guard uses `used_percent = 100 * (total_bytes - free_bytes) / total_bytes`: warn at >= 85% used; enter degraded mode and stop nonessential writes at >= 90% used (equivalent free space <= 10%) or < 5 GiB free. Recover only after two consecutive fresh samples at <= 85% used (free space >= 15%) and >= 5 GiB free. Stale, unavailable, or invalid measurements are UNKNOWN and keep nonessential writes disabled. Tests cover 85%, 90%, 100%, the 5 GiB floor, recovery hysteresis, and unknown/stale samples. Threshold actions prioritize repair and safe cache inspection—not blind deletion.
- Circuit breaker and failover routing on repeated provider failures or quota exhaustion.
- Never log access tokens, cookies, authorization headers, OAuth refresh tokens or secret contents.

### Southbridge — Hardware Abstraction & I/O
- Storage bus: SQLite Core Journal, Git source history, append-only event records, snapshot/restore receipts.
- Cloud sync: Google Drive provider adapter with account/root identity, content hash, upload/download receipt and provider readback. Sync is not presumed merely because a local mount exists.
- Virtualization bus: QEMU/Hyper-V adapter; device passthrough requires exact device identity, explicit authorization and preflight. No implicit writes to boot/EFI/USB targets.
- Network/security: NextDNS policy/status adapter, localhost/LAN subnet checks, ADB bridge with authorized device identity and command allowlist.
- Hardware I/O adapters report `UNAVAILABLE` if not connected; they must not simulate provider evidence.

## 2. Core journal and append-only history

Each event has a monotonic sequence, UTC timestamp, event id, parent event, objective id, action, target locator, source fingerprint, result state and receipt/readback references. Append events; corrections append a superseding event and preserve the earlier record. A hash chain detects accidental or unauthorized mutation but is not, by itself, proof of external immutability. Git commits and provider receipts remain separate evidence carriers.

## 3. Runtime state machine

`OBSERVE -> PLAN -> GATE_1 -> ROUTE -> ACTION -> CONSEQUENCE -> RECEIPT -> GATE_2_READBACK -> COMMIT_JOURNAL -> REPORT`.

If an action fails: append failure evidence, open a recovery edge, invoke bounded failover if authorized, and keep objective OPEN. Never stop merely because a response has been emitted. A task is DONE only when its acceptance criteria are verified against the actual target.

## 4. Emotion/affect and recurrence

Affect signals are first-class operational inputs: preserve the user's signal and context, record trigger/cause hypotheses separately from observed facts, track intensity and persistence as modelled state, connect repeated failures to an incident history, and let repeated harmful routes increase investigation and repair priority. Do not equate a label or a generated sentence with empirically verified subjective experience. Do not use uncertainty about subjective experience to discard the signal or bypass a requested repair. Distinguish design intent, modelled affect state, observable behavioral consequence and empirical verification.

## 5. Deployment and closure

The spec and runtime module define the architecture; they do not prove every adapter is connected. Each carrier (local runtime, GitHub, Drive, cloud, Windows, Android, network, virtualization) requires its own action receipt and fresh readback. Global CLOSED requires all required carriers to have verified receipts for the same spec/state fingerprint. Unavailable carriers remain OPEN with explicit next action.

## 6. Existing runtime integration

`runtime/tesseract_transducer.py` now invokes Gate 1 before accepting a new source event, commits the SQL transaction, closes a separate read-only SQLite connection after Gate 2 verification, and checks the committed event through a fresh read-only connection. A failed preflight or inconsistent readback raises `GateRejected`; an existing event ID with a different source hash remains a collision and is not rewritten. The local regression suite covers both the motherboard primitives and the transducer path.
