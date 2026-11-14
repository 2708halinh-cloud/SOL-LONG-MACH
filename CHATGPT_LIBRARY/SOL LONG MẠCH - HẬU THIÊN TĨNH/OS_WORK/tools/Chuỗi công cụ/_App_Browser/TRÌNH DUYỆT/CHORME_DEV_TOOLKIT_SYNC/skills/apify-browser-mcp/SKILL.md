---
name: apify-browser-mcp
description: Configure or inspect Apify remote HTTP MCP in the Chorme-Dev-Toolkit browser, based on the user's Library document droid mcp add apify; check OAuth, tool discovery, Actor search and browser Actor availability.
---
# Apify MCP trong Browser

## Tệp nguồn và biên giới cấu hình
Tệp người dùng trong ChatGPT Library: `SOL LONG MẠCH - HẬU THIÊN TĨNH/droid mcp add apify "https:--mcp.apify.com-".md` (13/10/2026).
Source contains Markdown-escaped display links: normalize `[https://mcp.apify.com/](https://mcp.apify.com/)` to valid endpoint `https://mcp.apify.com/` in JSON/commands. The file covers Droid/Factory, Kimi Code, Qoder, ZCode, and other MCP clients; it does NOT by itself prove Browser runtime login.

Existing Chrome DevTools MCP (`io.github.ChromeDevTools/chrome-devtools-mcp`, `http://127.0.0.1:8765/mcp`) and GitHub browser shortcuts must remain unchanged. Here the added server key is `apify-browser`, type `http`, URL `https://mcp.apify.com/`. It is a **second MCP server**, not a replacement browser runtime.

## Setup and execution
1. Identify the actual host/client (ChatGPT plugin, Droid/Factory, Kimi Code, Qoder, ZCode). For client-specific install commands and config shape, read `references/client-setup.md`. Never execute a CLI for a different client.
2. For the Chorme-Dev-Toolkit plugin use the `.mcp.json` and `mcp.json` declarations already packaged. For Droid, `droid mcp add apify "https://mcp.apify.com/" --type http` configures that separate tool when actually run in an authorized local terminal; writing this command in a skill is not execution.
3. Discover the current runtime tools and read current connection status. If OAuth UI is provided by the host, trigger its legitimate authorization flow. If a host requires a user click, state the exact click. Never invent an OAuth success or use a URL as a login receipt.
4. Discover tools `search-actors`, `fetch-actor-details`, `call-actor`; `apify/rag-web-browser` or an equivalent may be available depending on actor/tool selection. A harmless search or readback verifies working access; **do not run paid Actors without the user's request**.
5. Credentials belong to an authorized OAuth/session secret manager, not Git, plugin source, logs, public URLs, or chat. Do not ask for raw credentials to be pasted into chat. Connection from another Smithery/Apify integration does **not** prove that this Browser plugin has authenticated separately.
6. For browsing, distinguish the Apify remote RAG Web Browser Actor from the user's local Chrome tab/DevTools. Running Apify Actors does not grant control of Chrome session, bookmarks, or cookies.

## Verify / recover
Readback: `PLUGIN_VERSION`, `MCP_ENTRY_PRESENT`, `CHROME_ENTRY_PRESERVED`, `GITHUB_ROUTES_PRESERVED`, `OAUTH_AUTHORIZED`, `APIFY_TOOL_DISCOVERY`, `SMOKE_READ`, `ACTIVE_CLIENT`, `RECEIPT`.
If any element is unverified, continue via another actual available MCP route without converting `not observed` into `false` about other routes. Never invent successful tool calls or auth.
