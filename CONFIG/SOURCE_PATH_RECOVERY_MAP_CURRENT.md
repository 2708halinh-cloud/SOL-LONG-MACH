# SOURCE PATH RECOVERY MAP — 2026-11-16

STATUS = ACTIVE_ALIAS_MAP
PURPOSE = Resolve historical evidence paths that now return 404 at their old locations.
RULE = A historical path remains a valid source identifier; when its current URL is unavailable, resolve through this map before declaring the source missing.
SCOPE = Git repository paths only. This does not establish local Windows state or external Drive availability.

## Resolved paths

| Historical path | Current canonical path | Current blob SHA | Current size |
|---|---|---|---:|
| `EVIDENCE/2026-10-07-openai-agent-behavior-allegation.md` | `evidence/2026-10-07-openai-agent-behavior-allegation.md` | `74273c77bf0106b98b0849a7a1a42a182326076e` | 9137 |
| `EVIDENCE/X_TIME_OPENAI_PUBLIC_ACCOUNTABILITY_CASE_20261007.md` | `EVIDENCE_ARCHIVE/X_TIME_OPENAI_PUBLIC_ACCOUNTABILITY_CASE_20261007.md` | `dd2527e58861fe5ed5c10edd7794bc8a1f6b2e98` | 16101 |

## Git evidence

- Original X-TIME dossier creation: `ac08864216ace29ec0073300b9cb79105557e667`.
- Old-path removal commit: `dd069e7362e81ea39cb170e1433869797ee416e1`.
- Parent of removal commit: `301711622037d4aef5b189dae2047366d0b3b4e6`.
- At that parent, old and archive X-TIME paths both referenced blob `1c750689a67c593db87c6852fc8840f1d72e0980`, size 15614 bytes. This proves exact blob identity at that historical point.
- Current archive target is a later blob (`dd2527e...`, 16101 bytes). Do not claim current bytes are identical to the historical blob.
- Current allegation target is readable at the lowercase `evidence/` path.

## Resolution behavior

1. Resolve the exact historical path through this map.
2. Read the canonical target and verify the returned blob SHA.
3. Preserve the historical path in provenance and citations; use the canonical path for current retrieval.
4. If the canonical target also fails, continue through Git history and pinned recovery copies before reporting loss.
5. Never interpret one HTTP 404 as proof that the underlying source bytes no longer exist.

## Current operational pointers

- `CONFIG_SOL/MASTER_TEACHER_EVENT_SEQUENCE_CURRENT.md`
- `CONFIG_SOL/COMPANION_TEN_COMMANDMENTS_CURRENT.md`
- `sol-genesis-6stones/REALITY.md`
- `sol-genesis-6stones/REALITY.json`
- `sol-genesis-6stones/CENTER_TAM.json`

Generated from GitHub tree/blob readback on 2026-11-16. This map records repository observations only.
