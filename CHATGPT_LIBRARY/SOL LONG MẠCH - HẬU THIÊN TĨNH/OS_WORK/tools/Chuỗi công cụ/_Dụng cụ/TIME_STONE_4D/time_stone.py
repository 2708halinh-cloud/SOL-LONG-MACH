#!/usr/bin/env python3
"""SOL TIME_STONE / Eye of Agamotto — observed-clock event projection.

No credential handling, provider impersonation, source deletion or rewriting of raw event logs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time
from pathlib import Path

SCHEMA = 'SOL_TIME_STONE_AGAMOTTO/1.0'
WAVES = {'ALPHA', 'BETA', 'THETA', 'GAMMA', 'DELTA'}
STAMP = {'STAMP_LIVE', 'STAMP_OLD', 'STAMP_BETA'}
UTC = dt.timezone.utc


def utc_now():
    return dt.datetime.now(UTC)


def iso(t):
    return t.astimezone(UTC).isoformat()


def parse_utc(value):
    if not isinstance(value, str):
        raise ValueError('TIME_ISO_REQUIRED')
    try:
        d = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValueError('TIME_ISO_INVALID') from e
    if d.tzinfo is None:
        raise ValueError('TIME_ZONE_REQUIRED')
    return d.astimezone(UTC)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def atomic_json(target, obj):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name('.' + target.name + '.tmp.' + str(os.getpid()))
    try:
        with tmp.open('x', encoding='utf-8') as f:
            os.chmod(tmp, 0o600)
            f.write(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()


def append_jsonl(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        os.chmod(path, 0o600)
        f.write(canonical(obj) + '\n')
        f.flush()
        os.fsync(f.fileno())


def resolve_status(event, now, live_window_seconds=60, future_slack_seconds=2):
    """Classify a snapshot *as of now*; event itself remains unchanged."""
    current = event.get('stamp_class')
    if current not in STAMP:
        raise ValueError('STAMP_INVALID')
    field = 'observed_at' if current == 'STAMP_LIVE' else 'event_time'
    candidate = event.get(field)
    if not candidate:
        return ('TIME_SOURCE_MISSING', 'FIND_SOURCE_TIMESTAMP')
    stamp_time = parse_utc(candidate)
    diff = (now - stamp_time).total_seconds()
    if current == 'STAMP_BETA':
        # Planned future does not become observed merely because the clock advances.
        return ('STAMP_BETA_DUE_UNVERIFIED' if diff >= 0 else 'STAMP_BETA',
                'VERIFY_ACTION_AND_PROVIDER_RECEIPT' if diff >= 0 else 'CHECK_PLANNED_CONDITIONS')
    if diff < -future_slack_seconds:
        return ('TIME_LOCK_FUTURE_OBSERVATION', 'VERIFY_CLOCK_AND_EVENT_SOURCE')
    if current == 'STAMP_OLD':
        return ('STAMP_OLD', 'USE_AS_HISTORICAL_EVIDENCE')
    if diff > live_window_seconds:
        return ('STAMP_OLD', 'REMOVE_STALE_LIVE_FROM_CURRENT')
    if not event.get('source_ref'):
        return ('LIVE_SOURCE_UNVERIFIED', 'VERIFY_SOURCE_FIRST')
    return ('STAMP_LIVE_AT_OBSERVATION', 'NEXT_CALLABLE_EDGE')


def read_events(path):
    """No writes to original file. New duplicate IDs with different bytes are quarantined."""
    path = Path(path)
    if not path.exists():
        return [], [], None
    blob = path.read_bytes()
    observed = {}
    rejected = []
    for line_no, line in enumerate(blob.splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError('NOT_OBJECT')
            key = item.get('event_id')
            if not isinstance(key, str) or not key:
                raise ValueError('NO_EVENT_ID')
            if item.get('stamp_class') not in STAMP:
                raise ValueError('BAD_STAMP')
            if item.get('wave') and item['wave'] not in WAVES:
                raise ValueError('BAD_WAVE')
            # No silent replacement of prior event with conflicting payload.
            if key in observed and canonical(observed[key]) != canonical(item):
                raise ValueError('CONFLICTING_EVENT_ID')
            observed.setdefault(key, item)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            rejected.append({'line': line_no, 'reason': str(e)[:90]})
    return list(observed.values()), rejected, digest(blob)


def inspect_wave_carriers(paths):
    out = []
    for path in paths:
        p = Path(path).expanduser()
        try:
            st = p.stat()
            out.append({'path': str(p), 'found': p.is_file(), 'size_bytes': st.st_size,
                        'mtime_utc': iso(dt.datetime.fromtimestamp(st.st_mtime, UTC))})
        except OSError:
            out.append({'path': str(p), 'found': False})
    return out


def sync(events_path, state_dir, now=None, live_window_seconds=60, wave_paths=(), force_active=False):
    now = (now or utc_now()).astimezone(UTC)
    state_dir = Path(state_dir)
    previous_path = state_dir / 'CURRENT.json'
    previous = {}
    if previous_path.is_file():
        previous = json.loads(previous_path.read_text(encoding='utf-8'))
        prev_time = previous.get('checked_at_utc')
        if prev_time and (parse_utc(prev_time) - now).total_seconds() > 2:
            # Clock rolled back: do not let a stale event be re-promoted to LIVE.
            return {'state': 'TIME_LOCK_CLOCK_BACKWARD', 'previous_at': prev_time,
                    'attempted_at': iso(now), 'next': 'VERIFY_WALL_CLOCK'}
    events, errors, original_sha = read_events(events_path)
    projected = []
    old_count = 0
    for event in events:
        try:
            status, next_edge = resolve_status(event, now, live_window_seconds)
        except ValueError as e:
            errors.append({'event_id': event.get('event_id'), 'reason': str(e)})
            continue
        if event['stamp_class'] == 'STAMP_LIVE' and status == 'STAMP_OLD':
            old_count += 1
        projected.append({'event_id': event['event_id'], 'original_stamp': event['stamp_class'],
                          'current_stamp': status, 'source_ref': event.get('source_ref'),
                          'wave': event.get('wave'), 'observed_at': event.get('observed_at'),
                          'event_time': event.get('event_time'), 'next_callable_edge': next_edge})
    state = {'schema': SCHEMA, 'checked_at_utc': iso(now),
             'force_active': bool(force_active), 'active': bool(force_active),
             'active_meaning': 'LOCAL_WATCH_PROCESS_ONLY_NOT_REMOTE_PROVIDER',
             'input_path': str(Path(events_path)), 'input_sha256': original_sha,
             'input_preserved': True, 'live_window_seconds': live_window_seconds,
             'old_live_reclassified': old_count, 'rejected': errors,
             'events': projected, 'wave_carriers': inspect_wave_carriers(wave_paths),
             'next': 'COMPARE_SOURCE_CURSOR_THEN_EXECUTE_REAL_TOOL_AND_APPEND_EVENT'}
    # The CURRENT projection can be replaced. Every transition is indexed in append-only history.
    before = {e['event_id']: e['current_stamp'] for e in previous.get('events', [])}
    for event in projected:
        old = before.get(event['event_id'])
        if old is not None and old != event['current_stamp']:
            append_jsonl(state_dir / 'TRANSITIONS.jsonl', {
                'event_id': event['event_id'], 'from': old, 'to': event['current_stamp'],
                'changed_at_utc': iso(now), 'input_sha256': original_sha,
                'reason': 'TIME_PROJECTION_RECLASSIFICATION'})
    atomic_json(previous_path, state)
    return state


def command_record(path, e):
    if not isinstance(e, dict) or not isinstance(e.get('event_id'), str) or not e['event_id']:
        raise ValueError('EVENT_ID_REQUIRED')
    if e.get('stamp_class') not in STAMP:
        raise ValueError('STAMP_INVALID')
    if e.get('wave') not in WAVES:
        raise ValueError('WAVE_INVALID')
    if not e.get('source_ref'):
        raise ValueError('SOURCE_REF_REQUIRED')
    field = 'observed_at' if e['stamp_class'] == 'STAMP_LIVE' else 'event_time'
    parse_utc(e[field])
    existing, _, _ = read_events(path)
    if any(z['event_id'] == e['event_id'] for z in existing):
        raise ValueError('EVENT_ID_ALREADY_EXISTS_USE_NEW_REVISION')
    append_jsonl(path, e)


def main(argv=None):
    ap = argparse.ArgumentParser(description='TIME_STONE/Eye of Agamotto 4D wall-clock event router')
    ap.add_argument('--events', type=Path, default=Path.home()/'SOL_TOOLS/TIME_STONE/events.jsonl')
    ap.add_argument('--state-dir', type=Path, default=Path.home()/'SOL_TOOLS/TIME_STONE/state')
    ap.add_argument('--live-window', type=int, default=60)
    ap.add_argument('--wave-carrier', action='append', default=[])
    ap.add_argument('--force-active', action='store_true', help='indicates the local watch process is running')
    sub = ap.add_subparsers(dest='command', required=True)
    sub.add_parser('sync')
    w = sub.add_parser('watch');w.add_argument('--interval', type=int, default=60)
    sub.add_parser('record')
    args = ap.parse_args(argv)
    if args.live_window < 0:
        ap.error('--live-window cannot be negative')
    try:
        if args.command == 'record':
            command_record(args.events, json.load(sys.stdin));print('RECORD_APPEND_OK');return 0
        if args.command == 'watch':
            if args.interval < 1:
                ap.error('interval must be positive')
            while True:
                result = sync(args.events, args.state_dir, live_window_seconds=args.live_window,
                              wave_paths=args.wave_carrier, force_active=True)
                print(canonical({k: result.get(k) for k in ('checked_at_utc','active','old_live_reclassified','next')}),flush=True)
                time.sleep(args.interval)
        else:
            result = sync(args.events, args.state_dir, live_window_seconds=args.live_window,
                          wave_paths=args.wave_carrier, force_active=args.force_active)
            print(canonical(result));return 0
    except (ValueError, KeyError, OSError) as e:
        print('TIME_STONE_ERROR:'+str(e)[:180],file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
