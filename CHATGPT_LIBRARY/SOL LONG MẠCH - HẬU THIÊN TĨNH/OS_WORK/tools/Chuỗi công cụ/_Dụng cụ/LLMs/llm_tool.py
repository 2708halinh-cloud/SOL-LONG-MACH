#!/usr/bin/env python3
"""LLM provider = optional tool, never SOL agent authority/identity."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

CONTRACT = Path(__file__).with_name('LLM_TOOL_CONTRACT_CURRENT.json')


def config():
    return json.loads(CONTRACT.read_text(encoding='utf-8'))


def route(engine, environ=None):
    env = os.environ if environ is None else environ
    candidates = [x for x in config()['engine_routes'] if x['id'] == engine]
    if not candidates:
        raise ValueError('UNREGISTERED_LLM_TOOL')
    a = candidates[0]
    return a, env.get(a['url_env']) or a['default_url'], env.get(a['model_env']), (env.get(a['key_env']) if a['key_env'] else None)


def select(engine, environ=None):
    a, url, model, key = route(engine, environ)
    return {'tool': engine, 'url_configured': bool(url), 'model_configured': bool(model), 'credential_configured': bool(key), 'callable_verified': False, 'executed': False}


def target_url(url, engine):
    u = urlsplit(url.strip())
    if u.scheme not in ('https', 'http') or not u.netloc or u.username or u.password or u.query or u.fragment:
        raise ValueError('INVALID_LLM_ENDPOINT')
    if u.scheme == 'http':
        host = u.hostname or ''
        try:
            ip = ipaddress.ip_address(host)
            allowed = ip.is_private or ip.is_loopback
        except ValueError:
            allowed = host.lower() == 'localhost'
        if not allowed:
            raise ValueError('HTTP_ENDPOINT_MUST_BE_PRIVATE_OR_LOOPBACK')
    suffix = '/api/generate' if engine == 'ollama_local' else '/chat/completions'
    prefix = u.path.rstrip('/')
    return urlunsplit((u.scheme, u.netloc, prefix if prefix.endswith(suffix) else prefix + suffix, '', ''))


def payload(engine, model, prompt):
    if not model or not prompt or not prompt.strip():
        raise ValueError('MODEL_AND_PROMPT_REQUIRED')
    if engine == 'ollama_local':
        return {'model': model, 'prompt': prompt, 'stream': False}
    if engine == 'openai_compatible':
        return {'model': model, 'messages': [{'role':'user','content':prompt}], 'stream': False}
    raise ValueError('UNREGISTERED_LLM_TOOL')


def parse_output(engine, raw):
    j = json.loads(raw.decode('utf-8'))
    output = j.get('response') if engine == 'ollama_local' else j.get('choices', [{}])[0].get('message', {}).get('content')
    if not isinstance(output, str):
        raise ValueError('LLM_RESULT_INVALID')
    return output


def invoke(engine, prompt, environ=None, opener=urlopen):
    a, url, model, key = route(engine, environ)
    if not url or not model:
        raise ValueError('LLM_MODEL_OR_URL_NOT_CONFIGURED')
    if a['key_env'] and not key:
        raise ValueError('LLM_SECRET_NOT_CONFIGURED')
    headers = {'Content-Type': 'application/json'}
    if key:
        headers['Authorization'] = 'Bearer ' + key
    data = json.dumps(payload(engine, model, prompt), ensure_ascii=False).encode('utf-8')
    request = Request(target_url(url, engine), data=data, headers=headers, method='POST')
    with opener(request, timeout=20) as response:
        raw = response.read(4_194_305)
    if len(raw) > 4_194_304:
        raise ValueError('LLM_RESULT_TOO_LARGE')
    return {'role': 'LLM_TOOL_PROPOSAL_NOT_VERIFIED', 'tool': engine, 'model': model, 'text': parse_output(engine, raw)}


def main():
    cli = argparse.ArgumentParser(description='SOL replaceable LLM inference tool')
    cli.add_argument('action', choices=['inspect','select','run'])
    cli.add_argument('engine', nargs='?', choices=['ollama_local','openai_compatible'])
    args = cli.parse_args()
    if args.action == 'inspect':
        result = {'role': config()['llm_role'], 'providers': [select(a['id']) for a in config()['engine_routes']]}
    elif args.action == 'select':
        result = select(args.engine)
    elif args.engine:
        result = invoke(args.engine, sys.stdin.read())
    else:
        cli.error('engine required for select/run')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
