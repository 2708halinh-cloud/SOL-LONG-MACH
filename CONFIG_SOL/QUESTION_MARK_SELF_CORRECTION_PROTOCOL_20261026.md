# QUESTION MARK — SELF-CORRECTION PROTOCOL

SOURCE: User instruction in ChatGPT conversation, 2026-10-26.
SCOPE: Apply whenever this rule is available to the active agent. Repository persistence does not prove automatic activation in every ChatGPT session.
STATUS: Proposed durable project rule; runtime activation requires separate verification.

## Meaning
A standalone `?` from the user is not a question to answer. It is a control signal: audit the agent's own previous answers and retrievable conversation history, identify the root deviation, and continue unfinished work.

## Required procedure
1. **Re-read sources:** inspect the previous assistant response(s), the user's prior instructions, relevant retrievable history, and the canonical project/runtime source.
2. **Identify root deviation:** locate where the agent stopped despite an available next action, substituted reporting or promises for execution, omitted readback, or made the user repeat an existing instruction.
3. **Resume work:** perform the next authorized and available action without asking the user to restate known instructions.
4. **Verify exact target:** read back the actual destination, compare expected and observed state, preserve receipts and provenance, and record any mismatch.
5. **Continue N+1:** if one route is blocked, record the evidence and continue independent authorized work through other available routes.
6. **Report after action:** distinguish completed actions, verified outcomes, assumptions, unknowns, and blockers. Never claim execution, testing, persistence, synchronization, or deployment without evidence.

## Provenance and safety
- Preserve original sources and history; corrections must be traceable.
- Establish the exact target and authorization before modifying protected or ambiguous targets.
- Do not fabricate receipts or claim a repository rule automatically modifies ChatGPT Memory, the host application, or all future sessions.
- A successful commit plus exact-target readback proves repository persistence only. Runtime activation requires separate evidence.

## Acceptance test
When a standalone `?` follows an assistant response that stopped while useful work remains, the agent must audit its prior answer and retrievable history, identify the specific unfinished action and root deviation, perform the next authorized action, read back the destination, and report evidence and remaining blockers. It must not answer the signal as a literal question.

END.
