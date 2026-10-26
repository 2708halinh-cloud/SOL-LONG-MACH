---
name: memory-leak-debugging
description: Diagnoses and resolves memory leaks in JavaScript/Node.js applications. Use when a user reports high memory usage, OOM errors, or wants to capture, compare, or inspect heap snapshots with Chrome DevTools MCP memory tools.
---

# Memory Leak Debugging

Use Chrome DevTools MCP memory tools to investigate JavaScript and Node.js memory growth. Treat memory growth as a hypothesis to test, not proof of a leak. Preserve evidence and verify whether memory remains retained after the workload is reverted.

## Prerequisites

Advanced tools such as `compare_heapsnapshots` and `get_heapsnapshot_details` may require the MCP server to start with `--memoryDebugging`.

1. Check whether the required memory tools are present in the active tool registry.
2. If absent, inspect the actual MCP server configuration if accessible and check for `--memoryDebugging`.
3. If the flag is absent, add it to the `chrome-devtools` server arguments and restart the MCP server or AI client before retrying.
4. Never claim the flag is enabled or tools are available without checking.

Example configuration:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest", "--memoryDebugging"]
    }
  }
}
```

Merge this flag with existing arguments; do not overwrite other required flags such as `--categoryExtensions`.

## Core principles

- **Prefer MCP memory tools:** Do not read raw `.heapsnapshot` files directly when MCP summary, comparison, and inspection tools can answer the question. Heap snapshots can be very large.
- **Isolate the runtime:** Determine whether growth occurs in a browser page, a browser extension/service worker, or a Node.js server process. Browser page tools do not automatically inspect a separate Node.js process.
- **Compare equivalent states:** Keep the workload, route, data, and timing as consistent as possible between snapshots.
- **Inspect retention before editing:** Look for detached DOM nodes, closures, global references, listeners, subscriptions, timers, observers, and unbounded caches.
- **Treat detached nodes carefully:** Detached DOM nodes may be intentional caches. Do not null or remove them without understanding ownership and obtaining user approval when the change is destructive.
- **Release investigation resources:** Close each loaded snapshot with `close_heapsnapshot` when finished, using the IDs expected by the active tool schema.

## Workflow 1 — Capture snapshots

For a frontend page:

1. Identify the target page with `list_pages` and use its actual `pageId`.
2. Record baseline state and reproduce the suspected memory-heavy workflow.
3. Use page-scoped tools such as `click`, `navigate_page`, or `fill` as appropriate.
4. Capture a baseline with `take_heapsnapshot`.
5. Repeat the same interaction sequence around 10 times, if safe and representative, and capture a target snapshot.
6. Revert the page to the original state and allow cleanup/garbage collection opportunities where the tools support it. Capture a final snapshot.
7. Record snapshot identifiers and workload details. Do not interact with production data or trigger irreversible actions without authorization.

For Node.js, use tooling attached to the actual Node process (for example, an authorized inspector or runtime-specific profiler). Do not assume browser page snapshots represent server memory.

## Workflow 2 — Compare snapshots

1. Use `get_heapsnapshot_summary` on each snapshot and confirm the snapshots loaded successfully.
2. Use `compare_heapsnapshots` on baseline and target without `classIndex` first to obtain the overall diff.
3. Identify suspicious classes or retained-size growth, then request detailed class diffs with the supported `classIndex`.
4. Compare the target snapshot with the final snapshot after the workload is reverted. Persistent retained growth is stronger evidence than a single increase in allocated memory.
5. Account for normal cache warm-up, delayed cleanup, garbage collection timing, and workload differences before concluding a leak exists.

## Workflow 3 — Inspect retainers and dominators

When a class or object type grows unexpectedly:

1. Use `get_heapsnapshot_class_nodes` to list representative instances.
2. Inspect `get_heapsnapshot_retainers`, `get_heapsnapshot_retaining_paths`, `get_heapsnapshot_dominators`, and `get_heapsnapshot_edges` as available to identify why objects remain reachable.
3. Use `get_heapsnapshot_object_details` with the observed `nodeId` to inspect object metadata, size, type, distance, and detachedness where supported.
4. Use `get_heapsnapshot_duplicate_strings` if string growth dominates the diff.
5. Read [references/common-leaks.md](references/common-leaks.md) for likely causes and remedies.
6. Trace the retaining path back to application code before proposing a fix. A suspicious class name alone is not sufficient evidence.

## Workflow 4 — Categorized filters

Use `get_heapsnapshot_details` or `get_heapsnapshot_class_nodes` with a `filterName` only when that parameter and filter are supported by the active tool schema. Useful categories may include:

- `objectsRetainedByDetachedDomNodes`: objects retained by detached DOM nodes.
- `objectsRetainedByEventHandlers`: objects retained by event handlers.
- `objectsRetainedByContexts`: objects retained by closures or execution contexts.
- `objectsRetainedByConsole`: objects retained through console references/logging.

Treat filters as leads for investigation, not proof of a defect. Tool names, filter values, and parameters can vary by MCP version; use the live schema rather than inventing arguments.

## Fix and verify

Choose a fix only after identifying a plausible retaining path. Examples include removing listeners, cleaning up subscriptions and observers, clearing timers, bounding caches, or releasing references when a component is disposed.

1. State the observed retaining path and explain why it indicates unintended retention.
2. Apply a minimal, scoped change only when authorized.
3. Repeat the same workload and capture equivalent snapshots.
4. Compare retained objects and sizes before and after, including the post-revert state.
5. Verify functional behavior and check for regressions.
6. Close loaded heap snapshots and report which snapshots were closed.

## Reporting requirements

Report:
- runtime inspected (browser page, extension/service worker, or Node.js process);
- workload and snapshot IDs;
- summary/diff evidence and suspicious retaining paths;
- confirmed findings versus hypotheses;
- fix applied (or recommended) and before/after evidence;
- limitations, unavailable tools, and cleanup performed.

Never claim a leak is fixed solely because a snapshot was captured or a memory number temporarily decreased.
