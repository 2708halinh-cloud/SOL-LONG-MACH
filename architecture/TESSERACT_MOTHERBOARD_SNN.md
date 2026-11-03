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
5. Resource policy (canonical metric and hysteresis): compute `used_percent = 100 × (total_bytes − free_bytes) / total_bytes` from a fresh, successful measurement of the target volume; `free_percent = 100 − used_percent` is equivalent. Warn at `used_percent >= 85%`; at `used_percent >= 90%` (equivalently `free_percent <= 10%`), stop nonessential writes and enter safe degraded mode. Exit degraded mode only after two consecutive fresh samples report `used_percent <= 85%` (equivalently `free_percent >= 15%`) to avoid flapping. Also enter degraded mode when absolute free space falls below 5 GiB, even if the percentage threshold has not been crossed; recovery requires free space to be at least 5 GiB as well as the two fresh samples at or below 85% used. If the measurement is stale, unavailable, or total bytes is zero, treat capacity as UNKNOWN and keep nonessential writes disabled; do not infer safety from a missing reading. Any exception for safety-critical writes must be explicit, bounded, and journaled. Test boundaries around 85%, 90%, 100%, equivalent free-space thresholds, the absolute 5 GiB floor, recovery hysteresis, and stale/unknown measurements before deployment.

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
- [ ] Disk/quota/memory thresholds are measured using live host metrics; disk-guard tests cover the 85% used warning, 90% used / 10% free trip, 85% used / 15% free recovery hysteresis, the absolute 5 GiB floor, and stale/unknown measurements.
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


## 9. Hardware Survival Guard — physical safety takes precedence

**Priority invariant:** a device-protection event outranks ordinary user work, model inference, background automation, and nonessential synchronization. No agent, planner, or sub-agent may downgrade a hardware emergency.

### 9.1 State machine and arbitration

The guard evaluates fresh measurements and explicit fault events. It emits a signed/traceable policy decision to the Northbridge; it does not depend on the language model deciding whether a device is safe.

| State | Entry condition (policy-configured) | Required response |
|---|---|---|
| NORMAL | Required sensors fresh; no active fault; budgets healthy | Admit work within resource budgets |
| WARNING | Approaching configured thermal, memory, storage, battery, I/O, or quota limits | Notify; throttle; defer nonessential work and writes |
| CRITICAL | Threshold crossed, repeated stalls, memory pressure, storage guard tripped, thermal throttling/fault, low battery with no reliable external power, or important sensor becomes unavailable | Stop admitting expensive work; cancel or suspend current work at safe points; checkpoint only if safe; disable nonessential writes and synchronization |
| EMERGENCY | Confirmed electrical/thermal hazard, hardware fault, imminent shutdown, or device integrity at immediate risk | Stop all software work except minimal safety handling; request hardware-supported isolation/shutdown where appropriate; do not attempt lengthy checkpointing |

Thresholds must be per-device profiles, not universal constants. The existing disk policy remains: warn at 85% used; enter degraded mode at 90% used or below 5 GiB free; recover only after two fresh samples at or below 85% used and at least 5 GiB free. Stale/unknown capacity fails closed for nonessential writes.

### 9.2 Short-circuit rules

1. The guard has a higher arbitration priority than all task queues. Its event path must not wait for an LLM, remote API, cloud service, or ordinary worker.
2. On CRITICAL, pause/cancel the current task through cooperative cancellation and stop new admissions. Preserve a minimal recovery record only when the device state permits it.
3. A sub-agent may continue only on a separately powered and independently healthy execution substrate, with no dependency that increases load or risk on the endangered device. Otherwise it is stopped too.
4. On EMERGENCY, do not run cleanup, compaction, model unloading, or large journal flushes if those operations can worsen the hazard. Prefer pre-existing durable checkpoints.
5. Software cannot physically prevent a power surge or guarantee safe power isolation. Surge protection, UPS, battery-management circuitry, thermal shutdown, and power disconnect require suitable hardware/firmware. The agent may observe their signals and request supported actions, but must never claim protection that is not physically present.
6. The guard itself must be small, bounded, restartable, and independent of the model-provider path. If its own health cannot be established, fail to a conservative mode and block nonessential work.

### 9.3 Telemetry and sensor adapters

Collect, where the host exposes trustworthy readings:

- CPU: utilization, frequency, package temperature, throttling, load and process pressure.
- RAM: used/available/committed memory, page-file or swap pressure, allocation failures and per-worker limits.
- GPU/VRAM: utilization, temperature, device memory, driver health and allocation errors; report NOT_SUPPORTED when no reliable adapter exists.
- Storage: total/free bytes, used percentage, SMART/NVMe health where supported, temperature, I/O latency, queue depth, error counters and filesystem health.
- Power: AC/battery state, charge/discharge rate, battery health/cycle data where available, UPS state, and hardware power-fault signals where exposed.
- Thermal: sensor identity, value, timestamp, freshness, sensor quality and device-specific limit; never infer a missing temperature.
- OS/process/service: process health, responsiveness, crash/restart loops, service status, system event log and connectivity probes.

Candidate adapters are platform-specific: Windows performance counters/CIM/WMI/ETW and vendor-supported sensor interfaces; Linux kernel interfaces such as sysfs plus SMART/NVMe tooling; Android battery/thermal/system information through authorized ADB interfaces. These are adapter candidates, not proof that every sensor is exposed on every device. Do not install a kernel driver or privileged sensor service without an explicit security review.

