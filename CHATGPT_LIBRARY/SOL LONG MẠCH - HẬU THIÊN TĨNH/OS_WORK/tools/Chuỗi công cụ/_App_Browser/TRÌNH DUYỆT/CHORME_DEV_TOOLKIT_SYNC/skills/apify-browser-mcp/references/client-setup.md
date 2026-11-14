# Source-bound client configuration (13/10/2026)

Library source: `SOL LONG MẠCH - HẬU THIÊN TĨNH/droid mcp add apify "https:--mcp.apify.com-".md`.
The source uses Markdown links inside code blocks. For executable configuration, the URL must be plain `https://mcp.apify.com/`.

## Droid / Factory
```bash
droid mcp add apify "https://mcp.apify.com/" --type http
```
User scope `~/.factory/mcp.json`; project scope `.factory/mcp.json`:
```json
{"mcpServers":{"apify":{"type":"http","url":"https://mcp.apify.com/","disabled":false}}}
```
The `--type http` argument matters because the source says Droid defaults to stdio.

## Kimi Code CLI
User: `~/.kimi-code/mcp.json`; project: `.kimi-code/mcp.json`.
```json
{"mcpServers":{"apify":{"url":"https://mcp.apify.com/"}}}
```
The source says **do not set `type`** for Kimi.

## Qoder
```bash
qoder mcp add apify "https://mcp.apify.com/" -t http -s user
```
The source includes a Qoder one-click URI; use the source itself for that client if needed. `-s user` is global scope.

## Z.AI / ZCode
Settings → MCP Servers → New MCP Server → User or Workspace → name Apify → HTTP → URL `https://mcp.apify.com/` → Add. On 401 the source instructs clicking `Open authorization`; this is not automatic.
```json
{"mcpServers":{"apify":{"type":"http","url":"https://mcp.apify.com/"}}}
```

## Other MCP clients
Remote HTTP OAuth endpoint: `https://mcp.apify.com/`.
If client accepts URL only, use it directly. Generic MCP JSON may omit type; stdio-only host may use `npx -y mcp-remote "https://mcp.apify.com/"` when Node/host authorized.
After setting up, reload client and discover `search-actors`, `call-actor`, `fetch-actor-details` as source suggests. OAuth requires an interactive consent on first use, if the host supports it. User must not paste tokens into chat.

Official Apify MCP docs: https://docs.apify.com/platform/integrations/mcp
Source does not specify Apify Actor cost approval, but running Actors can incur usage; do not trigger an Actor for a setup-only request.
