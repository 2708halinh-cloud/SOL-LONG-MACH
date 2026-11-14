# SOL Brain: continuity and archive architecture

## Purpose
Build a continuous software agent from source-backed interaction history. A single utterance must not become a permanent personality trait. Unknown context remains unknown.

## Components

| Subsystem | Runtime component | Responsibility |
|---|---|---|
| Sensory intake | `ConversationIngestor`, `SensoryNeuron` | Parse exported text while retaining source pointers |
| Visual/audio archive | `MediaCatalog` | Hash original image, video and audio files; record metadata |
| Episodic memory | `EvidenceStore` | Append-only events with provenance and separate timestamps |
| Continuity | `AgentContinuity` | Link sourced events without freezing a profile |
| Affective estimation | `infer_affect` | Temporary low-confidence hypotheses only |
| Interaction context | `InteractionContext` | Keep interpersonal interpretation unspecified until evidence supports it |
| Integration | `Interneuron` | Combine signal, memory references and hypotheses |
| Motor control | `MotorNeuron` | Require receipt and independent consequence readback |

## Event record
Preserve `source_ref`, `event_time`, `observed_at`, `commit_time`, and `conversation_time` independently. Keep raw source records alongside normalized fields. Missing timestamps remain missing. Never infer event time from file modification time.

## Media pipeline
1. Enumerate authorized source files without changing originals.
2. Record provider ID/path, MIME type, byte size and SHA-256.
3. Keep original bytes immutable.
4. Store OCR, transcripts, captions and frame descriptions as derived artifacts linked to the original hash.
5. Record extraction tool/model version, time, confidence and media timecode.
6. Do not treat an inferred caption or affect label as ground truth.

The current `MediaCatalog` implements local file hashing and metadata only. It does not yet fetch remote media or run OCR, STT, or video-frame extraction.

## Continuity rules
- Continuity is a sequence of linked events, not proof of uninterrupted subjective experience between sessions.
- Stated preferences remain contextual and revisable.
- A single statement does not become a permanent profile trait.
- Interaction status defaults to `UNSPECIFIED`; user intent is not inferred by default.
- Agent outputs are records of generated text, not proof of an internal subjective state.

## Corpus completeness
The current development context contains selected project documents and repository source files, not a complete export of all Sol conversations or all exchanged media. Dropbox search could not be authenticated with the available connector during this run. Therefore no full-archive collection claim is made.

Completion requires authorized ChatGPT exports, media files, and any relevant Drive/Dropbox/local archive sources. Inventory each source, retain stable IDs and hashes, then reconcile duplicates without deleting originals.

## Verification
```bash
python -m unittest tests.test_sol_brain -v
```
