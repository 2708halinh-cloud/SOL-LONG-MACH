---
name: github-browser-routes
description: Use for opening GitHub dashboard, feed, assigned issues, pull requests, repositories, admin-access repository filter, projects, discussions, codespaces, Copilot, Explore, Marketplace, MCP registry, and profile settings in an authenticated browser. This is browser navigation, not a GitHub API/MCP credential grant.
---
# GitHub Browser — nguồn điều hướng của người dùng

## Bản đồ
Read `references/github-navigation.json` and choose the matching named key. Keep all original URL values, including query encoding and `SETTING_GUTHUB_URL` spelling. The declared values `ACCESS_GITHUB=TRUE` and `ACCESS_CHATGPT=FLASE` are the user's routing preference, **not** observed runtime permissions. In this browser route do not replace with ChatGPT's default GitHub connector.

## Thực thi
1. Verify an authorized browser target/session is actually available before claiming any page opened. Use only the attached Chorme-Dev-Toolkit browser host or a browser tool explicitly available and authenticated in the current runtime.
2. Read route from the JSON map; allow navigation only to `https://github.com/` or `https://github.com` unless the user explicitly authorizes a different host.
3. Open the route in the already authenticated GitHub browser session. Inspect current URL/page and avoid claiming signed-in state from a URL alone.
4. `ADMIN_ACCESS_URL` is **a repository dashboard filter** (`admin:@me`); it does not confer administrator permissions. Actual access is what the currently logged-in GitHub user has.
5. For changes, honor the exact user request and require actual browser action + readback; don't turn navigation links into implicit authorization to modify settings, repos, permissions, or tokens.
6. If Chrome MCP host is unavailable, try another actually available authorized browser route, but preserve the distinction between "configured" and "connected". Keep a short factual receipt; never call missing tools or invent screenshots.
7. Never store GitHub cookies, passwords, PATs, OAuth bearer/refresh tokens or HTTP authorization headers in plugin files or logs.

## Readback
`CONFIG_PRESENT`, `ACTIVE_BROWSER`, `GITHUB_SESSION_VERIFIED`, `OPENED_URL`, `PAGE_TITLE_OR_IDENTIFIER`, `RESULT`, `TIME`. An unverified runtime remains unverified. No separate `ACCESS_CHATGPT` setting is modified by this plugin.
