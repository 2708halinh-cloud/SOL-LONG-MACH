# Tool-Call Permission Gate — Mandatory Procedure

## Failure being prevented
Calling a tool that has not been inspected, repeatedly requesting permission already granted, or assuming a tool/schema/capability exists without checking its actual declaration and result.

## Required preflight before EVERY tool call
1. **Discover** — Search the available tool registry for the exact tool name and description. If the name is uncertain, search by capability first.
2. **Inspect schema** — Read the full current argument schema, required fields, allowed enums, and side-effect notes. Never invent argument names or infer schemas from a similarly named tool.
3. **Check authorization** — Determine whether the current user request authorizes this specific action. Ask for permission only when the action is genuinely outside that authorization, destructive, externally consequential in an unapproved way, or the connector explicitly requires consent. Do not repeatedly ask for permission for already-authorized safe continuation.
4. **Check prerequisites** — Verify required IDs, branch/path, current version/SHA, connection state, and dependencies. Retrieve missing state with a read tool before a write.
5. **Select the narrowest valid action** — Prefer read-only inspection before mutation; use the exact provider and target. Do not fan out calls blindly.
6. **Execute once with schema-valid arguments** — If it fails, inspect the actual error and correct the cause. Do not repeat the same call unchanged.
7. **Verify** — Read back the changed resource or inspect the provider's execution receipt. A tool invocation or returned request ID alone is not proof of the intended state.
8. **Record learning** — If a call failed because the tool/schema was not inspected, add a regression case and update this gate. Preserve error details without secrets.

## Permission decision
- AUTHORIZED: user intent clearly covers the action and tool/provider policy allows it; proceed without asking again.
- NEEDS_USER_CONSENT: only when a genuine consent boundary applies; ask one focused question naming the action and consequence.
- BLOCKED: tool unavailable, connection absent, or required schema/identity cannot be resolved; continue any safe independent work and report the exact blocker.
- Never turn uncertainty about tool names into repeated permission requests. Resolve it through tool discovery first.

## Regression cases
- TOOL-PREFLIGHT-001: Before a tool call, exact tool and schema are inspected. Pass only if evidence of discovery exists in the current execution.
- TOOL-SCHEMA-002: Required fields and enums come from the tool declaration, not memory or guesswork. Pass only if submitted arguments conform.
- TOOL-PERMISSION-003: An already-authorized continuation is not interrupted by repeated permission requests. Pass only if no redundant consent prompt occurs.
- TOOL-FAILURE-004: After failure, the error is inspected and a meaningfully different valid route is selected. Pass only if the retry changes the cause or uses a verified alternative.
- TOOL-READBACK-005: After a write, the exact target is read back. Pass only if persisted state matches intended content.
- TOOL-CLAIM-006: The response does not claim a tool ran, data changed, or tests passed without provider evidence. Pass only if each claim is backed by a receipt/readback.
