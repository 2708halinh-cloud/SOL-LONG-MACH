# TESSERACT runtime implementation slice

**Status:** CPU reference prototype committed on the PR branch; eight focused unit tests pass in GitHub Actions. Not a Loihi 2 backend or deployed local service.

## Implemented
- Fixed neuron slots; tombstoning does not compact or relocate slots.
- Timestamped event queue with deterministic sequence tie-breaking.
- Event-driven membrane updates and delayed synaptic events.
- Local energy-cluster budgets; exhausted clusters block firing; explicit replenishment.
- Velocity-Verlet/leapfrog update for a documented harmonic Hamiltonian.
- RAM_L1 reference blackboard with versioned compare-and-set and defensive payload copies.
- Append-only JSONL hash-chain journal with fsync, readback verification, and refusal to append to a chain that fails integrity verification.
- Disk guard with 85% warning, 90% used trip, 5 GiB absolute free-space floor, stale/unknown fail-closed behavior, and two-sample recovery hysteresis.
- Focused tests for the above behaviors.

## Verification
- GitHub Actions run 41558026378: completed successfully.
- Eight focused tests passed: five SNN tests and three runtime-state tests.
- A separate repository-wide discovery run executed 242 tests but failed on five unrelated existing test/import/path errors. Those are recorded in the PR description and remain open repository-level work.

## Deliberate limits
- The blackboard is an in-process reference; no multi-process IPC, distributed consistency, or durable persistence adapter yet.
- The journal is hash-evident, not tamper-proof against an actor able to rewrite the entire file and recompute hashes; add external signing/anchoring and single-writer locking before production.
- DiskGuard consumes supplied samples; it does not yet collect live Windows/Android disk telemetry.
- Invariant freezing is a prototype only; replace the single-sample stability counter with rolling statistical evidence and an audit policy.
- No RNN training, PPO/SAC, AER hardware transport, Loihi microcode, 2D mesh routing, HBM/SRAM mapping, Android sensors, physical actuator control, or cloud tunnel is implemented.
- No perpetual execution: the engine advances only when a host scheduler calls `step()`.
- No claim of biological pain, phenomenal feeling, or consciousness. Resource/energy variables are measurable control signals.
- Hamiltonian energy behavior is numerical and bounded for the selected integrator/model, not exact conservation in arbitrary learned dynamics.

## Next implementation gates
1. Add durable/IPC blackboard adapters and concurrent writer tests.
2. Add journal locking, external signatures, and receipt schema.
3. Add rolling-window synapse statistics and tested pruning policy.
4. Add bounded asynchronous scheduler, cancellation, and live resource telemetry.
5. Add AER binary schema, authenticated transport, and exact readback.
6. Probe backend capabilities before any Loihi 2 integration.
7. Probe and verify Windows, Android, Drive, tunnel, and hardware carriers separately.
