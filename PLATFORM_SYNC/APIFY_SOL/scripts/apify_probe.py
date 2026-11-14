#!/usr/bin/env python3
"""Check Apify REST actors with bearer token from environment; never print token."""
import json
import os
import sys
import urllib.error
import urllib.request


def main():
    token = os.environ.get('APIFY_API_TOKEN', '')
    if not token:
        print('APIFY_API_TOKEN_NOT_CONFIGURED')
        return 2
    req = urllib.request.Request(
        'https://api.apify.com/v2/actors?limit=1000',
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json'},
        method='GET',
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            data = json.load(res)
        items = data.get('data', {}).get('items', [])
        wanted = 'nwua9Gu5YrADL7ZDj'
        print(json.dumps({'api_ok': True, 'items_count': len(items), 'target_actor_present': any(x.get('id') == wanted for x in items)}, ensure_ascii=False))
        return 0
    except urllib.error.HTTPError as err:
        print(json.dumps({'api_ok': False, 'http_status': err.code}))
        return 1
    except Exception as err:
        print('APIFY_API_PROBE_FAILED:' + type(err).__name__)
        return 1

if __name__ == '__main__':
    sys.exit(main())
