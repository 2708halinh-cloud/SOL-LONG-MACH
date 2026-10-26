---
name: debug-optimize-lcp
description: Guides debugging and optimizing Largest Contentful Paint (LCP) using Chrome DevTools MCP tools. Use when the user asks about LCP performance, slow page loads, Core Web Vitals optimization, or why a page's main content takes too long to appear. Also use for "largest contentful paint", "page load speed", "CWV", or improving hero-image or main-content rendering.
---

# Debug and optimize Largest Contentful Paint (LCP)

Use this workflow with Chrome DevTools MCP. Do not claim a measurement or fix without collecting evidence from the target page.

## LCP thresholds

- **Good:** 2.5 seconds or less.
- **Needs improvement:** greater than 2.5 seconds and up to 4.0 seconds.
- **Poor:** greater than 4.0 seconds.

These thresholds are evaluated at the 75th percentile of real-user page loads, segmented by mobile and desktop. A single DevTools trace is a lab sample, not a substitute for field data.

## Debugging workflow

### 1. Record a page-load trace

1. Use `list_pages` and identify the correct `pageId`, or navigate to the target URL.
2. Start a load trace using `performance_start_trace` with `pageId`, `reload: true`, and `autoStop: true`.
3. Record the LCP timing and available insight-set IDs from the returned trace. If a tool's current schema differs, follow its exposed schema rather than guessing parameters.

### 2. Analyze trace insights

Use `performance_analyze_insight` with the correct `pageId`, insight-set ID, and insight name present in the trace output. Prioritize:
- `LCPBreakdown`: LCP subpart timings.
- `DocumentLatency`: document response / TTFB issues.
- `RenderBlocking`: render-blocking resources.
- `LCPDiscovery`: whether the LCP resource was discovered early.

Only request insight names and IDs actually returned by the trace.

### 3. Identify the LCP element

Use `evaluate_script` with `pageId` and the **Identify LCP Element** snippet in [references/lcp-snippets.md](references/lcp-snippets.md). Record the element selector/tag, image or resource URL when present, and raw LCP timing. An empty resource URL often indicates a text LCP element.

### 4. Inspect the network waterfall

1. Use `list_network_requests` with `pageId` and a resource-type filter such as `["image", "font"]`; adjust based on the observed LCP element.
2. Find the matching request and inspect it with `get_network_request`, using the request ID returned by the tool.
3. Compare request start time and duration with document response and LCP timing. Do not infer causality from file size alone.

### 5. Audit likely implementation issues

Use `evaluate_script` with `pageId` and the **Audit Common Issues** snippet in [references/lcp-snippets.md](references/lcp-snippets.md). Inspect lazy loading on an above-the-fold LCP image, `fetchpriority`, resource discovery, render-blocking CSS/JS, and long main-thread tasks. Treat the snippet as a diagnostic aid, not a complete audit.

## Map evidence to an optimization

LCP consists of four sequential phases: TTFB, resource load delay, resource load duration, and element render delay. Their proportions vary by page; treat percentage targets as diagnostic heuristics, not universal laws. Focus on the largest measured bottleneck.

### Resource load delay
- Make the LCP resource discoverable in initial HTML when possible.
- Do not lazy-load an above-the-fold LCP image.
- Consider `fetchpriority="high"` on the actual LCP image.
- Preload only when evidence shows discovery is late and the preload is correct; avoid duplicate or unused preloads.

### Element render delay
- Reduce render-blocking CSS and synchronous JavaScript.
- Inline only necessary critical CSS and defer non-critical work where appropriate.
- Break up long main-thread tasks.
- Consider server-rendering or otherwise making the LCP content available in initial HTML when client-side rendering delays it.

### Resource load duration
- Resize and compress images appropriately; consider AVIF/WebP and responsive `srcset`/ `sizes`.
- Improve delivery and caching (including CDN use where appropriate).
- If text LCP is blocked by a web font, inspect font loading and consider `font-display: swap` when it suits the design.

### TTFB
- Investigate server response latency, redirects, caching, and backend work.
- Consider edge caching where appropriate.
- Check bfcache eligibility for navigation scenarios where it is relevant; bfcache is not a general fix for a cold page-load TTFB.

## Verify changes

1. Repeat the same trace with `performance_start_trace` using `pageId`, `reload: true`, and `autoStop: true`.
2. Compare before/after LCP and each available subpart; keep conditions as similar as possible.
3. If supported by the active MCP schema, use `emulate` with `pageId`, `networkConditions: "Fast 3G"`, and `cpuThrottlingRate: 4` to assess constrained conditions.
4. Distinguish lab results from field data. Use real-user monitoring / Core Web Vitals field data for production conclusions.

## Reporting requirements

Report the target URL, measurement conditions, observed LCP element, measured bottleneck, proposed or applied changes, and before/after evidence. Separate hypotheses from confirmed findings. Do not edit production code or deploy a fix unless the user has authorized that scope.
