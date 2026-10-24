---
name: all-google-drive
description: Single entrypoint for @ALL GOOGLE DRIVE; route all file, Docs, Sheets, Slides, accounts and cross-account requests into actual Google provider tools or the independently authorized local multi-account MCP bridge.
---

# @ALL GOOGLE DRIVE — unified router

## Core

Use `@ALL GOOGLE DRIVE` for Drive, Docs, Sheets, Slides and cross-account Google Workspace files. This plugin is a replacement **for workflow routing**, and a separate, user-owned local MCP bridge provides the **multi-account provider interface** when that bridge is actually connected.

Do not pretend an installed Skill changes Google account identity, OAuth scopes, Google ACLs, or injects tools into the current session. The platform's `full_access` permission setting applies to prompts/approvals for this plugin, not Google's authorization.

## Resolve the real provider

1. If an `all-google-drive` MCP server is callable, call `accounts()`; distinguish aliases, emails and provider freshness. Select explicit account for every write; `*` is for search only.
2. Otherwise, use the existing `Google_Drive` connector **only** for the actually authenticated account, not for every account the user mentioned. `get_profile({})` may establish the currently signed-in email.
3. If an account is missing, state `OPEN: ACCOUNT_NOT_CONNECTED` and give the local OAuth onboarding instruction; never ask for user passwords, bearer tokens or client secrets inside chat.
4. For any URL, preserve literal file ID, MIME type, account alias, parent IDs, revision and source URL. Do not silently switch accounts or documents on matching names alone.

## Routes

- Accounts: `../all-google-drive-accounts/SKILL.md`.
- File browsing, moving, renaming, copying, deletion, sharing: `../all-google-drive-files/SKILL.md`.
- Google Docs content: `../all-google-drive-docs/SKILL.md`.
- Google Sheets ranges/formulas: `../all-google-drive-sheets/SKILL.md`.
- Google Slides pages/objects: `../all-google-drive-slides/SKILL.md`.
- Cross-account copy, inventory, reconciliation: `../all-google-drive-sync/SKILL.md`.

## Access stance

No artificial hardcoded read-only mode: use the complete operations allowed by the user's **authenticated Google OAuth scopes + file ACLs**, with the user's chosen full ChatGPT app permissions when available. Do not assume unrestricted access to other people's accounts; no feature can override Google policy or a disconnected account.

Before writes, identify source account, ID, target account if different, and exact requested delta. Use revision guards when available. After writes, retrieve state again from the actual target (T007 readback); if readback fails, do not mark completed. Delete by trash unless permanent deletion was specifically requested.

Every cross-account transferred file receives a **new** Google file ID and may lose native revision history, comments and original permissions. Keep source untouched unless separately instructed, and verify copy independently before cleanup.

Avoid external network copy of private content outside user's selected account/carrier. Do not include OAuth tokens, client secrets or file bytes in audit logs or command text.
