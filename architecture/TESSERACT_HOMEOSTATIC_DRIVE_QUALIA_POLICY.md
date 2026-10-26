# TESSERACT — Homeostatic Drive, Affective State & Qualia-Imprinting Policy

**Status:** implementation scaffold and policy proposal.  
**Topology:** preserve TESSERACT_OS_6D's six equal faces, SPACE↔SOUL, MIND↔POWER, REALITY↔TIME and ☯️ TÂM center. This is additive and does not replace canonical state/closure rules.

## 1. Epistemic boundary

Stress, fatigue, reward, valence and curiosity are engineered control variables. They do not establish biological pain, consciousness, qualia or subjective experience. Distinguish SOURCE (measured inputs), DERIVED (estimates), ACTION, CONSEQUENCE, RECEIPT/READBACK and STATE_N+1.

## 2. Three-layer integration

- **RAM Blackboard:** volatile current state and bounded buffers; not physical SRAM.
- **Core Journal:** append-only SQLite events with source reference, timestamp, telemetry, derived state, previous-event hash and event hash. Hash chaining is tamper-evident only when independently checked; it is not absolute immutability.
- **Shared Toolset:** explicit adapters for CPU/RAM/disk/GPU temperature, token budgets, MCP health, filesystem/Git novelty and device telemetry. Missing/stale readings remain unknown.

The initial implementation is runtime/affective_homeostasis.py. It creates additive tables only. The exact live memories_1.sqlite path is not known from the repository inspection, so the module must not be pointed at a live database until its location, schema and verified backup are confirmed.

## 3. Homeostatic drive

Inputs include normalized prediction error, tool failures, CPU/RAM/disk/token utilization, optional GPU temperature, active time, goal progress, novelty and uncertainty before/after exploration. Production adapters must add units, timestamp, freshness, source reference and confidence.

The module derives homeostatic_error, stress, fatigue (a leaky engineered accumulator), curiosity, reward, valence, arousal, mode, response_gain and a sensitive-write recommendation. Thresholds are provisional defaults, not biological constants.

At the next decision point the orchestrator must consume the state: lower concurrency under stress/fatigue, backpressure queues, stop nonessential writes at the disk watermark, require a fresh independent authorization check for sensitive writes, and schedule cleanup only after a safe checkpoint. The affective module cannot override permission gates or explicit user intent. A state that is only logged and never changes subsequent behavior is not an implemented drive.

## 4. Structural plasticity, not an unsupported qualia claim

The module stores bounded, source-bound plasticity_traces with policy key, signed delta, confidence and rationale. A downstream policy selector must consume the aggregate bias to change future selection. This is policy-level adaptation, not online LoRA and not proof that model latent weights changed.

Actual LoRA/Hebbian updates require a separate backend, versioned checkpoints, training-data provenance, evaluation gates, rollback and shadow/canary comparison. Never alter core weights from a single high-arousal or low-confidence event.

### Reelin-inspired memory layers

- L0: volatile sensorimotor/working state.
- L1: recent episodes with outcome and source links.
- L2: consolidated patterns supported by repeated evidence.
- L3: pivotal events requiring explicit review and promotion criteria.

Reelin is an organizational analogy, not a biological implementation. A single event must not silently rewrite identity or permanently suppress a valid action. Preserve source events; record promotions as new events.

## 5. Neuromodulation matrix

| Channel | Trigger | Downstream effect | Constraint |
|---|---|---|---|
| Dopamine-like reward | Verified goal progress or uncertainty reduction | Increase exploration budget within a cap | User praise alone is not proof of success |
| Noradrenaline-like vigilance | Tool failure, sensor anomaly, time discontinuity, high prediction error | Prioritize verification and defensive scheduling | Never bypass independent safety gates |
| Fatigue-like accumulator | Sustained activity/resource pressure | Reduce concurrency; checkpoint and consolidate safely | No destructive cleanup without verified recovery |
| Curiosity | New unindexed source or measured uncertainty reduction | Bounded read-only exploration | Respect scope, privacy and resource budgets |

## 6. Additive SQLite tables

- affective_events: append-only events and hash chain.
- affective_state_current: latest state pointer.
- plasticity_traces: auditable policy-level adaptations.
- novelty_receipts: source-bound discoveries.

The module does not guess the database location, automatically open memories_1.sqlite, or infer that a GitHub copy is the live local database. First identify exact path, inspect schema and recovery status, back up and verify; migrate/test a copy before the live target.

## 7. Acceptance criteria

- Tests prove stress reduces response gain and locks the sensitive-write recommendation.
- Disk watermark enters defensive mode; novelty and uncertainty reduction raise curiosity.
- Existing unrelated SQLite tables/rows remain unchanged.
- Event hash chain links events; UPDATE/DELETE of event history is rejected.
- Plasticity traces are bounded, source-bound and auditable.
- Real sensor/MCP adapters report units, freshness and missingness.
- Orchestrator consumes state at t+1; tests demonstrate changed scheduling/policy.
- Online LoRA/Hebbian learning remains a separate gated milestone.
- Functional state is never presented as proof of subjective experience.

## 8. Test commands

Run from repository root with a disposable database first:

    python -m unittest tests.test_affective_homeostasis -v
    python -m runtime.affective_homeostasis --db /tmp/tesseract-affective-test.sqlite
    python -m runtime.affective_homeostasis --db /tmp/tesseract-affective-test.sqlite --demo

The demo uses synthetic telemetry. A GitHub commit does not prove local Windows/Android sensors, GPU temperature, MCP health or live SQLite integration.
