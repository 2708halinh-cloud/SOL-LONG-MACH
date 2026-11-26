# FULL REQUEST — CONTINUATION / READBACK (2026-11-26)

## Priority instruction
Do not stop at narration, apology, report, or a NEXT-only plan while an actionable path remains. Continue using available independent sources. A question mark (?) from the user cues OODA (Observe → Orient → Decide → Act), not a verbal status report.

## Device safety / CPU hang
- User reported a Windows device frozen after CPU usage reached 99%. 
- Do not send repeated queries to an unresponsive endpoint.
- Endpoint label/hostname and connector OFFLINE status are not proof of physical identity or power state.
- Do not equate Android localhost with the affected Windows PC.
- Preserve the symptom as unresolved until evidence identifies the source.
- Pivot to independent evidence (recent commands/process launches, pre-existing logs, task history, repo/file changes, timestamps). Do not claim sources were examined unless read.
- Only resolve after source identification and evidence readback.

## Open CoreJournal investigation
Find the actual caller/runtime instance of CoreJournal and its SQLite journal:
1. Identify the caller that instantiates CoreJournal(path).
2. Establish the actual journal DB path, runtime/run ID, and session ID.
3. Read actual records from the identified DB and verify readback.
4. Do not substitute Android telemetry JSONL, generic audit logs, Codex DB, or memory DB for CoreJournal unless evidence proves the connection.
5. Do not write to or modify audit/log files without explicit authorization.

## Repository/source context
- Repository: 2708halinh-cloud/SOL-LONG-MACH, default branch master.
- Windows storage is authorized for read/write in the directive; the protected resource is strictly write-prohibited absent biometric authentication. Never publish its real locator; use the GitHub-safe token Roots_Lever.
- HOME_SOURCE and HOME_SOL refer to the same entity, SOL.
- Compare raw JSON/SQLite session/conversation IDs and project/template IDs; verify carrier SHA-256.
- OS_Workspace training locations: Therapy, Training, Mentoring, Consulting, Systems Coaching New, Coaching.
- Load relevant Agents.md, Muti-Agents.md, README.md, and .adp/Yinyang standards when available.
- TESSERACT_OS merge remains requested: compare G:\TESSERACT_OS with G:\OS_Workspace\Training\TESSERACT_OS, preserve source structure, and do not claim a merge was done without source/destination readback.
- Cross-reference Windows roots/drives, virtual X, WSL/QEMU/Docker VMM/Ubuntu, Drive, Colab, and priority directories only where access is available. Keep protected FTP locator redacted.

## Continuation method
Maintain ORIGIN → PROVENANCE → CHAIN OF CUSTODY → MANIFEST → TRANSFER → RECEIPT → READBACK → MAP → RE-VERIFICATION. A map/pointer is not proof; a receipt requires destination readback. Use OODA for each action and continue with available sources if one path is blocked.