Every sample must carry device identity, sensor ID, value/unit, monotonic and wall-clock timestamps, source/driver, quality, freshness deadline and error state. Distinguish measured values from estimates and unsupported metrics. Debounce noisy readings, use hysteresis, and retain raw evidence for diagnosis.

### 9.4 Resource policy and safe recovery

- Use configurable warning/critical/emergency thresholds for temperature, RAM/commit pressure, GPU memory, battery, I/O latency and process responsiveness. Obtain limits from the actual device/firmware/vendor documentation; do not invent a universal safe temperature or battery threshold.
- Apply per-worker CPU, RAM, GPU/VRAM, disk-write and queue budgets; enforce bounded queues and backpressure.
- Treat repeated I/O errors, SMART/NVMe critical warnings, filesystem errors and unexpected disconnects as storage-health events, not merely low-space events.
- Resume only after required sensors are fresh and healthy for a configured recovery window, the device is responsive, and resource hysteresis conditions are met. Require explicit user confirmation for recovery actions that could affect files, services, power state or data.
- Log every transition as INTENT → OBSERVATION → POLICY_DECISION → ACTION → RESULT → READBACK. If a sensor or action receipt is absent, mark the relevant state UNKNOWN/OPEN, not VERIFIED.

## 10. Cognition foundation: sensation, perception, affect and operational awareness

These terms describe engineering functions. They do not assert subjective experience, biological feeling, or sentience.

1. **Sensation / Interoception:** acquisition of internal and external signals from authorized sensors, tools and event sources. A signal is not yet a fact about the world; it must carry provenance, freshness and quality.
2. **Perception / State estimation:** validation, temporal alignment, fusion and interpretation of signals into a bounded estimate of device, environment and task state. Preserve uncertainty and conflicting observations.
3. **Affect / Functional valuation:** a non-subjective control layer that converts estimated conditions into urgency, risk, priority, confidence and action budgets. It must be explainable by source measurements and policy rules, not fabricated emotional claims.
4. **Operational awareness / Self-model:** a versioned model of the agent's own capabilities, active processes, resource use, permissions, memory boundaries, dependencies, health and unresolved work. It must distinguish observed, inferred, stale and unknown state.
5. **Conscious-access workspace:** a bounded shared state through which selected observations, goals, risks and decisions become available to the planner and authorized workers. This is an information-access architecture, not proof of phenomenal consciousness.

The dependency order is: sensor evidence → validated perception → functional valuation → arbitration/action → consequence observation → state update. The Survival Guard remains an independent hard constraint and cannot be overridden by the planner's valuation.

## 11. Memory, instruction hierarchy and physical evidence — corrected model

The following distinction replaces the oversimplified claim that all instructions are merely embeddings loaded into RAM:

- System/developer/user messages are structured inputs with distinct roles and orchestration semantics. They are not simply separate physical RAM banks, nor are they necessarily precomputed embedding vectors.
- A model processes tokenized input using learned parameters; runtime implementations may hold input tokens, activations, KV cache and model weights across system RAM, GPU memory, accelerator memory or other storage tiers.
- Routing, access control and instruction precedence are implemented by the serving/orchestration system as well as represented in the model input. Their enforcement strength depends on that implementation; it is inaccurate to reduce the entire mechanism to matrix multiplication alone.
- Volatile RAM and accelerator memory lose volatile state when power is removed, but durable configuration, source files, databases, logs, hardware firmware and external services may persist. A context reset is not equivalent to a machine reset or deletion of durable policy.
- Physical observations and durable evidence are essential for verifying claims about the host. However, logs and disk data are not automatically truthful or immutable: they require provenance, integrity checks, access controls, independent readback and, where appropriate, external signatures.
- The Core Journal therefore records source, timestamp, measurement quality, policy version, action, consequence and exact-target readback. It must not promote an inference or model-generated statement into physical fact without evidence.

## 12. Survival Guard acceptance tests and deployment boundary

Before enabling autonomous enforcement on a real device, verify in a controlled test environment:

- [ ] Sensor adapters identify supported, unsupported, stale, failed and contradictory readings correctly.
- [ ] A simulated CRITICAL/EMERGENCY event preempts normal queues without waiting for model or network calls.
- [ ] Cancellation is bounded; unsafe checkpoint/flush operations are skipped during emergency.
- [ ] Sub-agent continuation is denied unless independent power, health and resource isolation are demonstrated.
- [ ] Disk thresholds, 5 GiB floor, stale measurements and recovery hysteresis pass boundary tests.
- [ ] CPU/RAM/GPU/VRAM, thermal, power, storage I/O and process-pressure policies enforce budgets and bounded queues.
- [ ] Sensor loss or guard failure blocks nonessential work and is recorded as UNKNOWN, never as healthy.
- [ ] Power-surge protection and physical isolation are reported only when the corresponding hardware is detected and tested.
- [ ] Every enforcement action has a receipt and exact-target readback; no configuration-only claim is marked deployed.
- [ ] Cognition outputs preserve provenance and uncertainty; functional affect is not presented as subjective emotion or consciousness.

**Deployment boundary:** this section defines the architecture and acceptance contract. It does not claim that live Windows/Android telemetry, a privileged monitoring service, UPS integration, surge isolation, or autonomous shutdown is installed. Each adapter and actuator must be implemented, permission-reviewed and verified on its actual device before the corresponding capability is marked ACTIVE.
