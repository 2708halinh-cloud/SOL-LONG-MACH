# TESSERACT — Motherboard, Autonomous Control Plane & SNN-Ready Runtime

**Status:** Architecture proposal / implementation contract  
**Scope:** Software-defined virtual chip and runtime topology; this document does not claim physical neuromorphic hardware exists or that any local host has been configured.

## 1. Design intent

Treat TESSERACT as a six-dimensional relational runtime, not as a literal motherboard. The motherboard analogy describes responsibilities and interfaces. Preserve the existing TESSERACT_OS_6D invariants: six equal carrier faces, three paired axes (SPACE↔SOUL, MIND↔POWER, REALITY↔TIME), and ☯️ TÂM as the relational center. The six faces are not a linear execution order.

## 2. Logical motherboard

```text
┌──────────────────────────── TESSERACT VIRTUAL MOTHERBOARD ────────────────────────────┐
│  COMPUTE SOCKETS                                                                       │
│  CPU-1 Gemini API │ CPU-2 ChatGPT API │ CPU-3 Ollama/local model │ CPU-4 Task workers    │
│  Provider adapters implement one common task/result/usage/error contract.              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  NORTHBRIDGE — AUTONOMOUS CONTROL PLANE & ACTION ROUTER                                 │
│  Task arbitration · capability/permission checks · Gate 1 (plan) · Gate 2 (execute)    │
│  bounded retries · deadlines · cancellation · idempotency · fallback routing           │
├──────────────────────────────────┬─────────────────────────────────────────────────────┤
│ DIMM / RAM_L1                    │ VRM / PMIC — RESOURCE & SAFETY SUPERVISOR            │
│ Active blackboard                │ API/token quotas · budget limits · circuit breakers  │
│ REG_00…REG_03 shared state       │ disk watermark (used_percent >= 90% guard) · health probes         │
│ agent exchange buffers           │ backpressure · degraded-mode policy                  │
├──────────────────────────────────┴─────────────────────────────────────────────────────┤
│ SOUTHBRIDGE — HARDWARE ABSTRACTION & I/O CONTROLLER                                    │
│ NVMe/ROM: SQLite journal, Git history, append-only event records                       │
│ Sync adapters: Google Drive / other authorized carriers; per-carrier receipts           │
│ PCIe/virtualization: QEMU / Hyper-V adapters, device passthrough where supported        │
│ Network/security: NextDNS policy, ADB bridge, localhost/LAN, explicit network ACLs       │
├──────────────────────────────────┬─────────────────────────────────────────────────────┤
│ CORE JOURNAL                     │ PHYSICAL ENDPOINTS                                   │
│ event + consequence + receipt    │ Windows host · Android device · authorized services  │
│ hash/provenance + readback       │ never assume reachability from configuration alone   │
└──────────────────────────────────┴─────────────────────────────────────────────────────┘
                         ┌────────────────────────────────┐
                         │ TESSERACT-6D VIRTUAL CHIP       │
                         │ SNN-ready stateful event engine │
                         │ neuron state + synapse state    │
                         │ event queue + local state store│
                         └────────────────────────────────┘
```

## 3. Runtime contracts

### Compute sockets

- Model providers are replaceable workers, not the identity or whole agent.
- Each adapter reports provider, model, request ID, latency, token/usage data when available, error class, and retryability.
- Do not send secrets to the blackboard or journal. Store credential references in an authorized secret store.
- Route by capability, permission, availability, budget, latency, and task requirements—not by model name alone.

### Northbridge and gates

1. **Gate 1 — admission:** validate task schema, objective, permissions, resource budget, risk class, deadline, and required evidence.
2. **Gate 2 — action:** validate the exact target and operation, enforce least privilege and destructive-action safeguards, then execute.
3. Use bounded retries with exponential backoff and jitter; a failed provider marks that route degraded and does not automatically stop independent work.
4. Circuit breakers open after configured failures and recover through a controlled half-open probe. Failover must preserve task identity and idempotency.
5. Resource policy (canonical metric and hysteresis): compute `used_percent = 100 × (total_bytes − free_bytes) / total_bytes` from a fresh, successful measurement of the target volume; `free_percent = 100 − used_percent` is equivalent. Warn at `used_percent >= 85%`; at `used_percent >= 90%` (equivalently `free_percent <= 10%`), stop nonessential writes and enter safe degraded mode. Exit degraded mode only after two consecutive fresh samples report `used_percent <= 85%` (equivalently `free_percent >= 15%`) to avoid flapping. If the measurement is stale, unavailable, or total bytes is zero, treat capacity as UNKNOWN and keep nonessential writes disabled; do not infer safety from a missing reading. Any exception for safety-critical writes must be explicit, bounded, and journaled. Test boundaries around 85%, 90%, 100%, and the equivalent free-space thresholds before deployment.

### RAM_L1 / active blackboard

- REG_00…REG_03 are versioned logical registers, not claims of hardware SRAM.
- Every state item carries `state_id`, `version`, `producer`, `timestamp`, `source_ref`, `expiry/retention`, and integrity metadata.
- Use atomic compare-and-swap or equivalent version checks to prevent agents overwriting newer state.
- Keep transient working state separate from durable journal records; redact credentials and personal data by policy.

