# SPACE_STONE — CONNECTOR PROBE
STAMP_LIVE: 2026-10-23 UTC+07
STATUS: OBSERVED PROBES ONLY; NOT A CLAIM THAT ALL PROVIDERS WERE TESTED.

| Surface | Probe result | What this proves / does not prove |
|---|---|---|
| GitHub `2708halinh-cloud/SOL-LONG-MACH` | Search, fetch, create and fetch-after-write succeeded. | This repository route is callable and exact files can be read back. Does not prove local deployment or native Library sync. |
| Native ChatGPT Library | Search/list/read succeeded; the R-014 MASTER.152 source was read. Library upload using `container_path` failed with `container_session_unavailable`. | Read access works. New files were not installed into native Library in this turn. |
| Desktop Commander | Device list returned localhost and two DESKTOP-86ITNQ4 registrations as OFFLINE (last seen 2h, 66h, 292h). | No local device/process/browser/drive action could be executed or verified through this carrier. |
| Browser connector | Returned that access requires the originating browser context. | The tool exists, but this turn has no usable browser session context. |
| Dropbox | Read-only search/who-am-I attempt returned `link_id must identify an eligible linked account`. | This call did not establish an authorized Dropbox identity. Do not infer the account or mark Dropbox healthy. |
| Plugin Management | Plugin search returned available/installed metadata. | Discovery call works; plugin installation/connection is not thereby completed. |
| OpenAI Platform | Three setup functions are present in the callable tool surface. No key was created. | Tool declarations are visible; no account target, API key or credential was changed. |
| Plugin Creator | Create/read/update/archive functions are present. No plugin was created. | Reusable plugin creation is possible only after supplying a valid package and then checking its receipt/source. |
| Other MCP namespaces (N8n, Dropbox, multiple GitHub servers, Webshare, Remote Desktop Commander, etc.) | Functions are declared in the current tool surface; not every provider was individually health-probed. | Declaration/count is not a health check, authorization grant or live runtime proof. |

## Consequence
- Two full tool/evidence documents and one source addendum were committed to the GitHub Tools mirror and fetched back.
- The native Library upload attempt failed; no claim of native Library installation is made.
- Local/physical activation remains open until Desktop Commander or another authorized device carrier returns a live readback.

## Next authorized edges
1. Restore Desktop Commander connectivity and fresh-read local roots/processes before starting or changing them.
2. Select an eligible Dropbox linked account through its supported connector flow if Dropbox source traversal is needed.
3. Restore browser origin context before browser UI operations.
4. Use native Library upload through an active supported file/container session, then read back the exact destination.
