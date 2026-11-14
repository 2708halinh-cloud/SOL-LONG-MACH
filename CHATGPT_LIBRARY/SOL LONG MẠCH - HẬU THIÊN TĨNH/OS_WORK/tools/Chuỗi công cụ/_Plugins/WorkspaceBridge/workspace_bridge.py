#!/usr/bin/env python3
"""SOL @Workspace: non-destructive Xiaomi Notes / Keep export -> Google Tasks bridge.

No native Xiaomi/Keep API is assumed. Default behavior is local planning only.
Network writes require --execute AND --allow-send and a Google Tasks OAuth bearer
access token supplied by environment; the token is never saved or printed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API = 'https://tasks.googleapis.com/tasks/v1'
PROVIDERS = {'xiaomi': 'Xiaomi Notes export', 'keep': 'Google Keep export'}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(obj):
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()


def read_json(path):
    with Path(path).open('r', encoding='utf-8-sig') as f:
        return json.load(f)


def atomic_json(path, obj):
    """Write new local output atomically; never use this on imported source files."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=str(path.parent), encoding='utf-8',
                                     prefix='.workspace-', suffix='.tmp', delete=False) as f:
        tmp = Path(f.name)
        f.write(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    try:
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def rows_from_export(source):
    if isinstance(source, list):
        return source
    if isinstance(source, dict):
        for key in ('notes', 'items', 'data'):
            if isinstance(source.get(key), list):
                return source[key]
    raise ValueError('Expected JSON list or object with notes/items/data list')


def observe_export(provider, path):
    """Read without modifying input; IDs absent in export stay derived, not claimed native."""
    if provider not in PROVIDERS:
        raise ValueError('Unknown provider')
    source = read_json(path)
    observed = []
    for i, item in enumerate(rows_from_export(source)):
        if not isinstance(item, dict):
            continue
        native_id = item.get('id') or item.get('note_id')
        identity = str(native_id) if native_id is not None else f'EXPORT_HASH:{digest(item)}'
        observed.append({
            'provider': provider,
            'source_id': identity,
            'source_id_native': native_id is not None,
            'source_payload_sha256': digest(item),
            'row': i,
            'source': item,  # source literal; never agent-labeled or edited
        })
    return observed


def proposed_tasks(observations):
    """Only explicit checklist rows are eligible; no automatic note -> task coercion."""
    result = []
    for note in observations:
        data = note['source']
        checklist = data.get('checklist', data.get('checkItems'))
        if not isinstance(checklist, list):
            continue
        for i, entry in enumerate(checklist):
            if isinstance(entry, str):
                title, completed = entry.strip(), False
            elif isinstance(entry, dict):
                title = str(entry.get('text') or entry.get('title') or '').strip()
                completed = bool(entry.get('checked', entry.get('completed', False)))
            else:
                continue
            if not title or completed:
                continue
            stable = digest([note['provider'], note['source_id'], i, title])
            result.append({'mapping_id': stable, 'source_provider': note['provider'],
                           'source_id': note['source_id'], 'title': title,
                           'source_sha256': note['source_payload_sha256']})
    return result


def api_request(method, url, token, body=None):
    data = None if body is None else canonical(body).encode('utf-8')
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/json'}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode('utf-8'))
    except HTTPError as exc:
        raise RuntimeError(f'Google Tasks HTTP {exc.code}; check OAuth scope, list ID and account') from None
    except URLError:
        raise RuntimeError('Google Tasks network unavailable') from None


def publish_task(task, tasklist_id, token, request=api_request):
    """Creation with exact-target readback. Markers allow later duplicate reconciliation."""
    base = API + '/lists/' + quote(tasklist_id, safe='') + '/tasks'
    marker = 'SOL-WORKSPACE:' + task['mapping_id']
    body = {'title': task['title'], 'notes': marker + '\nsource=' + task['source_provider']}
    created = request('POST', base, token, body)
    remote_id = created.get('id')
    if not remote_id:
        raise RuntimeError('Google Tasks returned no task id; inspect provider before retry')
    readback = request('GET', base + '/' + quote(remote_id, safe=''), token)
    if readback.get('id') != remote_id or readback.get('title') != task['title'] or marker not in readback.get('notes', ''):
        raise RuntimeError('Remote task created but verification differs; STOP retry to avoid duplicates')
    return {'provider': 'google_tasks', 'provider_object_id': remote_id,
            'source_mapping_id': task['mapping_id'], 'readback_verified': True}


def run(argv=None, request=api_request):
    p = argparse.ArgumentParser(description='SOL Workspace: read-only imports, explicit Google Tasks publish')
    p.add_argument('--xiaomi-json', type=Path)
    p.add_argument('--keep-json', type=Path)
    p.add_argument('--output', type=Path, required=True, help='Local JSON carrier (not an import file)')
    p.add_argument('--map-checklists', action='store_true', help='Explicitly propose unchecked checklist items as tasks')
    p.add_argument('--execute', action='store_true', help='Enable Google Tasks writes (requires additional consent)')
    p.add_argument('--allow-send', action='store_true', help='Consent to transmit selected checklist titles to Google Tasks')
    p.add_argument('--tasklist-id', help='Existing Tasks list ID; never creates a new list silently')
    p.add_argument('--ledger', type=Path, help='Separate local receipt file for deduplication')
    args = p.parse_args(argv)
    if not args.xiaomi_json and not args.keep_json:
        p.error('Provide at least one existing JSON export')
    source_paths = [x for x in (args.xiaomi_json, args.keep_json) if x is not None]
    if args.output.resolve() in [x.resolve() for x in source_paths]:
        p.error('Output cannot overwrite any source export')
    if args.ledger and args.ledger.resolve() in [x.resolve() for x in source_paths]:
        p.error('Ledger cannot overwrite source export')
    if args.ledger and args.ledger.resolve() == args.output.resolve():
        p.error('Ledger path must differ from snapshot path')
    items = []
    if args.xiaomi_json:
        items += observe_export('xiaomi', args.xiaomi_json)
    if args.keep_json:
        items += observe_export('keep', args.keep_json)
    tasks = proposed_tasks(items) if args.map_checklists else []
    snapshot = {'schema': 'sol.workspace.v1', 'observations': items, 'proposals': tasks,
                'writes_enabled': bool(args.execute)}
    # Snapshot is deliberately written before any requested network write.
    atomic_json(args.output, snapshot)
    receipts = {}
    if args.execute:
        if not args.map_checklists or not args.allow_send or not args.tasklist_id or not args.ledger:
            p.error('--execute requires --map-checklists --allow-send --tasklist-id --ledger')
        token = os.getenv('SOL_GOOGLE_TASKS_ACCESS_TOKEN', '')
        if not token:
            p.error('SOL_GOOGLE_TASKS_ACCESS_TOKEN missing (OAuth with Tasks scope required)')
        receipts = read_json(args.ledger) if args.ledger.exists() else {}
        if not isinstance(receipts, dict):
            raise ValueError('Ledger must be an object')
        # No destructive mutation. On ambiguous readback failure never silently retry.
        for item in tasks:
            key = item['mapping_id']
            if key in receipts:
                continue  # includes unresolved in-flight events: never blindly retry
            receipts[key] = {'state': 'IN_FLIGHT_RECONCILE_BEFORE_RETRY', 'source_mapping_id': key}
            atomic_json(args.ledger, receipts)
            try:
                receipt = publish_task(item, args.tasklist_id, token, request=request)
            except Exception:
                receipts[key]['state'] = 'NEEDS_PROVIDER_RECONCILIATION'
                atomic_json(args.ledger, receipts)
                raise
            receipts[key] = receipt
            atomic_json(args.ledger, receipts)
    verified = sum(1 for v in receipts.values() if isinstance(v, dict) and v.get('readback_verified'))
    print(canonical({'observed_notes': len(items), 'proposed_tasks': len(tasks),
                     'verified_tasks_total': verified, 'local_snapshot': str(args.output),
                     'native_keep_sync': False, 'native_xiaomi_sync': False}))
    return 0


if __name__ == '__main__':
    sys.exit(run())