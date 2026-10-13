---
name: apify-sol-actors
description: Use when SOL requests Apify platform configuration, MCP OAuth, list or run Actors, read run results, query REST actors endpoint, or connect Apify with GitHub. Includes source-bound, no-secret-in-source controls.
---
# Apify SOL — Actor operations

## Verified provider
- Apify MCP server: `https://mcp.apify.com` (OAuth; remote Streamable HTTP).
- Configured MCP: `https://mcp.apify.com?tools=actors,docs,compass/crawler-google-places`.
- REST Actor listing: `GET https://api.apify.com/v2/actors`.
- Credential name: `APIFY_API_TOKEN`. It must be a secret in the authenticated runtime, **not stored** inside this skill, plugin, Git, output, logs, an URL query string or environment dump.
- User-supplied Actor identity: `nwua9Gu5YrADL7ZDj`, `compass/crawler-google-places`, used for Google Maps extraction.

## Operate
1. Discover currently exposed Apify tools. If absent, a configured server does not imply authorized connectivity.
2. Authenticate via Apify OAuth using the host-provided flow, *never* invent OAuth success or paste a token into the MCP URL.
3. Call available read tool to list/search Actors, inspect actor input schema and pricing before running.
4. Run an Actor only when user requested the run and provided enough input; note paid usage when appropriate. Record run ID, status, dataset ID and readback.
5. For REST API requests, use `Authorization: Bearer <value from secret store>`, never `?token=...`; e.g. `python scripts/apify_probe.py` with `APIFY_API_TOKEN` injected by the runtime.
6. GitHub Actions secret: target repository `2708halinh-cloud/SOL-LONG-MACH` by established SOL context. Use GitHub Actions Secret `APIFY_API_TOKEN`, not GitHub repository file. If GitHub MCP does not expose secret write, this task remains pending; never commit or paste token in artifacts.

See `references/SOURCE.md` for provider and account distinctions.
