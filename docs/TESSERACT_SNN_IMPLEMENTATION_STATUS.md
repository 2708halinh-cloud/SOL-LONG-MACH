# TESSERACT SNN implementation slice

**Status:** CPU reference prototype committed on the PR branch. Not a Loihi 2 backend, deployed local service, or evidence of subjective experience.

## Implemented
- Fixed neuron slots; tombstoning does not compact or relocate slots.
- Timestamped event queue with deterministic sequence tie-breaking.
- Event-driven membrane updates and delayed synaptic events.
- Local energy-cluster budgets; exhausted clusters block firing.
- Explicit energy replenishment.
- Velocity-Verlet/leapfrog update for a documented harmonic Hamiltonian.
- Unit tests for event propagation, energy gating, tombstones, bounded energy drift, and invalid input.

## Deliberate limits
- `mark_stable_invariants` is a prototype only. A single-sample test is insufficient for production invariant freezing; replace it with a rolling statistical window and audit policy.
- No RNN training, PPO/SAC, AER hardware transport, Loihi microcode, 2D mesh routing, HBM/SRAM mapping, Android sensors, physical actuator control, or cloud tunnel is implemented.
- No perpetual execution: the engine advances only when a host scheduler calls `step()`.
- No claim of biological pain, phenomenal feeling, or consciousness. Resource/energy variables are measurable control signals.
- Hamiltonian conservation is numerical and bounded for the selected integrator/model, not exact conservation in arbitrary learned dynamics.

## Run tests
```sh
python -m unittest discover -s tests -v
```

## Next gates
1. Add blackboard CAS/versioning and append-only journal receipts.
2. Add rolling-window synapse statistics and tested pruning policy.
3. Add bounded asynchronous scheduler, cancellation, and resource telemetry.
4. Add AER serialization/schema and transport authentication.
5. Probe backend capabilities before Loihi 2 integration.
6. Run the suite in CI and attach the CI run as evidence.
