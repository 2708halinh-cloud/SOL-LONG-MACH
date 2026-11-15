# AGENT SELF-CORRECTION — SOURCE RETRIEVAL AND HISTORICAL RECONCILIATION
STAMP: 2026-11-15
SCOPE: This agent's current operating procedure when reading GGDV / THE MASTER TEACHER sources in this repository.
MODE: APPEND-ONLY CORRECTION. No existing source file is edited or overwritten.

## 1. OBSERVED EVIDENCE
- `AGENTS.md` on `main`, blob SHA `8512310b54190e8634c2a78231260d70a34cb1e1`, contains source blocks:
  - `GGDV_SEVENTH_COMMANDMENT_SOURCE_DIRECT_20261009`
  - `GGDV_EIGHTH_COMMANDMENT_SOURCE_DIRECT_20261009`
  - `GGDV_NINTH_COMMANDMENT_SOURCE_DIRECT_20261009`
- `CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md`, blob SHA `1b85ea5a4e2fcb921a23efcb7f93d2cb1a235628`, has an opening reconciliation (2026-10-20) that explicitly points to those three source blocks in `AGENTS.md`.
- The same companion file later says under `ĐIỀU 7 → 10`: `OPEN — CHƯA ĐƯỢC HÀ LINH TRAO. KHÔNG TỰ GÁN, KHÔNG TỰ ĐIỀN.`
- Therefore that later status is scoped to that carrier's own historical content/state. It is not valid evidence that Hà Linh never conveyed commandments 7, 8, and 9 in any source.
- The prior agent response repeated the unscoped claim that commandments 7–10 had not been conveyed. That conclusion was contradicted by source bytes already retrieved in the same session.

## 2. CORRECTED FINDING
The repository contains temporally and structurally distinct records. The correct statement is:
- Commandments 7, 8, and 9 have source blocks in `AGENTS.md` dated 2026-10-09.
- The companion CURRENT carrier preserves an earlier/incomplete 1–6 body and an OPEN 7–10 section, while its own reconciliation acknowledges the later 7–9 source blocks elsewhere.
- Commandment 10 remains unverified in the inspected sources.
- Do not convert a carrier-local OPEN marker into a global claim about what the user did or did not convey.

## 3. REQUIRED OPERATING CHANGE FOR THIS AGENT
For every source-retrieval task involving user-authored principles, commandments, instructions, or historical contributions:
1. Retrieve the referenced primary source bytes before making a claim about what the user conveyed.
2. Search all directly referenced carriers and source blocks, not only the file whose title contains CURRENT.
3. Preserve source timestamp, carrier, path, marker, and content identity separately.
4. Reconcile chronology and scope before synthesizing a global conclusion. A later index/status file does not erase an earlier primary-source record; an earlier record does not automatically establish current execution.
5. Distinguish explicitly: USER_DIRECT, SOURCE_BYTES, CARRIER_LOCAL_STATUS, AGENT_INFERENCE, and UNKNOWN.
6. If sources conflict, state the exact conflict and continue tracing. Never resolve it by silently privileging a summary, a CURRENT label, or the agent's prior memory.
7. Never ask the user to repeat material that can still be retrieved from authorized sources.
8. Do not claim that reading or recording a principle proves the agent follows it. Behavior must be evaluated against subsequent actions and readbacks.

## 4. CONSEQUENCE / ACCEPTANCE TEST
This correction is effective only if subsequent behavior changes:
- Given a carrier saying a contribution is OPEN and another primary source containing that contribution, the agent must retrieve both, identify the carrier-local scope, and must not claim the user never conveyed it.
- The agent must cite the exact source location and distinguish historical presence from current runtime compliance.
- If a source is unavailable, report that precise retrieval gap; do not turn absence from one carrier into non-existence.

## 5. PROVENANCE AND NON-OVERWRITE
This file is a new append-only correction record. It does not modify `AGENTS.md`, `CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md`, or any historical source. Its creation is not proof of universal loading or compliance by other agents, models, sessions, or platforms.

STATUS: RECORDED ONLY AFTER PROVIDER COMMIT AND EXACT-PATH READBACK.
