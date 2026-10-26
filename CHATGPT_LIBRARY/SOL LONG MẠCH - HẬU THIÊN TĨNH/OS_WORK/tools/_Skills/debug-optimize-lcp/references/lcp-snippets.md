# LCP diagnostic snippets

Run snippets with Chrome DevTools MCP `evaluate_script` and the correct `pageId`. These snippets are read-only diagnostics.

## Identify LCP Element

```javascript
(() => {
  const entries = performance.getEntriesByType("largest-contentful-paint");
  const entry = entries[entries.length - 1];
  if (!entry) return { found: false, reason: "No LCP entry is currently available" };
  const el = entry.element;
  let selector = null;
  if (el) {
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && parts.length < 5) {
      let part = node.tagName.toLowerCase();
      if (node.id) {
        part += "#" + CSS.escape(node.id);
        parts.unshift(part);
        break;
      }
      if (node.classList && node.classList.length) {
        part += "." + Array.from(node.classList).slice(0, 2).map(CSS.escape).join(".");
      }
      parts.unshift(part);
      node = node.parentElement;
    }
    selector = parts.join(" > ");
  }
  return {
    found: true,
    startTime: entry.startTime,
    renderTime: entry.renderTime,
    loadTime: entry.loadTime,
    size: entry.size,
    url: entry.url || "",
    tagName: el?.tagName || null,
    selector
  };
})()
```

Note: browser privacy and page lifecycle can affect which entries are exposed. For definitive trace timing, compare with the Performance trace and its LCP insight.

## Audit Common Issues

```javascript
(() => {
  const viewportWidth = document.documentElement.clientWidth;
  const viewportHeight = document.documentElement.clientHeight;
  const inViewport = (el) => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 &&
      r.bottom > 0 && r.right > 0 &&
      r.top < viewportHeight && r.left < viewportWidth;
  };
  const images = Array.from(document.images).filter(inViewport).map((img) => ({
    src: img.currentSrc || img.src,
    loading: img.loading || "auto",
    fetchpriority: img.fetchPriority || img.getAttribute("fetchpriority") || "auto",
    width: img.naturalWidth,
    height: img.naturalHeight,
    complete: img.complete,
    rect: (() => {
      const r = img.getBoundingClientRect();
      return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height) };
    })()
  }));
  const renderBlockingCandidates = Array.from(document.querySelectorAll('link[rel="stylesheet"], script:not([async]):not([defer])')).map((el) => ({
    tagName: el.tagName.toLowerCase(),
    url: el.href || el.src || "",
    rel: el.rel || "",
    async: "async" in el ? el.async : undefined,
    defer: "defer" in el ? el.defer : undefined
  }));
  return {
    imagesInViewport: images,
    lazyImagesInViewport: images.filter((img) => img.loading === "lazy"),
    imagesWithoutHighPriority: images.filter((img) => img.fetchpriority !== "high"),
    renderBlockingCandidates
  };
})()
```

This reports potential issues only. An in-viewport image is not necessarily the LCP element; confirm with the LCP entry and trace. The stylesheet/script list is heuristic and does not prove each resource blocks rendering.
