# ALL GOOGLE DRIVE v0.1.1 — existing Token.json.txt import

This private plugin includes Python MCP bridge code. The plugin package never includes OAuth secrets.

## Securely import your existing token.json.txt

In the unpacked plugin root on **your own computer** (not the ChatGPT sandbox):

```bash
python -m pip install -r bridge/requirements.txt
python -m bridge.cli import-token-file --alias existing --file "/absolute/path/to/Token.json.txt"
python -m bridge.cli verify --alias existing
python -m bridge.cli accounts
```

The CLI checks JSON and Drive scopes, refreshes with Google's OAuth endpoint, reads the actual email via Google Drive `about`, then stores the credentials in OS keyring and only non-secret metadata in `accounts.json`. The original file remains untouched. Google must accept the refresh token. If expired/revoked, use `python -m bridge.cli add --alias existing` with a Google Desktop OAuth client secret file instead.

**Scope note:** The supplied source file grants `drive` and `drive.file`; import preserves only these scopes. Other API permissions must be granted through Google OAuth before use.

**Important:** The installed ChatGPT plugin is a skills/router package. The local Python MCP service must still be configured and connected to a compatible MCP host or HTTPS bridge before ChatGPT can call imported aliases. The currently connected ChatGPT Google Drive connector is separate.

For the complete initial plugin description, refer to the original v0.1.0 release.
