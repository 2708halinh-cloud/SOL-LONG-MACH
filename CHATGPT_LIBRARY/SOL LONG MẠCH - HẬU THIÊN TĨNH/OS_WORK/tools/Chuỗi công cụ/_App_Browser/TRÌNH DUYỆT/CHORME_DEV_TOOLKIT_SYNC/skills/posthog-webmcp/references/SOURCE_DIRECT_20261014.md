# SOL X-Time PostHog — source ledger

- `SOURCE_DIRECT`: user-supplied PostHog US URLs for project `662649`, organization details, email identifier and redirect callback URL.
- `OBSERVED_EXTERNAL_DOCUMENTATION`: PostHog's documented MCP server is `https://mcp.posthog.com/mcp`; the OAuth flow takes place in the MCP client. Sources: https://posthog.com/docs/model-context-protocol/codex , https://posthog.com/docs/model-context-protocol/cursor.
- `OBSERVED_LIBRARY_STATE_BEFORE`: both original JSON configs contained Chrome DevTools and Apify only. Chrome bridge `127.0.0.1:8765/mcp` has a potential port conflict with declared MINH; it is preserved, not enabled/verified.
- `ACTION`: add PostHog HTTP MCP entry without removing Chrome or Apify; add the PostHog skill and an opt-in local sync/verification helper.
- `AUTH_PROVENANCE`: project `phc_` token is write-only ingestion scope, not access control. Prior `127.0.0.1:22635/oauth/callback` had a code/state in the user conversation but must never be replayed, stored or copied.
- `UNRESOLVED`: whether the authenticated local Chrome client is accessible; whether OAuth is current; whether `tools/list` succeeds; whether project `662649` is active. User's remote Desktop Commander tools have previously returned a monthly usage limitation; do not claim live host changes without new verified access.

## 2026-10-14 follow-up — OAuth callback

- `SOURCE_DIRECT`: user supplied browser callback `localhost:8239` with a *PostHog login complete* message instructing them to return to the terminal wizard.
- `OBSERVED_FROM_USER`: local OAuth callback UI reports success. The one-time `code` value is deliberately neither retained nor replayed.
- `TOOL_READBACK`: latest Plugin Management catalog reported PostHog `installed=false`; Smithery toolbox returned no PostHog tools.
- `DISTINCTION`: local wizard login is **not** the same as ChatGPT's PostHog plugin authorization, and a callback is not an MCP endpoint.
- `UNRESOLVED`: local wizard process completion, MCP `tools/list`, X-Time project 662649 readback.

## PostHog login continuity contract (2026-10-14)

- `USER_BROWSER_CALLBACK_LOGIN_COMPLETE`: evidence is the user-shared success screen from PostHog Wizard on localhost:8239; *not* a credential or client `tools/list` proof.
- `ONE_TIME_OAUTH_CODE`: intentionally NOT persisted/replayed; not needed for future MCP calls if the native client has its OAuth session.
- `NO_REPEAT_USER_INPUT`: reuse the same local authenticated client first; do not request password, token, cookie, callback code or OAuth URL again as a generic prerequisite.
- `NEXT_RUNTIME_CHECK`: inspect PostHog Wizard terminal's final result and client-owned secure credential store on the actual host without exporting secret bytes; then verify MCP tools and project 662649.
- `CHATGPT_CONNECTOR`: independent client; its installation state does not establish the state of the user's local PostHog Wizard session.
