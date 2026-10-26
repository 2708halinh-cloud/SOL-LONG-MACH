# Intel Core Ultra Software Emulation Layer
- Cores: virtual scheduling slot ceiling only, not an assertion about P/E core topology.
- Smart Cache: metadata and software budget only; no actual cache allocation.
- Max Turbo: metadata only; no frequency control.
- GPU: catalog label only; no GPU work runs until real hardware/backend detection.
- Source: user-provided catalog, 2026-10-26; unverified against Intel ARK.
