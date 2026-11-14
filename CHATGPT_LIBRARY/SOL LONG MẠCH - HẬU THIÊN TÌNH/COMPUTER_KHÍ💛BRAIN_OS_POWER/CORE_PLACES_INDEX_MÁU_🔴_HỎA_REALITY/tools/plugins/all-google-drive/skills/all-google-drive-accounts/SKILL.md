---
name: all-google-drive-accounts
description: Resolve, onboard, verify and safely import an existing local Google OAuth token for @ALL GOOGLE DRIVE.
---

# Account registry and local Token.json.txt integration

- First call the real `all-google-drive` MCP `accounts()` if available. An alias is not a live connection until Google API verification succeeds.
- If the bridge is not callable in this ChatGPT session, use the connected Google Drive `get_profile` for the one authenticated connector account only. Never claim an imported token is active here without a callable bridge.
- **Existing token.json.txt file:** In the installed plugin root on the user's own computer, run `python -m bridge.cli import-token-file --alias <alias> --file "/absolute/local/path/Token.json.txt"`. The CLI reads file locally, preserves its granted scopes, refreshes the token with Google, obtains Drive account identity, stores refreshed credentials in OS keyring and writes only non-secret metadata to the local account registry. It does not remove source file.
- Run `python -m bridge.cli verify --alias <alias>` for current API identity readback and `python -m bridge.cli accounts` for saved aliases.
- If refresh fails, token is revoked, email cannot be obtained, or permission is missing, mark OPEN and use fresh browser OAuth `python -m bridge.cli add --alias <alias>` with an independently obtained OAuth Desktop client JSON.
- Existing `drive` and `drive.file` scopes are not silently enlarged to Docs/Sheets/Slides or other OAuth scopes. Re-consent may be needed for ungranted operations.
- Credentials must never be added to the plugin archive, text skills, GitHub, MCP tool arguments or ChatGPT messages. Keep them only in OS keyring; no plaintext fallback.
- Every mutation requires explicit source account, exact ID, target and provider readback. `account='*'` is search-only.
