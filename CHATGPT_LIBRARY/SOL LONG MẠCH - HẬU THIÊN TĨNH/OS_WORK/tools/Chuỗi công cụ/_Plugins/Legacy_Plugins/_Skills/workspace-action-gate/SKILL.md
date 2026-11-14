---
name: workspace-action-gate
description: Route authorized Google Workspace tasks through connected provider tools; validate live callability, maintain source receipts and readback. Use for Drive, Gmail, Calendar, Contacts, and multi-step workspace actions.
---
# WORKSPACE_ACTION_GATE — OS_WORK binding

Source of operational policy (installed plugin):
- `skills://plugins/workspace-action-gate/workspace-action-gate/skill.md`
- `skills://plugins/workspace-action-gate/google-ecosystem-whole-route/skill.md`

## Executable route
1. Detect provider and intent; use real callable connected tools (for Drive: `mcp__Google_Drive__search`, `get_file_metadata`, etc.) rather than made-up endpoints.
2. Check availability and permission state. Do not infer that a UI view or credential filename equals an authenticated session.
3. Use exact provider IDs, small read/write batches and receipts: `READ -> PLAN_DELTA -> BOUNDED_BATCH -> PROVIDER_RECEIPT -> READBACK -> CHECKPOINT`.
4. Credentials: `config.json` holds a *name-only* reference for the requested OAuth client. It contains NO secret; do not bind a different OAuth client as a fallback. Continue using the already connected provider when available.
5. If the exact requested OAuth client file has not been found, retain `AUTH_UNBOUND` for that optional binding. Never claim it is set up.

## Local healthcheck
`python3 scripts/healthcheck.py config.json` validates the config without opening the credential. This is a local file check, **not** a Google authentication test. Verify live provider with an authorized connector call.
