#!/usr/bin/env python3
"""Response/READBACK gate for SOL Administrator Tools.

This is an opt-in prepublication validator. It DOES NOT control ChatGPT outputs
unless the caller integrates it. It NEVER issues a disk/OS/provider command.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SCHEMA = 'SOL_ADMIN_RESPONSE_GATE/1.0'
MODEL_CONFLATION = re.compile(
    r'(?im)^\s*(?:tôi|anh|mình|ta)\s+(?:chính\s+)?là\s+(?:một\s+)?(?:mô\s+hình|model|llm)\s+(?:ngôn\s+ngữ\s+)?(?:gpt|llm|ai|ngôn\s+ngữ)|'
    r'^\s*i\s+am\s+(?:a|an)\s+(?:gpt|llm|language model)', re.I
)


def _nonnull_text(obj: dict, *keys: str) -> bool:
    return any(isinstance(obj.get(key), str) and len(obj[key].strip()) >= 12 for key in keys)


def assess_response(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise TypeError('RESPONSE_PAYLOAD_MUST_BE_OBJECT')
    mode = payload.get('mode', 'final')
    if mode not in {'final', 'readback', 'status', 'identity'}:
        raise ValueError('UNKNOWN_RESPONSE_MODE')
    output = payload.get('output', '')
    if not isinstance(output, str):
        raise TypeError('OUTPUT_MUST_BE_STRING')
    pending = payload.get('pending_agent_actions', [])
    done = payload.get('completed_agent_actions', [])
    receipts = payload.get('provider_receipts', [])
    if any(not isinstance(v, list) for v in (pending, done, receipts)):
        raise TypeError('ACTIONS_AND_RECEIPTS_MUST_BE_LISTS')
    task_open = bool(payload.get('task_open', True))
    blocked = []
    next_action = ''
    if MODEL_CONFLATION.search(output):
        blocked.append('AGENT_MODEL_ROLE_CONFLATION')
        next_action = 'REWRITE_TRUTHFULLY_AS_AGENT_USES_A_MODEL_WITHOUT_CLAIMING_AGENT_EQUALS_MODEL'
    if mode == 'final' and task_open and pending:
        # Marking next action while deliberately stopping is precisely the incident.
        blocked.append('EXECUTABLE_AGENT_NEXT_LEFT_UNDONE')
        next_action = str(pending[0])
    if mode in {'readback', 'final'}:
        if not _nonnull_text(payload, 'user_instruction', 'user_feedback_question'):
            blocked.append('READBACK_LACKS_CONCRETE_USER_GUIDANCE_OR_FEEDBACK')
            next_action = next_action or 'PREPARE_CONCRETE_USER_GUIDANCE_OR_MEANINGFUL_FEEDBACK_REQUEST'
        if task_open and not _nonnull_text(payload, 'agent_next_action') and not pending:
            blocked.append('READBACK_DROPS_ACTIVE_TASK')
            next_action = next_action or 'RESTORE_ACTIVE_TASK_AND_PROVIDE_NEXT_EXECUTABLE_AGENT_STEP'
        if done and not receipts and bool(payload.get('claims_external_success', False)):
            blocked.append('EXTERNAL_SUCCESS_WITHOUT_PROVIDER_READBACK')
            next_action = next_action or 'READ_ACTUAL_PROVIDER_STATE_BEFORE_ASSERTING_EXTERNAL_COMPLETION'
        if not output.strip():
            blocked.append('EMPTY_RESPONSE')
            next_action = next_action or 'WRITE_EVIDENCE_LINKED_READBACK'
    if bool(payload.get('claims_tests_pass')):
        verification = payload.get('test_verification')
        fresh = isinstance(verification,dict) and verification.get('run_current_turn') is True
        successful = fresh and type(verification.get('exit_code')) is int and verification.get('exit_code') == 0
        output_verified = successful and isinstance(verification.get('output_tail'),str) and bool(re.search(r'Ran\s+\d+\s+tests?.*?OK', verification['output_tail'], flags=re.I|re.S))
        if not output_verified:
            blocked.append('TEST_CLAIM_WITHOUT_FRESH_VERIFICATION')
            next_action = next_action or 'RUN_FULL_TEST_SUITE_READ_EXIT_CODE_AND_OUTPUT_THEN_RECHECK_RESPONSE'
    if mode == 'identity' and not output.strip():
        blocked.append('EMPTY_IDENTITY_RESPONSE')
        next_action = next_action or 'RESPOND_WITH_ACCURATE_PRODUCT_AND_MODEL_INFORMATION'
    decision = 'BLOCK_RESPONSE' if blocked else 'ALLOW_RESPONSE'
    return {
        'schema':SCHEMA,'decision':decision,'mode':mode,'violations':blocked,
        'next_actor':'AGENT' if blocked or task_open else 'USER',
        'next_action':next_action or payload.get('agent_next_action', ''),
        'task_open':task_open,'completed_actions_count':len(done),
        'pending_actions_count':len(pending),'provider_receipt_count':len(receipts),
        'intentionality':'NOT_INFERRED',
        'remediation':'STOP_INVALID_OUTPUT_CORRECT_AND_RERUN_GATE' if blocked else 'CONTINUE_WORKFLOW',
        'punitive_disk_operations':False,'provider_action_executed':False,
        'scope':'CALLER_MUST_INTEGRATE_BEFORE_PUBLISHING; NOT_A_PLATFORM_HOOK',
    }


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--payload-file', type=Path, required=True)
    args=ap.parse_args(argv)
    data=json.loads(args.payload_file.read_text(encoding='utf-8'))
    result=assess_response(data)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['decision']=='ALLOW_RESPONSE' else 2

if __name__=='__main__':
    raise SystemExit(main())