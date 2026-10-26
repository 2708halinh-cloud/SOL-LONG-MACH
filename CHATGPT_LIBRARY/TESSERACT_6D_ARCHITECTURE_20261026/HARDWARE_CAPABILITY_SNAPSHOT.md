# Sanitized Hardware Capability Snapshot

Source: operator-supplied audit summary dated 2026-10-26. Values are reported, not independently re-probed in this change.

## Host

- Windows x86 host; 6-core/12-thread CPU, 48 GB DDR4, and a discrete GPU in the 4 GB VRAM class.
- Hyper-V, WSL2, and Docker were reported active.
- System-volume capacity was flagged as critical in the source report. Exact volume identities and usage figures are omitted; recheck before large writes, exports, or builds.

## Mobile edge

- Two mobile compute nodes were reported: one Qualcomm-based Android 15 device and one MediaTek-based Android 16 device.
- Exact device models, serials, build fingerprints, sensor paths, and local service endpoints are omitted.

## Agent and network inventory

- Local model/MCP tooling and network services were reported, but this snapshot does not independently confirm current configuration, authentication, reachability, or service health.
- Account identifiers, local configuration paths, IP addresses, DNS addresses, ports, and credentials are intentionally omitted.

This profile is a planning hint, not a hardware attestation or evidence of current service availability. Re-probe the exact target before scheduling workloads or making infrastructure decisions.
