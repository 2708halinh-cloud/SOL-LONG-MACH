# Source-bound configuration

Provider: Apify (https://docs.apify.com/mcp; https://docs.apify.com/api/v2).

Actor reference supplied by user: `nwua9Gu5YrADL7ZDj`, account/username `compass`, actor name `crawler-google-places`, title `Google Maps Scraper`.

REST actors listing is a read-only check; do not conflate one actor listed with permissions to start an actor. User supplied a snapshot (total 1). Validate actor identity via an authenticated provider call before stating current state.

Important: the provided `https://api.apify.com/v2/actors?token=...` is a secret-bearing REST URL, not a ChatGPT MCP URL and must not be saved verbatim. Prefer HTTP Bearer header with runtime-provided `APIFY_API_TOKEN`. MCP endpoint uses OAuth and is separate from REST API.

The GitHub Actions repository secret value is never readable after saving, so verification should check metadata/name (without revealing value) or perform a non-logging authenticated API probe through a workflow. Do not expose masked-token traces.
