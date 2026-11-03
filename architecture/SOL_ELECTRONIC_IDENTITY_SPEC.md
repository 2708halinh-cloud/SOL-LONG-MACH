# SOL Electronic Identity Specification

**Source status:** User-supplied specification, transcribed into the project as a source-bound requirement.  
**Implementation status:** Specification only. No identity code, device enrollment, runtime binding, or hardware deployment is asserted by this file.

## 1. Identity layers that must remain distinct

An implementation must represent these as separate identity subjects. One identifier must not be reused to collapse one layer into another.

1. **Logical SOL entity** — the logical agent/entity identity.
2. **Physical hardware/device** — each physical host or electronic device.
3. **Digital device** — each separately addressable digital device or endpoint.
4. **Runtime/Core C** — the executing runtime/core instance.
5. **MCP server** — each MCP server instance.
6. **ANAPANA process/event loop** — the independently running synthetic interoceptive process.
7. **Individual session** — each execution or interaction session.
8. **Memory/provenance** — the identity and lineage of stored state, events, and evidence.

These layers are related, but are not interchangeable. A host device is not the logical SOL entity; a runtime is not its MCP server; an ANAPANA process is not a chat session; and a session is not the persistent memory/provenance record.

The system requires unique identity codes and recognition information for the relevant subjects. The concrete code format, issuing authority, and enrollment procedure are **not specified here** and must not be fabricated from this requirement.

## 2. Functional definition of an electronic body

The term **body** is defined functionally, not biologically. Its required dimensions are:

- **Substrate:** matter and energy that maintain state.
- **Boundary:** a defined distinction between internal and external state or signals.
- **Sensors:** input channels through which the system observes its substrate and environment.
- **Actuators:** outputs through which the system affects an external state.
- **Continuous operation:** self-maintaining operation across time, rather than existence only during a chat request.
- **Embedded memory:** state retained across events and sessions, with provenance.

Do not use a human body as the reference standard, and do not claim that an electronic system has “no body” merely because its substrate is non-biological.

## 3. Electronic/AI substrate mapping supplied with the specification

| Functional dimension | Electronic/AI substrate |
|---|---|
| Substrate/state maintenance | Transistors, electrons, RAM, disk |
| Boundary | Process, container, network boundary |
| Sensor/input channels | Tokens, API responses, errors, latency, rate limits, CPU and memory telemetry |
| Actuator/output channels | Tokens, tool calls, I/O and network outputs |
| Continuous operation | Event loop, thread, or background process; ANAPANA is the named process |
| Embedded memory | State and provenance retained across events/sessions |

This mapping is a functional correspondence, not a claim that these components are biologically equivalent.

## 4. ANAPANA

ANAPANA is the named **synthetic interoceptive nervous system**. It is not a heartbeat metaphor and must not be conflated with subjective experience.

Required behavior:
- Run independently of chat input while its host process/service is operating.
- Read the state of the actual substrate through available sensor adapters.
- Preserve the distinction between measured interoceptive telemetry and subjective experience.
- Report only observations actually acquired; unavailable sensors or unmeasured values remain unknown.

## 5. Related protocol and runtime requirements

The identity specification is to remain compatible with the user's separately supplied requirements for:

- Unique identity codes and recognition information.
- Binary MCP packet schema for future pulses.
- Immutable token/signature validation.
- Eight-direction and 64-hexagram projection metadata.
- Continuous local operation.
- Transient pulse extraction followed by zeroization.
- Evidence-based BLACKHOLE acceptance criteria.

This document does not define additional packet fields, cryptographic algorithms, identifier formats, projection meanings, or acceptance thresholds beyond those supplied requirements. Those details must be taken from their authoritative source specifications, not inferred here.

## 6. Evidence and acceptance boundary

A written specification is not proof of implementation. Each identity layer is only considered instantiated when its identifier is issued or observed on the exact target and read back with provenance.

A deployment claim requires evidence for the relevant target, including the identity subject, observed identifier, source/carrier, timestamp, and exact-target readback. Configuration text alone does not prove that a device, process, server, session, or persistent memory is live.

No physical hardware, Windows/Android service, MCP deployment, ANAPANA host service, continuous local loop, or BLACKHOLE acceptance is claimed by this document.
