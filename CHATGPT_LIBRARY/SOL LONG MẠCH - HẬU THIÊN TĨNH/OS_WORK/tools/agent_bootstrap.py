#!/usr/bin/env python3
"""Opt-in, local GGDV runtime startup hook. Works after a chat/RAM reset if invoked.

Verifies pinned artifact hashes and ledger first. Runs allowlisted local tests only
with --calibrate-if-due; no network, GitHub, Android, or provider write actions.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from agent_capability_lifecycle import CapabilityLedger, bootstrap


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    root = Path(__file__).resolve().parent
    p.add_argument('--manifest', type=Path, default=root/'capability_manifest.json')
    p.add_argument('--ledger', type=Path, required=True)
    p.add_argument('--session-id', required=True)
    p.add_argument('--core-db', type=Path)
    p.add_argument('--run-id')
    p.add_argument('--calibrate-if-due', action='store_true')
    a = p.parse_args(argv)
    try:
        before = bootstrap(a.manifest,a.ledger,session_id=a.session_id,
                           core_db_path=a.core_db,run_id=a.run_id)
        calibration = {}
        if a.calibrate_if_due:
            ledger = CapabilityLedger(a.ledger)
            try:
                for cap_id, state in before.capabilities.items():
                    if not state['status']['calibration_due']:
                        continue
                    def bounded_tests():
                        # Running tests is a local calibration only, never remote provider proof.
                        cmd = [sys.executable, '-m', 'unittest', '-q',
                               'test_agent_core_runtime.py', 'test_agent_capability_lifecycle.py']
                        proc = subprocess.run(cmd,cwd=str(a.manifest.parent),
                                              capture_output=True, text=True,timeout=40,
                                              env={**os.environ,'PYTHONPATH':str(a.manifest.parent)})
                        return {'passed':proc.returncode==0 and 'OK' in proc.stderr,
                                'exit_code':proc.returncode,
                                'test_suite':'core+capability',
                                'simulated':True}
                    calibration[cap_id] = ledger.calibrate(cap_id, bounded_tests)
            finally:
                ledger.close()
        after = bootstrap(a.manifest,a.ledger,session_id=a.session_id,
                          core_db_path=a.core_db,run_id=a.run_id)
        print(json.dumps({'schema':'GGDV_AGENT_BOOT/1.0',
                          'manifest_sha256':after.manifest_digest,
                          'checkpoint_source':after.checkpoint_source,
                          'blackboard_stage':after.blackboard['stage'],
                          'tool_invocation_claimed':False,
                          'provider_execution_claimed':after.provider_execution_claimed,
                          'capabilities':{key: value['status'] for key,value in after.capabilities.items()},
                          'calibration_receipts':calibration,
                          'ledger_head':after.ledger_head},ensure_ascii=False,indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({'schema':'GGDV_AGENT_BOOT/1.0','state':'DEGRADED',
                          'error_class':type(exc).__name__, 'detail':str(exc)[:250],
                          'provider_execution_claimed':False},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())