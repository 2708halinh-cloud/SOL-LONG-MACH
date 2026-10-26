---
name: chrome-devtools
description: Uses Chrome DevTools via MCP for efficient debugging, troubleshooting, and browser automation. Use when debugging web pages, automating browser interactions, analyzing performance, or inspecting network requests. This skill does not apply to --slim mode (MCP configuration).
---

# Chrome DevTools via MCP

## Core concepts

**Browser lifecycle:** The browser starts automatically on the first tool call using a persistent Chrome profile. Configure CLI arguments in the MCP server configuration with `npx chrome-devtools-mcp@latest --help`.

Additional tooling can be enabled with:
- `--categoryExtensions` for extension tooling.
- `--memoryDebugging` for memory tooling.

**Page targeting:** Page-scoped tools require `pageId`. Use `list_pages` to find page IDs (for example, `pageId: 1`), or use the ID returned by `new_page`. For `evaluate_script`, provide `pageId` when targeting a page. When `--categoryExtensions` is enabled, `pageId` may be omitted in favor of `serviceWorkerId` to evaluate inside an extension background service worker.

**Element interaction:** Use `take_snapshot` to inspect page structure and obtain element `uid` values. Use those UIDs for interaction. If an element is missing, take a fresh snapshot because the page may have changed.

## Workflow before interacting with a page

1. Navigate with `navigate_page` or `new_page`.
2. Wait with `wait_for` when there is a known load condition.
3. Take a snapshot with `take_snapshot`, specifying `pageId`.
4. Interact using the UIDs from that snapshot and the same `pageId`.

## Efficient data retrieval

- Use `filePath` for large outputs such as screenshots, snapshots, or traces.
- Use pagination (`pageIdx`, `pageSize`) and filtering (`types`) to reduce output.
- Set `includeSnapshot: false` on input actions unless the updated page state is needed.

## Tool selection

- **Automation and interaction:** `take_snapshot` is text-based and generally faster for automation.
- **Visual inspection:** use `take_screenshot` when visual evidence is needed.
- **CSS and styling:** use `get_css_styles` to inspect matched rules, cascade, and CSS variables; treat the returned output as authoritative for that query.
- **Runtime DOM/JavaScript details:** use `evaluate_script` when snapshots and CSS inspection do not provide the needed data.

## Parallel execution

Independent tool calls may run in parallel, but preserve the sequence for page operations: navigate → wait → snapshot → interact.

## Testing a browser extension

Extension tools such as `install_extension` and `list_extensions` are available only if the MCP server starts with `--categoryExtensions`. If those tools are absent, do not pretend they are available. Update the server configuration and restart the MCP server or AI client before retrying:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest", "--categoryExtensions"]
    }
  }
}
```

Then:

1. **Install:** call `install_extension` with the path to the unpacked extension.
2. **Identify:** obtain the extension ID from the result or `list_extensions`.
3. **Trigger:** use `trigger_extension_action` to open the popup or side panel when applicable.
4. **Verify the service worker:** use `evaluate_script` with `serviceWorkerId`, omitting `pageId` and `args`. For page evaluation, use `pageId` and omit `serviceWorkerId`.
5. **Verify page behavior:** navigate to a relevant page and use `take_snapshot` to check whether content scripts injected elements or changed the page.

## Troubleshooting

If Chrome DevTools MCP is insufficient, consult:
- Chrome DevTools documentation: https://developer.chrome.com/docs/devtools
- DevTools AI assistance: https://developer.chrome.com/docs/devtools/ai-assistance
- Chrome DevTools MCP troubleshooting: https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/troubleshooting.md

## Limits and verification

- Do not claim that the MCP server is configured, connected, or working unless its configuration and live tools have been checked.
- Do not claim an extension is installed or functioning based only on a successful installation response; verify its ID, service worker state, and page behavior where applicable.
- This skill does not apply to `--slim` mode (MCP configuration).
