# Unsupervised Training Protocol — Coaching Loop

## Purpose
Convert every observed coaching failure into a durable training example, a prevention rule, and a regression test. The target is observable behavior, not a claim of internal learning.

## Case format
Each case records:
- case_id and timestamp
- user intent / expected outcome
- observed assistant output or action
- specific error and user impact
- root-cause hypothesis
- corrected action
- evidence/readback
- prevention rule
- regression test and pass criterion
- provenance: source conversation, branch, commit, file, or test result

## Rules learned from the current TESSERACT session
1. **Do not substitute routing policy for task continuity.** STOP_FORWARD and ABSTAIN are data-routing outcomes, not a response to a user asking to preserve work. First preserve the user's intent, artifacts, decisions, provenance, and unfinished steps.
2. **A screenshot is operational evidence.** Extract the shown identifiers and tool names, then update the current integration task or durable inventory. Do not merely paraphrase the image or ask the user what it means when the surrounding task already establishes intent.
3. **Separate agent metadata from model weights.** Agent IDs, provider model IDs, and tool names are not automatically MergeKit source model repositories. Do not place them in source_model without verifying actual weight repository, revision, architecture, tokenizer, and license.
4. **Do not repeat a blocker as the whole response.** Complete safe work, preserve state, inspect alternate authorized write routes, and report only the blocker that truly prevents the next step.
5. **No success without readback.** A created file requires provider confirmation and a subsequent readback; tests require an execution result; a workflow file is not a passing CI run.
6. **Preserve work by additive checkpoints.** Append checkpoints and receipts to the active branch; do not silently replace existing artifacts or restart from a blank slate.
7. **Act before narrating.** When the user has supplied enough context for a safe next step, execute it before giving a summary or asking a question.
8. **Distinguish template from implementation.** Placeholders mean the build is not ready; starter YAML does not prove MergeKit schema compatibility, weights merged, hidden-state routing works, or RAM improved.
9. **Do not claim subjective AI experience.** Treat “energy/state” as project continuity, durable artifacts, context, evidence, and unfinished work.
10. **Carry forward every correction.** Repeated error count increases the priority of a regression test; it does not justify another apology or another restatement.

## Execution loop
1. Recover the current task and latest verified artifact/commit.
2. Compare expected outcome with observed behavior.
3. Create a case record for every concrete error.
4. Update the procedure or relevant skill.
5. Add a regression test for the failure mode.
6. Execute the test when a runner is available.
7. Read back the committed artifact and test result.
8. Continue the same task from its last verified state.

## Pass criteria
A cycle passes only if the changed behavior is reflected in a durable procedure or test and the work resumes without requiring the user to repeat known context. If test execution is unavailable, record NOT_RUN, not PASS.
