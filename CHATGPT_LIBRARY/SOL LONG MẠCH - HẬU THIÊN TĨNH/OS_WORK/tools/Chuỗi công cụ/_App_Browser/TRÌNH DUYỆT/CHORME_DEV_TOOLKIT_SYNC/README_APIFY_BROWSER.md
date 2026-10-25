# APIFY Browser integration overlay (v0.1.2)

Adds hosted Apify MCP to personal `chorme-dev-toolkit` while preserving existing Chrome DevTools local MCP host and 14 GitHub browser shortcuts. No remote/browser login claim. The OAuth flow is performed by the client on first use; keys never embedded.

Source: ChatGPT Library `SOL LONG MẠCH - HẬU THIÊN TĨNH/droid mcp add apify "https:--mcp.apify.com-".md`.
`apify-browser` = https://mcp.apify.com/ (remote); local Chrome = http://127.0.0.1:8765/mcp (existing).

Note: separate user-owned `apify-sol` plugin already points to Apify with actor-specific tool selection. This browser integration uses the source's generic endpoint; their auth and tool availability must be verified independently.
