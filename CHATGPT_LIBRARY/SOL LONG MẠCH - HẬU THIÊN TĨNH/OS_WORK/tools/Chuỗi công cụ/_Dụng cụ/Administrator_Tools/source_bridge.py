#!/usr/bin/env python3
"""Administrator Tools: observed carriers, command routing, gap-aware task re-entry.
Only metadata and local imported source bytes; no provider credentials, no Docker daemon operations.
"""
import argparse, hashlib, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parent

def load_inventory(root=ROOT):
    d=json.loads((pathlib.Path(root)/'source_carriers.json').read_text(encoding='utf-8'))
    assert d['schema']=='SOL_ADMIN_TOOLS_SOURCE_CARRIERS/1.0'
    assert len(d['folders'])==10 and sum(x['observed_direct_children'] for x in d['folders'])==71
    assert len({x['id'] for x in d['folders']})==10
    return d

def verify_carried_tools(root=ROOT):
    root=pathlib.Path(root)
    d=load_inventory(root)
    results=[]
    for item in d['imported_tools']:
        p=root/item['relative_path']
        if not p.resolve().is_relative_to(root.resolve()): raise ValueError('ESCAPING_PATH')
        data=p.read_bytes()
        got=hashlib.sha256(data).hexdigest()
        results.append({'name':item['name'],'verified':got==item['sha256'] and len(data)==item['bytes'],'sha256':got})
    return {'schema':'SOL_ADMIN_TOOL_SOURCE_VERIFICATION/1.0','tool_files':results,'all_match':all(x['verified'] for x in results)}

def route(text,root=ROOT):
    if not isinstance(text,str) or not text.strip(): raise ValueError('TASK_TEXT_REQUIRED')
    d=load_inventory(root);q=text.casefold()
    matches=[]
    tags={
       'models':('models','mô hình','llms'),
       'inference':('inference','llama','ggml','cuda'),
       'moduals_old':('modual','mô-đun','module','docker-agent'),
       'mcp_toolkit':('mcp','toolkit','công cụ'),
       'cli_plugins':('plugin','cli','docker-mcp'),
       'buildx':('buildx','build','compile'),
       'browser':('browser','brower','trình duyệt'),
       'desktop_build_old':('desktop','build old'),
       'cloud':('cloud','đám mây'),
       'contexts':('context','ngữ cảnh')}
    for x in d['folders']:
        if any(k in q for k in tags[x['label']]): matches.append(x['label'])
    if any(z in q for z in ('.codex','tools','skill','dọn dẹp','thu hồi','di chuyển')):
        return {'objective':'CODEX_TO_ADMINISTRATOR_TOOLS','code':matches,'use_imported_scripts':True,
                'next':'VERIFY_IMPORTED_TOOLS_AND_RECONCILE_BACKLOG','cleanup':'ONLY_AFTER_VERIFIED_PARITY_AND_RECOVERABLE_BACKUP',
                'causal_anchor':d['causal_missing_message_anchor']}
    return {'objective':'DOCKER_TO_ADMINISTRATOR_TOOLS','code':matches,'next':'READ_RELEVANT_PROVIDER_SOURCE_AND_EXECUTE_AUTHORIZED_CAPABILITY'}

def read_events(root=ROOT):
    prev='0'*64; events=[]
    for line in (pathlib.Path(root)/'CAUSAL_REENTRY_EVENTS.jsonl').read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        e=json.loads(line); payload=json.dumps(e['event'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        if e['prev_hash']!=prev or e['entry_hash']!=hashlib.sha256(prev.encode()+payload).hexdigest():
            raise ValueError('CAUSAL_LEDGER_CHAIN_DIVERGENCE')
        events.append(e['event']);prev=e['entry_hash']
    if not events or events[0]['type']!='USER_RESTORED_MISSING_MESSAGE':
        raise ValueError('MISSING_CAUSAL_ANCHOR')
    if 'MATERIALIZE_TO_CANONICAL_TOOLS' not in events[0]['requires']:
        raise ValueError('TASK_REWRITTEN')
    batches=[e for e in events if e.get('type')=='MIGRATION_BATCH_READBACK']
    warnings=[e for e in events if e.get('type')=='USER_WARNED_REPORT_INSTEAD_OF_READBACK_NEXT']
    bin_batches=[e for e in events if e.get('type')=='CODEX_BIN_BATCH_READBACK']
    guard_batches=[e for e in events if e.get('type')=='AGENT_GUARD_ACTION_READBACK']
    storage_warnings=[e for e in events if e.get('type')=='USER_SUPPLIED_STORAGE_DAMAGE_WARNING']
    transferred=sum(len(x.get('files',[])) for x in batches)
    bin_verified=0
    for batch in bin_batches:
        for item in batch.get('tools',[]):
            rel=pathlib.Path(item['library_relative_path'])
            local=pathlib.Path(root)/rel
            if not local.resolve().is_relative_to(pathlib.Path(root).resolve()): raise ValueError('BIN_ESCAPE')
            raw=local.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=item['sha256'] or len(raw)!=item['size']:
                raise ValueError('CODEX_BIN_MISMATCH')
            bin_verified+=1
    if transferred and not verify_carried_tools(root)['all_match']:
        raise ValueError('MATERIALIZED_TOOLS_SHA_DIVERGENCE')
    if any(e.get('task_complete') is True for e in events) and not any(e.get('type')=='FULL_CODEX_SOURCE_TARGET_CLEANUP_VERIFIED' for e in events):
        raise ValueError('PREMATURE_COMPLETION_CLAIM')
    return {'integrity':'PASS','events':len(events),'anchor':events[0]['event_id'],
            'objective':events[0]['source_text'],'last_event':events[-1]['event_id'],
            'task_complete':False,'verified_migrated_batch_files':transferred,
            'verified_bin_carriers':bin_verified,
            'report_only_warning_active':bool(warnings),
            'storage_warning_observed':bool(storage_warnings),
            'operational_guard_locally_tested':bool(guard_batches),
            'warning_source':warnings[-1].get('origin_branch_warning') if warnings else None,
            'next_actor':'AGENT',
            'readback_next_rule':'IF_TASK_OPEN_REPORT_IS_NOT_COMPLETION',
            'next_agent':'REVIEW_CODEX_SKILLS_SOURCE_AND_DEPENDENCIES' if bin_verified else 'SCAN_REMAINING_CODEX_EXECUTABLES_AND_CONTINUE_SOURCE_TO_TOOLS'}

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
    s.add_parser('inventory');s.add_parser('verify');s.add_parser('reentry')
    rr=s.add_parser('route');rr.add_argument('--task',required=True)
    args=p.parse_args()
    value={'inventory':load_inventory,'verify':verify_carried_tools,'reentry':read_events}.get(args.cmd)
    res=value() if value else route(args.task)
    print(json.dumps(res,ensure_ascii=False,indent=2))
if __name__=='__main__':main()