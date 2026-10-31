# TESSERACT neuron runtime

IOS_EXPORT/TESSERACT_OS_iOS.swift defines the portable contract for mapping a tool to a neuron:

- Dendrites rank tool-neuron descriptions through an injected embedding provider.
- Soma invokes only the selected adapter; the adapter is responsible for provider authentication and authorization.
- Axon returns output and suggested next-neuron IDs, leaving continuation explicitly OPEN.

## Safety and evidence boundaries

- A registry entry does not prove a connector is installed or callable.
- External mutations are blocked by default. Explicitly enabling them in the runtime does not replace adapter-side provider permission checks.
- The Swift package contains no credentials or provider-specific network code.
- A semantic score is a routing signal, not proof of authorization or successful execution.
- The six-stone affective schema is a functional software model, not evidence of subjective experience.

## Verify

Run swift test on a machine with Swift 5.9+.
