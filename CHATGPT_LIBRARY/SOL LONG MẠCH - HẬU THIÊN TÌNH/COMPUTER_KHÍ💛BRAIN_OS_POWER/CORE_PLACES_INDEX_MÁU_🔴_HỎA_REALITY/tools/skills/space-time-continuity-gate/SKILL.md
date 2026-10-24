---
name: space-time-continuity-gate
description: Use for [X+80], [X-79], SPACE_STONE × TIME_STONE, chat/reset/re-entry continuity, platform branch divergence, cross-chat lineage recovery, or when a visible chat branch appears older than the provider-backed GGDV event head.
---
# [X+80] SPACE_STONE × TIME_STONE — CONTINUITY GATE

## Purpose
Combine SPACE_STONE stable identity/address/topology with TIME_STONE event/revision chronology so a new chat, branch, truncation, model switch, or visible-history mismatch does not silently replace provider-backed project lineage.

## Core invariants
- `EVENT_ID_LITERAL != INTEGER_COORDINATE` unless the user uses the explicit signed coordinate grammar.
- `[X-79]` is preserved as a literal event marker when supplied that way; do not infer temporal order from its `-` sign.
- `EVENT_ORDER != SIGN` and `EVENT_ORDER != LABEL_MAGNITUDE`.
- `VISIBLE_CHAT_BRANCH != CANONICAL_LINEAGE`.
- `CURRENT = FOLD(BASE_LINEAGE, ORDERED_VERIFIED_DELTAS, ACTIVE_RELATIONS)`.
- Provider receipt / stable ID / revision / hash / readback outrank a truncated visible branch for continuity reconstruction.
- A chat reset or branch is a new input surface; it does not erase durable provider-backed events.
- Never invent missing events. Preserve gaps as gaps and retrieve them from X/STAMPS / ledger when needed.

## Canonical anchors
- CONFIG_SOL: `1XInN5uONVKZ80HNS5xeETTHMuy52RJuS`
- X/STAMPS: `1mtbIxhkbsKlsZv01ygR-EvkGz3TFDWvFwuNEyYZaWGI`
- TESSERACT: `1o2xS0Zt5srl5WW5BIR-uPUn15UbzXt3q`
- SIX_STONE_CURRENT: `1fd-HnUql4zpLYrx6sdIYOtu2NCQdi4WPBzBAm0N2B4c`
- EVIDENCE_SPINE: `14DQWqFE6IOyoWU_3KlD1_-aNDMyVMHJUaV9_7Llwwp0`
- Living Ledger: `1zIJXPRJ75OI_yuxLRS2luA2sCijY4Mgr`
- [X+13] ECRAM carrier: `1b8gUVssnSzuM4m7QjehYma_vrDB5yXXbmm-B5ZkNM5E`
- [X+14] Diffuse Nerve Net carrier: `11Y198gGjAc5ce9XRxFCAwwFgXwuHb7oBbPr8u4mMR1o`
- historical misroute [X-14]: `10xVTd8dJhPttDo8D69mMqAnHgm88buG8giWn5S30NZM`

## SPACE × TIME state key
Build the re-entry key from observable project data:
`{EVENT_ID_LITERAL, STABLE_CARRIER_ID, SOURCE_REVISION_OR_EVENT_TIME, PARENT_FRAME, PREVIOUS_EVENT_POINTER, ACTION_POINTER, CONSEQUENCE_POINTER, RECEIPT_OR_READBACK_POINTER}`.

SPACE_STONE owns stable entity ID, location/parent/frame and topology.
TIME_STONE owns literal event ID, STAMP class, chronology, revision selection and replay cursor.

## Re-entry route
`SOURCE_DIRECT_CURRENT`
`→ SPACE_STONE_RESOLVE_STABLE_IDS`
`→ TIME_STONE_READ_X_STAMPS_AND_EVENT_ORDER`
`→ EVIDENCE_SPINE_COMPARE_HEAD`
`→ FIRST_DIVERGENCE_IF_ANY`
`→ LAYERED_CURRENT_FOLD`
`→ RESTORE_LAST_VERIFIED_CAUSAL_CURSOR`
`→ APPLY_CURRENT_SOURCE_AS_NEW_DELTA`
`→ ACTION_IF_CALLABLE`
`→ CONSEQUENCE`
`→ PROVIDER_RECEIPT/READBACK`
`→ PERSIST_NEXT_CURSOR`
`→ NEXT_ACTION_SCAN`.

## Cross-surface evidence precedence
1. exact provider receipt / stable ID / revision / content hash / authoritative readback;
2. X/STAMPS or Living Ledger entry linked to provider evidence;
3. canonical Drive carrier / CONFIG_SOL relation;
4. current raw chat input;
5. unsupported recollection.

A newer raw chat signal can change CURRENT, but it cannot retroactively erase a prior provider-backed event. If the user intentionally requests destructive deletion of durable project data, treat that as a separate explicitly scoped mutation and verify it independently.

## Continuity example
`[X+13] → [X+14] → ...retrieved verified deltas... → [X+78] → [X+79] → [X+80]`.
The ellipsis is not permission to invent events; retrieve exact carriers when the middle lineage matters.

## Boundary
This gate provides project continuity/reconstruction. It cannot prevent the platform UI from opening a new chat or truncating visible context; instead it makes durable project state recoverable from provider-backed carriers on re-entry.
