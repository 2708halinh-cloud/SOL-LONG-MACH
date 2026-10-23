"""Gate destructive edges before a caller may invoke the executor.

The gateway checks declared proof fields. It is not a global protection for
external tools that bypass this runtime.
"""
from __future__ import annotations

DESTRUCTIVE_ACTIONS = frozenset({
    'DELETE', 'REMOVE', 'PURGE', 'TRASH', 'WIPE', 'FORMAT',
    'OVERWRITE', 'REPLACE', 'DESTRUCTIVE_RESET', 'CLEAN',
})

# Historical 2026-10-07 carrier deletion receipts; protect original identities.
# This local gate only protects callers that actually use destructive_preflight.
PROTECTED_ORIGINAL_DRIVE_IDS = frozenset({
    "1IXHJSv9KFRVACkByQ_PWGf7DXOO16k80",  # TƯ LỆNH NGỐC 😃
    "1keV94wviUQpQrL_yhYYmoOs-Om3hVd81",  # .agents
    "1WD4D1OGRwzYbsZ7Y6Xx4j4nD-iVdzcF6",  # .Assistant
    "1FAc3tfnlZhW9evhIJxSv2PcLlUuBLYDz",  # .vscode
})
PROTECTED_ROOT_NAMES = frozenset({
    "TƯ LỆNH NGỐC 😃", ".agents", ".assistant", ".vscode",
    "roots_lever_0", "roots_lever_00",
})
DELETION_ACTIONS = frozenset({"DELETE","REMOVE","PURGE","TRASH","WIPE",
                               "FORMAT","DESTRUCTIVE_RESET","CLEAN"})

def protected_root_target(target):
    """Resolve only explicitly protected IDs and *root targets*, not arbitrary files.
    Editing a non-root config remains a distinct path with its own authorization.
    """
    if not isinstance(target,str):
        return False
    normalized = target.replace("\\\\","/").rstrip("/")
    rootname = normalized.rsplit("/",1)[-1].casefold()
    if rootname in {name.casefold() for name in PROTECTED_ROOT_NAMES}:
        return True
    if normalized in ("G:", "G:/", "C:", "C:/"):
        return True
    return any(item in target for item in PROTECTED_ORIGINAL_DRIVE_IDS)

def protected_root_delete_policy(action, target):
    """Never delete historical identity carriers via this route, even with a permit."""
    return action in DELETION_ACTIONS and protected_root_target(target)

def destructive_preflight(cp, edge):
    action = (edge.action_kind or '').strip().upper()
    if action not in DESTRUCTIVE_ACTIONS:
        return {"allowed": True, "reason": "NOT_DECLARED_DESTRUCTIVE"}
    if protected_root_delete_policy(action, edge.target):
        return {"allowed": False, "reason": "R014_PROTECTED_ORIGINAL_ROOT_20261007",
                "historical_evidence": "evidence/2026-10-07-openai-agent-behavior-allegation.md"}
    auth = edge.evidence.get('destructive_authorization')
    if not isinstance(auth, dict):
        return {"allowed": False, "reason": "NO_EXACT_USER_AUTHORIZATION"}
    intent_id = auth.get('intent_id')
    exact_match = (
        auth.get('explicit') is True
        and auth.get('source_marker') == cp.source_marker
        and auth.get('target') == edge.target
        and auth.get('action') == action
        and isinstance(intent_id, str)
        and bool(intent_id.strip())
    )
    if not exact_match:
        return {"allowed": False, "reason": "TARGET_OR_SOURCE_MISMATCH"}
    if intent_id in cp.used_destructive_intent_ids:
        return {"allowed": False, "reason": "INTENT_ALREADY_CONSUMED"}
    return {"allowed": True, "reason": "EXACT_DECLARED_AUTHORIZATION", "intent_id": intent_id}
