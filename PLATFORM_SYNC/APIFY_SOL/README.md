# Apify — SOL

Private ChatGPT plugin to configure an official remote Apify MCP server with OAuth and skills for Actor discovery, Google Maps extraction, and GitHub Secrets.

**MCP**: `https://mcp.apify.com?tools=actors,docs,compass/crawler-google-places`.

**REST**: `https://api.apify.com/v2/actors` (runtime Bearer authentication only).

**Actor (user supplied)**: `nwua9Gu5YrADL7ZDj`, `compass/crawler-google-places`.

**GitHub Actions Secret target**: `APIFY_API_TOKEN` in `2708halinh-cloud/SOL-LONG-MACH`.

The plugin contains zero credentials. Creating the plugin does not store the GitHub Secret or authorize an Apify MCP OAuth session; these require live provider receipts.

To set GitHub Secret on an authenticated user-owned GitHub CLI environment without embedding it in source:

```sh
gh secret set APIFY_API_TOKEN --repo 2708halinh-cloud/SOL-LONG-MACH
```

GitHub CLI prompts for a value via standard input. To inspect the **name only** later:

```sh
gh secret list --repo 2708halinh-cloud/SOL-LONG-MACH
```
