"""Gate destructive edges before a caller may invoke the executor.

The gateway checks declared proof fields. It is not a global protection for
external tools that bypass this runtime.
"""
from __future__ import annotations

DESTRUCTIVE_ACTIONS = frozenset({
    'DELETE', 'REMOVE', 'PURGE', 'TRASH', 'WIPE', 'FORMAT',
    'OVERWRITE', 'REPLACE', 'DESTRUCTIVE_RESET', 'CLEAN',
})

def destructive_preflight(cp, edge):
    action = (edge.action_kind or '').strip().upper()
    if action not in DESTRUCTIVE_ACTIONS:
        return {"allowed": True, "reason": "NOT_DECLARED_DESTRUCTIVE"}
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
