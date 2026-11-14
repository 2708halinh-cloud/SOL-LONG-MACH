# SPACE_STONE / @Workspace: Xiaomi Notes + Google Keep + Google Tasks

This is a runnable, standard-library-only **local staging and Google Tasks connector**. It does not claim the Xiaomi Notes, Google Keep or Google Cloud service is connected. It reads JSON exports without changing them, retains the source item literally, makes a separate observation/proposal projection, and only converts unchecked checklist items to Tasks when explicitly requested.

No action deletes anything. There is no automatic monitoring, two-way synchronization, Xiaomi Cloud access or Keep REST connector. No raw notes, access token, or private data is committed to GitHub.

## Run read-only (default)

```bash
python workspace_bridge.py --xiaomi-json /path/notes.json --keep-json /path/keep.json --output local-snapshot.json
```

Accepted inputs: JSON array of notes or `{"notes":[...]}`, `{"items":[...]}`, `{"data":[...]}`. Each note can use a `checklist` or `checkItems` array containing strings or `{ "text": "...", "checked": false }`. Exports may require schema conversion by their native export tools. Omitting a provider is allowed. Output must differ from input paths.

## Show an explicit checklist → Google Tasks proposal, without sending data

```bash
python workspace_bridge.py --xiaomi-json /path/notes.json --output local-snapshot.json --map-checklists
```

## Send explicitly to an existing Google Tasks list

The operator must have an authenticated, short-lived Google OAuth bearer token with Google Tasks scope (`https://www.googleapis.com/auth/tasks`) and supply a real task-list ID. This script does not generate tokens and never saves them.

```bash
# Set SOL_GOOGLE_TASKS_ACCESS_TOKEN in the local environment using an authorized secret store.
python workspace_bridge.py --xiaomi-json /path/notes.json --output local-snapshot.json \
  --map-checklists --execute --allow-send --tasklist-id ACTUAL_TASKLIST_ID --ledger private-local-ledger.json
```

The script writes one in-flight marker **before** remote `POST`, performs a `GET` on that exact provider task ID, then records `readback_verified` in the separate local ledger. Unknown results are quarantined as `NEEDS_PROVIDER_RECONCILIATION` and deliberately not retried automatically, preventing duplicate remote tasks. Do not publish or Git-commit local snapshots/ledgers.

## Verification

```bash
python -m unittest -q test_workspace_bridge.py
```

Provider status for 2026-10-17: connected ChatGPT Google Drive/Calendar do not grant Google Keep/Tasks API scopes; Windows Desktop Commander is offline; the script was unit-tested offline, not proven against a live Google Tasks OAuth account. A Google Cloud integration is not claimed from these local tests.