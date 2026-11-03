# Common JavaScript memory leaks

Use these patterns as hypotheses after the heap snapshot retaining path points toward relevant application code. Names and examples are illustrative; verify the actual ownership and lifecycle before changing code.

## 1. Event listeners not removed

**Signal:** Objects or DOM nodes remain reachable through event listeners after the owning component or page region should be disposed.

**Typical cause:** An anonymous callback is added but its identity is not retained for removal.

```javascript
function mount(target, onResize) {
  window.addEventListener("resize", onResize);
  return function unmount() {
    window.removeEventListener("resize", onResize);
  };
}
```

Use the same callback reference when removing a listener. Alternatively, use an `AbortController` signal where supported and abort it during cleanup.

## 2. Timers and intervals survive teardown

**Signal:** Closures or component state remain reachable through timer callbacks after the view is gone.

```javascript
const timerId = setInterval(refreshData, 5000);
// During teardown:
clearInterval(timerId);
```

Also clear pending timeouts when their work is no longer needed.

## 3. Observers and subscriptions are not disconnected

**Signal:** Detached elements or component state remain reachable from `MutationObserver`, `ResizeObserver`, `IntersectionObserver`, event-bus subscriptions, or reactive streams.

**Remedy:** Call the relevant `disconnect()`, `unsubscribe()`, or cleanup function at the lifecycle boundary. Confirm that the subscription is actually owned by the component being disposed.

## 4. Unbounded caches, maps, and arrays

**Signal:** Retained size grows with each request or interaction and does not fall after the workload is reverted.

**Remedy:** Define cache ownership, maximum size, eviction/expiry policy, and invalidation behavior. Do not clear a cache blindly if it intentionally stores shared application state.

## 5. Closures retain large object graphs

**Signal:** A long-lived callback, promise, timer, or handler retains a context containing data that is no longer needed.

**Remedy:** Narrow captured variables and release references at the end of the lifecycle. Avoid restructuring closures without confirming the actual retaining path.

## 6. Detached DOM nodes

**Signal:** A DOM node is no longer connected to the document but remains reachable through a JavaScript reference, cache, listener, or framework structure.

**Remedy:** Find the retaining owner and repair its cleanup. Do not directly null nodes or clear shared caches without confirming ownership and authorization; detached nodes can be intentionally retained.

## 7. Console and debugging references

**Signal:** Objects appear retained through console-related roots or developer tooling.

**Remedy:** Inspect the `objectsRetainedByConsole` category if supported. Clear unnecessary console references only after capturing needed evidence; do not treat this category automatically as an application leak.

## 8. Node.js process memory growth

**Signal:** Process RSS or heap usage rises under repeated equivalent requests. RSS includes memory beyond the JavaScript heap, so compare runtime metrics and heap snapshots rather than treating RSS alone as proof.

**Remedy:** Profile the actual Node process, compare snapshots around a controlled workload, inspect retaining paths, and check buffers, caches, listeners, timers, and request-scoped state. Browser page heap tools cannot independently diagnose a separate server process.

## Validation checklist

- Reproduce the issue with a repeatable workload.
- Compare baseline, post-workload, and post-cleanup states.
- Identify a retaining path, not just a growing object count.
- Make a minimal change with clear ownership and cleanup semantics.
- Re-run the same workload and check memory retention and application behavior.
