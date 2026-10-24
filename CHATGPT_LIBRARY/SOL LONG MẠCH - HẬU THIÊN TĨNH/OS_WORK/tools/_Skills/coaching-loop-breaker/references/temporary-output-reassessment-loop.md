# Temporary Output and Reassessment Loop

Status: operational protocol defined; runtime behavior must be evaluated separately.

## Purpose
Keep the user informed with concise, useful intermediate outputs while work continues. An intermediate output must report evidence or a concrete decision, not merely announce that work is in progress.

## Loop
1. IDENTIFY — State the observed failure or uncertainty and its concrete impact.
2. EVIDENCE — Inspect the exact source, tool declaration/schema, authorization boundary, and available readback.
3. REASSESS — Classify the failure: wrong tool/route, schema mismatch, genuine consent gate, missing prerequisite, failed verification, or unsupported claim.
4. ADJUST — Choose a materially different, authorized next action. Do not repeat a rejected path unchanged.
5. VERIFY — Read back the result or run an available test. Record PASS, FAIL, or BLOCKED with evidence.
6. REPEAT — On FAIL/BLOCKED, preserve completed work and reassess alternatives. Stop only when the goal is achieved or all safe available routes are exhausted.

## Temporary output format
Emit an update when a meaningful state transition occurs:
- IDENTIFY: failure + impact.
- EVIDENCE: what was inspected and what it proves.
- REASSESS: revised diagnosis and why the prior approach was insufficient.
- ADJUST: exact action now being taken.
- VERIFY: observed result, evidence link/reference, and remaining gap.
- NEXT: next concrete step if still incomplete.

Avoid empty heartbeat messages, repetitive apologies, inflated progress claims, and output that merely restates the plan. Keep updates short and continue working after each update whenever tools and time permit.

## Evidence and truthfulness
- A commit existing is not proof that its tests pass.
- A workflow file existing is not proof that the workflow ran.
- A regression case existing is not proof that live agent behavior improved.
- Mark tests as PASS only after observing successful execution; otherwise mark NOT RUN, FAIL, or BLOCKED.
- If a provider blocks a specific route, do not retry the same route unchanged. Inspect available alternatives and preserve the distinction between provider consent requirements and tool uncertainty.
- Never claim autonomous background or cross-session execution unless an actual mechanism and its execution are verified.

## Acceptance criteria
A work cycle is complete only when the intended change is read back or independently verified, available tests are run where possible, and residual gaps are explicit. If incomplete, the next update must identify a different concrete action rather than repeat a generic status.
