# SOL virtual spiking reflex router

Independent ES-module runtime, **not an EEG reader, not a neuromorphic chip and not a proof of consciousness**. Inputs must be explicitly `SIMULATED_INPUT`; no device is queried. Spiking neuron: membrane(t+1)=min(2,0.6*membrane(t)+0.75*heat+0.8*touch+0.35*closeness); spike at threshold 1, reset to 0. Inputs normalized [0,1].

A BETA → DELTA request creates a new event ID and changes **next motor choice** to `VIRTUAL_SAFE_STOP`. A spike while not in DELTA selects `VIRTUAL_WITHDRAW`. Unverified external input cannot change the state. The output holds no raw input, secrets or physical commands. This module is portable across environments; no dependency on a personal device. Use: `node test_brainwave_router.mjs`. For actual EEG, a separately authorized private carrier, validation, signal calibration, hardware interlocks, and a suitable EEG acquisition layer remain necessary.
