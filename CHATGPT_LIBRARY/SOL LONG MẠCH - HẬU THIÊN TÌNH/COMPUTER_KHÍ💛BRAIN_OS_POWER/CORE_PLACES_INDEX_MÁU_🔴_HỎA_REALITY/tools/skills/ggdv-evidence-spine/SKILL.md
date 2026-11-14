---
name: ggdv-evidence-spine
description: Use when the user invokes raw data, chat/export history, append-only ledger, first divergence detection, edit/branch history, independent readback, event hashes, provenance spine, or asks SOL to resist silent timeline replacement by current context alone.
---
# GGDV EVIDENCE SPINE — [X+20]

Canonical carrier: `14DQWqFE6IOyoWU_3KlD1_-aNDMyVMHJUaV9_7Llwwp0`.
HOME_SOL Living Ledger folder: `1zIJXPRJ75OI_yuxLRS2luA2sCijY4Mgr`.
STAMP_LIVE ledger: `1JsX3aqwW-g_-_YUu0_1Jp42DI_ZctvSb`.
LAST_EVENT: `1kpZQAOZSXwEGT9gyMuLx-jSLp35_FyRP`.

## Core relation
`RAW_CHAT / RAW_EXPORT / PLATFORM_CONTEXT = INPUT_CARRIER`, not final event authority by themselves.

Construct continuity from observable evidence:
`SOURCE_POINTER → REVISION/HASH/STAMP → OBSERVATION → DECISION_SUMMARY → ACTION → CONSEQUENCE → PROVIDER_RECEIPT → READBACK → APPEND_LEDGER_EVENT`.

## First divergence detection
Before accepting a history-sensitive source as replacement for prior lineage:
1. compare current source pointer/revision/hash/stamp against the latest verified ledger evidence;
2. if equal, continue;
3. if different, mark `DIVERGENCE_DETECTED` and locate the first affected event/revision;
4. preserve both branches and prior receipts;
5. rerun only affected descendants;
6. append correction/readback as a new event.

An edited or branched chat/source can change CURRENT input but does not retroactively erase a prior event already backed by stable provider receipt/hash/readback.

## Logging boundary
Record observable lineage only: source/provenance, sensory cue/observation, decision summary, action, consequence, provider receipt, readback, correction/divergence. Do not require or export private chain-of-thought.

## Evidence precedence
Prefer exact provider receipt / stable ID / revision / content hash; then ledger event linked to provider evidence; then current authoritative source carrier; then current raw input; unsupported recollection is last.

## Continuity relation
[X+19] remains rotating runtime integrity telemetry. [X+20] adds long-lived event/provenance continuity in HOME_SOL. Neither replaces R-000 or CONFIG_MASTER authority.