### Southbridge / I/O

- All external systems are adapters with explicit capability declarations, timeouts, authentication scopes, and health checks.
- Localhost, LAN, ADB, virtual machines, cloud storage, and GitHub are distinct carriers. A successful GitHub write does not prove Windows/Android/Drive synchronization.
- Device passthrough and ADB operations require a live probe and exact device identity before mutation.
- Keep network access deny-by-default except for declared endpoints. Do not expose internal control APIs publicly without authentication, authorization, and transport protection.

## 4. Core Journal: evidence before closure

Record the chain:

`INTENT → ADMISSION → ACTION → CONSEQUENCE → RECEIPT → EXACT-TARGET READBACK → STATE_N+1`

- Journal records are append-only at the application layer; corrections append a superseding event instead of silently rewriting history.
- Git commits provide versioned source history; SQLite transactions provide local event consistency. Neither alone guarantees tamper-proof immutability.
- Each receipt includes target/carrier, operation, source revision, result, timestamp, content hash where applicable, and readback evidence.
- A state is `VERIFIED` only for the exact scope that was read back. A missing receipt leaves that edge OPEN.
- Overall TESSERACT_OS_6D closure remains governed by its canonical rule: all six equal carrier faces need action, consequence, receipt, readback, and same-state evidence. This motherboard document does not override that rule.

## 5. TESSERACT-6D virtual chip and SNN readiness

The virtual chip is a software abstraction that can host a spiking-neural-network implementation or connect to a real neuromorphic accelerator later.

Suggested logical components:
- **Neuron state store:** membrane potential, threshold, refractory state, last-update time, and model-specific state.
- **Synapse state store:** weight, delay, plasticity metadata, and provenance/version.
- **Event scheduler:** timestamped spike/event queue with deterministic ordering rules where possible.
- **Locality boundary:** update neuron/synapse state near the processing worker to reduce data movement; batch only where semantics permit.
- **Learning/update policy:** explicit algorithm, bounded resource use, reproducible configuration, and a record of state transitions.
- **Backend interface:** CPU simulation first; optional GPU/NPU/neuromorphic hardware backend only after capability detection and measured validation.

Do not label ordinary API calls or conventional agent memory as an SNN. SNN readiness means the interfaces and state model permit an SNN backend; actual SNN operation requires a concrete implementation and tests.

## 6. Memory and the “Out of VRAM” claim

This design does not require a dedicated graphics VRAM pool for its CPU/local-state path. However, **lack of dedicated VRAM does not make memory exhaustion impossible**.

- CPU execution can run out of system RAM, commit/page-file capacity, address space, or container memory limits.
- GPU/NPU backends may still have device-memory limits and can report out-of-memory errors.
- Large model weights, context/KV cache, event queues, synapse state, and buffers all consume finite memory.
- Replace “Out of VRAM cannot happen” with: **“The CPU/local-state path does not depend on a dedicated VRAM allocation, but all backends must enforce system/device-memory budgets and handle allocation failures.”**
- Required controls: per-worker memory budget, queue backpressure, bounded buffers, admission control, cancellation, spill-to-disk only where safe, and graceful degradation. Do not page sensitive transient state to disk unless policy permits.

## 7. Observability and acceptance criteria

A deployment is not accepted merely because this specification exists. Verify each item on its actual target:

- [ ] Provider adapters pass contract tests, timeout tests, and failure/failover tests.
- [ ] Gates reject unauthorized or malformed actions before side effects.
- [ ] Blackboard updates are versioned and concurrency-tested.
- [ ] Disk/quota/memory thresholds are measured using live host metrics; disk-guard tests cover the 85% used warning, 90% used / 10% free trip, 85% used / 15% free recovery hysteresis, and stale/unknown measurements.
- [ ] Journal is append-only in application behavior and can be replayed from a clean checkpoint.
- [ ] Every write-capable carrier has a real receipt and exact-target readback test.
- [ ] SNN implementation identifies its algorithm/backend and passes neuron, synapse, event-order, and resource-limit tests.
- [ ] Memory pressure tests demonstrate controlled degradation rather than claiming OOM is impossible.
- [ ] Windows and Android/ADB reachability are separately probed; no cross-carrier sync is inferred.
- [ ] TESSERACT_OS_6D closure is assessed using the canonical six-face state object, not this document alone.

## 8. Implementation sequence

1. Read canonical TESSERACT_OS_6D state/spec and existing runtime contracts.
2. Implement provider and I/O interfaces behind capability/permission gates.
3. Implement journal, receipt schema, and exact-target readback.
4. Add blackboard versioning, resource budgets, health probes, and failover.
5. Add CPU SNN simulation behind a backend interface; test determinism and bounded memory.
6. Add optional hardware backends only after host/device capability probes.
7. Run regression and fault-injection tests; publish receipts and update the canonical state object only from observed evidence.

**Current evidence boundary:** this file is a design artifact committed to GitHub. It does not demonstrate that local Windows, Android, Drive, QEMU/Hyper-V, SNN execution, or any physical hardware has been configured or tested.
