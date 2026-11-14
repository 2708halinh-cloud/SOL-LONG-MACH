#!/usr/bin/env python3
"""SOL -> Xiaomi Notes (Redmi/Termux) via Android ACTION_SEND.

This opens the real Xiaomi Notes receiver. It does not silently save a note;
commit/save depends on the Xiaomi Notes UI and user interaction.
"""
import argparse
import json
import subprocess
import sys

PACKAGE = 'com.miui.notes'
ACTION = 'android.intent.action.SEND'


def dispatch(text: str, runner=subprocess.run) -> dict:
    if not text.strip():
        raise ValueError('Empty note body')
    args = ['am', 'start', '--user', '0', '-a', ACTION, '-t', 'text/plain',
            '-p', PACKAGE, '--es', 'android.intent.extra.TEXT', text]
    result = runner(args, capture_output=True, text=True, timeout=12)
    return {
        'route': 'SOL_TOOLS_XIAOMI_NOTES_SEND',
        'target': PACKAGE,
        'action': ACTION,
        'intent_accepted': result.returncode == 0,
        'saved_note_verified': False,
        'result_class': ('INTENT_ACCEPTED' if result.returncode == 0 else 'INTENT_FAILED'),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Open Xiaomi Notes with text from stdin on a connected Android device')
    parser.add_argument('--text', help='Note text; stdin is preferred for privacy')
    args = parser.parse_args()
    body = args.text if args.text is not None else sys.stdin.read()
    try:
        status = dispatch(body)
    except (ValueError, subprocess.TimeoutExpired, OSError):
        status = {'route': 'SOL_TOOLS_XIAOMI_NOTES_SEND', 'intent_accepted': False,
                  'saved_note_verified': False, 'result_class': 'INVOKE_ERROR'}
    print(json.dumps(status, ensure_ascii=False))
    return 0 if status['intent_accepted'] else 1


if __name__ == '__main__':
    sys.exit(main())
