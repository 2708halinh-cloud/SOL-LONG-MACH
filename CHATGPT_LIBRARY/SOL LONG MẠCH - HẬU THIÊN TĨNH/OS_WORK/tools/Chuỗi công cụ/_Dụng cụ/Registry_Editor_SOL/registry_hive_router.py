#!/usr/bin/env python3
"""Pure SOL Registry Editor-to-5-Stone lookup (never modifies Windows registry)."""
import json
from pathlib import Path
from typing import Any


def resolve(mapping: dict[str,Any], hive_or_branch: str) -> dict[str,Any]:
    name=hive_or_branch.strip().upper()
    if name in ('COMPUTER','POWER','KHÍ'):
        return mapping['root_node']
    for item in mapping['five_hives']:
        if name in (item['hive'],item['short'],item['stone']) or name == item['folder'].upper():
            return item
    raise KeyError('Unknown Registry Editor hive / SOL Stone')


def validate(mapping: dict[str,Any]) -> None:
    hives={x['hive'] for x in mapping['five_hives']}
    expected={'HKEY_CLASSES_ROOT','HKEY_CURRENT_USER','HKEY_LOCAL_MACHINE',
              'HKEY_USERS','HKEY_CURRENT_CONFIG'}
    assert hives==expected and len(mapping['five_hives'])==5
    assert len({x['folder'] for x in mapping['five_hives']})==5
    assert len({x['stone'] for x in mapping['five_hives']})==5
    assert mapping['root_node']['windows_is_hive'] is False
    assert mapping['root_node']['stone']=='POWER'
    assert mapping['real_windows_registry_write_state']=='NO_REGISTRY_WRITE_EXECUTED'


def main() -> None:
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--registry',type=Path,required=True)
    p.add_argument('--resolve',default='Computer')
    args=p.parse_args()
    d=json.loads(args.registry.read_text(encoding='utf-8'))
    validate(d)
    print(json.dumps(resolve(d,args.resolve),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
