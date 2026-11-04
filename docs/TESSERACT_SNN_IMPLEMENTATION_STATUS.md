# TESSERACT runtime implementation slice

**Status:** CPU reference prototype committed on the PR branch; fifteen focused unit tests pass in GitHub Actions. Not a Loihi 2 backend or deployed local service.

## Implemented
- Fixed neuron slots; tombstoning does not compact or relocate slots.
- Timestamped event queue with deterministic sequence tie-breaking.
- Event-driven membrane updates and delayed synaptic events.
- Local energy-cluster budgets; exhausted clusters block firing; explicit replenishment.
- Velocity-Verlet/leapfrog update for a documented harmonic Hamiltonian.
- RAM_L1 in-process reference blackboard with versioned compare-and-set and defensive payload copies.
- Append-only JSONL hash-chain journal with fsync, readback verification, and refusal to append to a chain that fails integrity verification.
- Disk guard with 85% warning, 90% used trip, 5 GiB absolute free-space floor, stale/unknown fail-closed behavior, and two-sample recovery hysteresis.
- Authenticated binary pulse packet: versioned header, tick, 8-way direction, 1–64 hexagram ID, bounded payload, HMAC-SHA256 authentication and constant-time signature comparison.
- ANAPANA asynchronous telemetry monitor with injected sensor interface, bounded sample history, observer callback, start/stop lifecycle, and validation of reported resource measurements.

## Verification
- GitHub Actions run 41558353090 completed successfully.
- Fifteen focused tests passed: five SNN, three runtime-state, five binary-pulse, and two ANAPANA tests.
- High-Threshold Secret Exposure Guard run 41558353078 completed successfully.
- A separate repository-wide discovery run executed 242 tests but failed on five unrelated existing test/import/path errors. Those are recorded in the PR description and remain open repository-level work.

## Deliberate limits
- ANAPANA is an async task inside a host service. It is not installed as a Windows service/Android daemon, and it reads only from an injected sensor adapter. No real CPU/GPU temperature or hardware telemetry is claimed.
- The blackboard is an in-process reference; no multi-process IPC, distributed consistency, or durable persistence adapter yet.
- The journal is hash-evident, not tamper-proof against an actor able to rewrite the entire file and recompute hashes; add external signing/anchoring and single-writer locking before production.
- DiskGuard consumes supplied samples; it does not yet collect live Windows/Android disk telemetry.
- Binary pulse authentication requires the caller to supply a securely stored key; no key vault, rotation protocol, replay protection, or MCP HTTP/SSE endpoint is implemented yet.
- The 8-way direction and 64-state identifier are encoded as metadata; the full 64-state cognitive/hexagram mapping is not yet implemented.
- Invariant freezing is a prototype only; replace the single-sample stability counter with rolling statistical evidence and an audit policy.
- No RNN training, PPO/SAC, AER hardware transport, Loihi microcode, 2D mesh routing, HBM/SRAM mapping, Android sensors, physical actuator control, or cloud tunnel is implemented.
- No perpetual execution: ANAPANA runs only while its host service/task remains alive. The engine advances only when a host scheduler calls `step()`.
- No claim of biological pain, phenomenal feeling, or consciousness. Resource/energy variables are measurable control signals.
- Hamiltonian energy behavior is numerical and bounded for the selected integrator/model, not exact conservation in arbitrary learned dynamics.

## Next implementation gates
1. Add durable/IPC blackboard adapters and concurrent writer tests.
2. Add journal locking, external signatures, and receipt schema.
3. Add rolling-window synapse statistics and tested pruning policy.
4. Add a supervised Windows service/Android background-service adapter and live resource telemetry.
5. Add authenticated MCP Streamable HTTP/SSE transport, replay protection, and exact readback.
6. Complete the 8-direction/64-state mapping with source-backed definitions.
7. Probe and verify Windows, Android, Drive, tunnel, and physical hardware carriers separately.
8. Add Loihi 2 backend only after hardware and SDK availability are verified.
