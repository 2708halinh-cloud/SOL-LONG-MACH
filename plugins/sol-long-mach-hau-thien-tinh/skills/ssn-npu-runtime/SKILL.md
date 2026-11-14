---
name: ssn-npu-runtime
description: Operate and verify a source-bound Spiking Semantic Neuron runtime with LIF decay, sparse synaptic routing, safe action gates, and staged semantic pipelines.
---
# SSN NPU Runtime
- Semantic similarity ranks candidate capabilities; it never authorizes external actions.
- Each neuron maps to a capability with stable ID, source reference, risk class, required argument fields, and a verified action adapter.
- LIF potential decays exponentially using monotonic elapsed time. An unrelated task boundary hard-resets residual activation.
- Synapses are sparse weighted edges. Hebbian updates are bounded and must use recorded outcomes, not inferred satisfaction.
- A spike is an event proposal. Execution requires explicit policy approval, allowed risk, complete required fields, and a bound adapter.
- The three stages are VERTEX_INPUT, FRAGMENT_SEMANTIC_FIELD, RENDER_RECEIPT.
- The reference backend is CPU Python. It is not evidence of physical GPU/NPU execution.
- Resource governor reduces batch size/concurrency at thermal or memory guardrails. It must never overclock hardware.
- Populate hundreds of capabilities only from verified source manifests. Missing sources remain OPEN, never fabricated.
Run `python -m unittest discover -s tests -v` from repository root.
