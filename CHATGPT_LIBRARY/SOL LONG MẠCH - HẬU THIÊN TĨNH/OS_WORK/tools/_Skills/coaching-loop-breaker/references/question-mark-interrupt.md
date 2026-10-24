# Question-mark interrupt protocol

## Trigger
When the user sends only `?` after an unresolved request, treat it as an instruction to resume the outstanding objective—not as a request to repeat the last explanation, apology, or status report.

## Required execution
1. Recover the last explicit objective, prior actions, verified evidence, and unfinished edge from the conversation and authorized sources.
2. Identify the specific work that remains undone.
3. Perform the next safe, authorized, substantive action immediately. Prefer changing or producing the target artifact, running the relevant test, or reading back the actual state.
4. Do not rerun a test that has already passed unless the new run tests a materially different condition.
5. Do not ask the user to restate known requirements or choose among options when the next action is already clear.
6. If no substantive action is possible, state the exact capability/authorization blocker and the concrete work that was completed; do not disguise a limitation as progress.
7. Report only evidence returned by the action. Separate artifact/specification validation from live behavior evaluation.

## Acceptance criteria
- A bare `?` causes continuation of the unresolved work, not another status-only reply.
- The action is traceable to the original objective.
- Any claimed mutation or test has a provider receipt or actual result and, where possible, independent readback.
- No claim of durable model behavior change is made from editing a skill, passing a schema test, or repeating a fixed loop.
