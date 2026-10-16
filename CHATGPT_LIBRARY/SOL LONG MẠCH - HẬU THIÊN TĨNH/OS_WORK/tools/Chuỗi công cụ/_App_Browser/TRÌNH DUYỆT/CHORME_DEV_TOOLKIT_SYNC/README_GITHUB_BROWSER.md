# GitHub navigation in Chorme-Dev-Toolkit

14 user-provided GitHub browser shortcuts are added as a non-destructive skill in `skills/github-browser-routes/`.

The original Chrome DevTools MCP server configuration (`mcp.json`, `.mcp.json`), existing tools, skills, bridge and scripts are preserved by the overlay update.

Run browser navigation using the current authenticated GitHub session, if present. These routes are regular web pages, not MCP servers or OAuth endpoints. `ADMIN_ACCESS_URL` is a search filter, not a request to grant administrative rights.

Source flags preserved verbatim: `ACCESS_GITHUB=TRUE`; `ACCESS_CHATGPT=FLASE`. Actual permissions / login require runtime readback, and no ChatGPT access settings are modified.

Secrets are deliberately absent; secrets from adjacent ToolBox or AI Studio tasks are neither consumed nor embedded.
