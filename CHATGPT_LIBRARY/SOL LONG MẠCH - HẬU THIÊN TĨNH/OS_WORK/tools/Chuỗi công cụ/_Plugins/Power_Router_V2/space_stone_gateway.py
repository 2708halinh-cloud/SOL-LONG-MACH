#!/usr/bin/env python3
"""SPACE_STONE common gate. Pure routing + injectable, verifiable provider actions.

A ChatGPT tag is not provisioned by writing this file: installed plugin hosts must
bind their @SPACE_STONE callback to this route with authorized provider adapters.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from typing import Any, Protocol

CANONICAL_SPEC_REL = Path('CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE/SPACE_STONE_UNIFIED_GATE_CURRENT.json')


def locate_registry() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / CANONICAL_SPEC_REL
        if candidate.is_file():
            return candidate
    # For local isolation tests or a downloaded one-file bundle only.
    return Path(__file__).with_name('SPACE_STONE_UNIFIED_GATE_CURRENT.json')

REGISTRY = locate_registry()


def norm(value: str) -> str:
    value = unicodedata.normalize('NFD', value.casefold().replace('đ', 'd'))
    return ''.join(c for c in value if unicodedata.category(c) != 'Mn')


def registry() -> dict:
    data = json.loads(REGISTRY.read_text(encoding='utf-8'))
    if data.get('schema') != 'SOL_SPACE_STONE_UNIFIED_GATE/1.0':
        raise ValueError('SPACE_GATE_SCHEMA_MISMATCH')
    if len(data['five_capabilities']) != 5:
        raise ValueError('FIVE_CAPABILITIES_REQUIRED')
    return data


def plan(task: str, mode: str | None = None) -> dict:
    """Compose one tagged gate to SPACE/TIME/TEREX/Tools without a fake action."""
    if not task or not task.strip():
        raise ValueError('TASK_REQUIRED')
    manifest = registry()
    aliases = manifest['five_capabilities']
    normalized = norm(task)
    explicit = {cap['id']: cap for cap in aliases}
    if mode:
        choice = explicit.get(mode.upper().strip())
        if not choice:
            raise ValueError('UNKNOWN_SPACE_MODE')
    else:
        hits = [(len(norm(word)), cap) for cap in aliases for word in cap['invoke']
                if norm(word) in normalized]
        choice = max(hits, key=lambda item: item[0])[1] if hits else aliases[1]
    return {
        'schema':'SOL_SPACE_STONE_PLAN/1.0',
        'gateway':'@SPACE_STONE',
        'operation':choice['id'],
        'software_capability':choice['implemented'],
        'delegated_skill':choice['skill'],
        'space_anchor':manifest['canonical_anchor'],
        'relation':'SPACE ↔ SOUL, MIND ↔ POWER, REALITY ↔ TIME; center TÂM (0)',
        'next':'RESOLVE_PROVIDER_STABLE_IDS_AUTH_AND_CAPABILITY',
        'action_executed':False,
        'provider_receipt':None,
        'readback':None,
        'physical_action_claimed':False,
    }


class Provider(Protocol):
    """Authorized provider adapter implemented by a caller, NOT by this module."""
    def read(self, entity_id: str) -> bytes: ...
    def write(self, target_id: str, content: bytes, *, overwrite: bool) -> Any: ...
    def move(self, source_id: str, target_id: str) -> Any: ...
    def probe(self, entity_id: str) -> dict: ...


def copy_verified(source: Provider, destination: Provider,
                  source_id: str, target_id: str, *, overwrite: bool = False) -> dict:
    """Cross-provider portal = copy+readback. Never delete the original."""
    if not source_id or not target_id:
        raise ValueError('SOURCE_DEST_STABLE_IDS_REQUIRED')
    before = source.read(source_id)
    if not isinstance(before, bytes):
        raise TypeError('PROVIDER_READ_MUST_RETURN_BYTES')
    receipt = destination.write(target_id, before, overwrite=overwrite)
    if not receipt:
        raise RuntimeError('DESTINATION_PROVIDER_RECEIPT_MISSING')
    after = destination.read(target_id)
    if before != after:
        raise RuntimeError('PORTAL_READBACK_HASH_MISMATCH')
    return {'action':'CROSS_PROVIDER_COPY','status':'DESTINATION_READBACK_VERIFIED',
            'source_id':source_id,'target_id':target_id,
            'sha256':hashlib.sha256(before).hexdigest(),
            'size_bytes':len(before),'provider_receipt':receipt,
            'source_deleted':False,'cross_provider_identity_unchanged':False}


def move_verified(provider: Provider, source_id: str, target_id: str) -> dict:
    """Same-provider move only when adapter reports actual mutation and readback."""
    if not source_id or not target_id or source_id == target_id:
        raise ValueError('DISTINCT_SOURCE_AND_DESTINATION_REQUIRED')
    before = provider.read(source_id)
    if not isinstance(before,bytes):
        raise TypeError('PROVIDER_READ_MUST_RETURN_BYTES')
    receipt = provider.move(source_id,target_id)
    if not receipt:
        raise RuntimeError('MOVE_PROVIDER_RECEIPT_MISSING')
    after = provider.read(target_id)
    if after != before:
        raise RuntimeError('MOVE_READBACK_HASH_MISMATCH')
    return {'action':'SAME_PROVIDER_MOVE','status':'DESTINATION_READBACK_VERIFIED',
            'source_id':source_id,'target_id':target_id,
            'sha256':hashlib.sha256(after).hexdigest(),'provider_receipt':receipt,
            'provider_report_only_source_detached':True}


def portal_probe(left:Provider,right:Provider,left_id:str,right_id:str) -> dict:
    """Shows two callable provider endpoints, NOT network tunnel or wormhole."""
    if not left_id or not right_id:
        raise ValueError('TWO_ENDPOINT_IDS_REQUIRED')
    a,b=left.probe(left_id),right.probe(right_id)
    if not (a.get('reachable') and b.get('reachable') and a.get('authorized') and b.get('authorized')):
        return {'status':'OPEN','ready':False,'left':a,'right':b,'connection_established':False}
    return {'status':'ENDPOINTS_PROBED','ready':True,'left':a,'right':b,
            'connection_established':False,'next':'BIND_VALIDATED_OPERATION_AND_EXECUTE'}


def space_transform(point:tuple[float,float], delta:tuple[float,float]) -> dict:
    """Logical coordinate transform for a spatial graph, NOT physical metric bending."""
    if len(point)!=2 or len(delta)!=2:
        raise ValueError('TWO_DIMENSIONAL_COORDINATES_REQUIRED')
    x,y=point[0]+delta[0],point[1]+delta[1]
    return {'status':'TRANSFORM_CALCULATED','source_xy':list(point),'target_xy':[x,y],
            'physical_space_modified':False,'geometry_written':False}


def resource_budget(cpu_seconds:float, memory_mb:int, energy_wh:float|None=None) -> dict:
    """Plan authorized compute allocation; no electrical power creation/weapon energy."""
    if cpu_seconds<0 or memory_mb<0 or energy_wh is not None and energy_wh<0:
        raise ValueError('BUDGET_MUST_BE_NONNEGATIVE')
    return {'status':'RESOURCE_BUDGET_PLANNED','cpu_seconds_max':cpu_seconds,
            'memory_mb_max':memory_mb,'energy_wh_max':energy_wh,
            'provider_allocation_executed':False,'physical_energy_generated':False}


def spacetime_reentry(entity_id:str, revision:str, events:list[dict]) -> dict:
    """Join SPACE identity with TIME event history; no actual time travel."""
    found=[v for v in events if v.get('entity_id')==entity_id and v.get('revision')==revision]
    return {'status':'REVISION_FOUND' if found else 'REVISION_NOT_OBSERVED',
            'entity_id':entity_id,'revision':revision,'matches':found,
            'real_time_reversed':False,
            'next':'PROVIDER_READBACK_OF_SELECTED_REVISION' if found else 'TRACE_HISTORICAL_CARRIERS'}


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--task',required=True)
    a.add_argument('--mode',choices=[x['id'] for x in registry()['five_capabilities']])
    b=a.parse_args()
    print(json.dumps(plan(b.task,b.mode),ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
