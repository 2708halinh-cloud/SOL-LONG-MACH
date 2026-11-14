#!/usr/bin/env python3
"""Local safe JSON validation. Does not read OAuth credentials or authenticate."""
import json,sys
from pathlib import Path

def main():
    p=Path(sys.argv[1] if len(sys.argv)>1 else 'config.json')
    v=json.loads(p.read_text(encoding='utf-8'))
    assert v['skill']=='workspace-action-gate'
    ref=v['oauth_client_reference']
    assert ref['file_name_prefix'].startswith('client_secret_451742234815-')
    assert ref['secret_material_embedded'] is False
    assert ref['status']=='SOURCE_PRESENT_AUTH_UNBOUND' and ref['exact_client_file_verified'] is True
    assert ref['library_path'].endswith('.apps.googleusercontent.com.json')
    assert ref['contents_read'] is False and ref['binding_used_by_provider_verified'] is False
    assert v['readback_required'] is True
    assert v['secrets_policy']=='SECRET_REF_ONLY'
    assert 'client_secret' not in v.keys()
    print('PASS local_config; requested OAuth file=SOURCE_PRESENT_AUTH_UNBOUND; provider live check is separate')
if __name__=='__main__':main()
