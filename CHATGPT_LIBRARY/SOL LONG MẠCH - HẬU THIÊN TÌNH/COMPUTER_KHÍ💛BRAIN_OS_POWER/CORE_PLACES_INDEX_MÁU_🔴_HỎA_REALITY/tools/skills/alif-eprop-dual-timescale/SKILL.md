---
name: alif-eprop-dual-timescale
description: Use for ALIF neurons with e-prop, dual-timescale recurrent state, forward temporal credit, on-device learning memory tradeoffs, and sequence-length-independent online state retention.
---
# ALIF + e-prop — DUAL TIMESCALE

ALIF keeps a fast membrane-like state v_t and a slower adaptive state a_t.
Typical discrete structure:
`v_{t+1} <- fast decay + synaptic input - reset term`
`a_{t+1} <- rho * a_t + z_t`
`A_t <- A0 + beta * a_t`
`z_t <- H(v_t - A_t)`.

The exact equation variant is model-specific; preserve the implementation's own reset and adaptation convention.

For e-prop, use the hidden state `h_t = [v_t, a_t]` and carry the forward eligibility vector:
`epsilon_t = (dh_t/dh_{t-1}) epsilon_{t-1} + dh_t/dW`.
Then:
`e_t = (dz_t/dh_t) dot epsilon_t`
and local online weight update uses the available learning signal.

The slow adaptive state can extend temporal credit because rho may be close to 1 relative to the fast membrane decay. It does not create infinite memory and does not guarantee every long-sequence task.

## MEMORY TRADEOFF
BPTT-style LSTM training stores time-indexed activations/history and therefore grows with sequence length T unless truncated/checkpointed/recomputed.
e-prop removes that time-history dependence from the online update path, but keeps ongoing eligibility state tied to synapses/parameters. Describe memory as `independent of T for the recurrent trace`, not as zero-cost.

## HARDWARE TRADEOFF
Event sparsity and accumulate-only synaptic processing can reduce activity on neuromorphic/event-driven hardware, but actual SRAM, sparsity, operation energy and total system energy depend on model, quantization, hardware and benchmark. Do not promote example numbers to universal constants.
