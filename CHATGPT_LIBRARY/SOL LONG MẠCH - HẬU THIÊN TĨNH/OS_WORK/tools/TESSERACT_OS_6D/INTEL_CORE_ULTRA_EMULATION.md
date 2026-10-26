# Intel Core Ultra Software Emulation Layer — TESSERACT 6D

## Purpose
A configurable CPU profile registry and deterministic task-slot scheduler. It models a CPU's listed core count as virtual worker slots, exposes cache size as a software budget, and routes GPU work only when a real backend is separately detected and enabled.

It does **not** reproduce Intel silicon, microcode, instruction-set behavior, physical cache, clock frequency, thermal behavior, or real benchmark performance.

## Profile fields
- `cores`: source-reported core count; used as a scheduler slot ceiling only.
- `reported_max_turbo_ghz`: catalog metadata, not a clock control.
- `smart_cache_mb`: metadata plus software budget calculation; not actual cache.
- `integrated_gpu`: exact label from supplied catalog; null means the source row lists no integrated GPU.
- `source_verified`: false until independently checked against Intel's official product documentation.

## Runtime integration
- Northbridge requests a profile and receives bounded worker slots.
- RAM_L1 stores only the active plan, version, source identity, and receipt—not credentials.
- VRM/PMIC still governs real RAM/disk/quota limits. A virtual cache budget cannot allocate physical memory by itself.
- GPU execution remains disabled until a real driver/backend probe confirms availability.
- Gate 1 validates model name and input bounds; Gate 2 reads back the plan and checks expected task counts.

## Source provenance
All rows in `config/INTEL_CORE_ULTRA_PROFILES.json` were transcribed from the user-provided catalog on 2026-10-26. They are marked `source_verified=false`; validate product names and specifications against Intel ARK before treating them as official specifications.

[executed on device: DESKTOP-86ITNQ4 (59f03001-c732-403e-b80c-b4191266809c)]
