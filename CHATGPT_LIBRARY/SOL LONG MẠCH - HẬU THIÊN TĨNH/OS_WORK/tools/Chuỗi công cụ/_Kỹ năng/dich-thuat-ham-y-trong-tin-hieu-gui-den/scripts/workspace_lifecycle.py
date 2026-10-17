#!/usr/bin/env python3
"""SPACE_STONE worktree lifecycle decision assistant (read-only / no provider calls)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def decide(c: dict) -> dict:
    if not isinstance(c, dict):
        raise ValueError('OBJECT_REQUIRED')
    if c.get('operation') not in ('select', 'archive', 'restore'):
        raise ValueError('OPERATION_REQUIRED')
    op=c['operation']; matched=bool(c.get('existing_suitable'))
    busy=bool(c.get('active_task') or c.get('active_process') or c.get('in_use'))
    protected=bool(c.get('pinned') or c.get('shared'))
    pending=bool(c.get('unaccounted_changes') or c.get('uncommitted_work'))
    tool=set(c.get('callable_tools', []))
    if op=='archive':
        if busy or protected or c.get('remaining_dependencies'):
            action='PRESERVE_WORKTREE'
        elif c.get('important_ignored_unpreserved'):
            action='PRESERVE_IGNORED_FIRST'
        elif 'archive_worktree' in tool:
            action='ARCHIVE_WITH_MANAGED_TOOL'
        else:
            action='NEED_ARCHIVE_TOOL';
    elif op=='restore':
        if not (c.get('user_requested_restore') or c.get('premature_archive_for_specific_task')):
            action='DO_NOT_RESTORE'
        elif 'restore_worktree' in tool:
            action='RESTORE_WITH_MANAGED_TOOL'
        else:
            action='NEED_RESTORE_TOOL'
    elif matched:
        action=('CONTINUE_ACTIVE_WORKTREE' if busy else 'ACCOUNT_FOR_EXISTING_CHANGES' if pending else 'REUSE_EXISTING_WORKTREE')
    elif c.get('isolation_required') or c.get('no_reusable_workspace'):
        if not c.get('base_ref') or not c.get('branch'):
            action='PREPARE_BASE_AND_BRANCH'
        elif 'create_worktree' in tool:
            action='CREATE_MANAGED_WORKTREE'
        elif c.get('allow_manual_fallback'):
            action='MANUAL_WORKTREE_FALLBACK'
        else:
            action='DISCOVER_WORKTREE_TOOL'
    else:
        action='DISCOVER_EXISTING_WORKSPACE'
    return {
      'schema':'SOL_SPACE_WORKTREE_DECISION/1.0',
      'action':action,
      'can_archive_without_ignored_backup':False if c.get('important_ignored_unpreserved') else True,
      'pr_closure_requested':False,
      'requires_provider_action':action in ('ARCHIVE_WITH_MANAGED_TOOL','RESTORE_WITH_MANAGED_TOOL','CREATE_MANAGED_WORKTREE','MANUAL_WORKTREE_FALLBACK'),
      'actual_provider_action_executed':False,
      'path_verified':False,
    }


def tests() -> None:
    cases=[
      ({'operation':'select','existing_suitable':True},'REUSE_EXISTING_WORKTREE'),
      ({'operation':'select','existing_suitable':True,'active_task':True},'CONTINUE_ACTIVE_WORKTREE'),
      ({'operation':'select','existing_suitable':True,'unaccounted_changes':True},'ACCOUNT_FOR_EXISTING_CHANGES'),
      ({'operation':'select'},'DISCOVER_EXISTING_WORKSPACE'),
      ({'operation':'select','isolation_required':True},'PREPARE_BASE_AND_BRANCH'),
      ({'operation':'select','isolation_required':True,'base_ref':'main','branch':'feat/a','callable_tools':['create_worktree']},'CREATE_MANAGED_WORKTREE'),
      ({'operation':'select','no_reusable_workspace':True,'base_ref':'main','branch':'feat/a'},'DISCOVER_WORKTREE_TOOL'),
      ({'operation':'select','no_reusable_workspace':True,'base_ref':'main','branch':'feat/a','allow_manual_fallback':True},'MANUAL_WORKTREE_FALLBACK'),
      ({'operation':'archive','active_process':True,'callable_tools':['archive_worktree']},'PRESERVE_WORKTREE'),
      ({'operation':'archive','pinned':True,'callable_tools':['archive_worktree']},'PRESERVE_WORKTREE'),
      ({'operation':'archive','shared':True,'callable_tools':['archive_worktree']},'PRESERVE_WORKTREE'),
      ({'operation':'archive','remaining_dependencies':True,'callable_tools':['archive_worktree']},'PRESERVE_WORKTREE'),
      ({'operation':'archive','important_ignored_unpreserved':True,'callable_tools':['archive_worktree']},'PRESERVE_IGNORED_FIRST'),
      ({'operation':'archive','callable_tools':['archive_worktree']},'ARCHIVE_WITH_MANAGED_TOOL'),
      ({'operation':'archive'},'NEED_ARCHIVE_TOOL'),
      ({'operation':'restore'},'DO_NOT_RESTORE'),
      ({'operation':'restore','user_requested_restore':True,'callable_tools':['restore_worktree']},'RESTORE_WITH_MANAGED_TOOL'),
      ({'operation':'restore','premature_archive_for_specific_task':True},'NEED_RESTORE_TOOL'),
    ]
    for i,(payload,expected) in enumerate(cases,1):
        got=decide(payload)
        assert got['action']==expected,(i,got,expected)
        assert not got['actual_provider_action_executed']
    try:
        decide({'operation':'delete'})
        raise AssertionError('must reject unknown op')
    except ValueError:
        pass
    print('PASS 19/19 SPACE_STONE workspace lifecycle decisions')


def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument('--input');ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    if args.self_test:tests();return
    if not args.input:ap.error('--input or --self-test required')
    print(json.dumps(decide(json.loads(Path(args.input).read_text(encoding='utf-8'))),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
