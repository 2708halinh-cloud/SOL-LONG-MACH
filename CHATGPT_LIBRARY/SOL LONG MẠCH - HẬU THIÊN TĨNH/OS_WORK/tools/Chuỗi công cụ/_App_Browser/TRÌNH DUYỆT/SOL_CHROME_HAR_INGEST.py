#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOL CHROME: HAR -> audited, minimized network receipts (offline, stdlib-only).

This tool never connects to Chrome or any network. It only processes a HAR
export supplied by the user. Raw HAR stays where it was exported.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

VERSION = "1.0.0"
ALLOW_HEADERS = {
    "content-type", "content-security-policy", "x-frame-options",
    "cache-control", "referrer-policy", "server-timing", "timing-allow-origin",
    "cross-origin-opener-policy", "cross-origin-embedder-policy",
}
SENSITIVE_URL_PARTS = ("token", "auth", "key", "password", "secret", "session", "code", "sig", "credential", "jwt")
TIMING_ENTRY = re.compile(r"\s*(?P<name>[!#$%&'*+.^_`|~0-9A-Za-z-]+)(?P<params>(?:\s*;[^,]*)?)\s*$")
DURATION = re.compile(r"(?:^|;)\s*dur\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*(?:;|$)", re.I)
DESCRIPTION = re.compile(r'(?:^|;)\s*desc\s*=\s*(?:"([^"]*)"|([^;,]*))\s*(?:;|$)', re.I)


def safe_url(raw):
    """Preserve chrome:// scheme, minimize accidental secret-bearing query data."""
    try:
        sp = urlsplit(str(raw))
        keep = []
        for k, v in parse_qsl(sp.query, keep_blank_values=True):
            if any(s in k.casefold() for s in SENSITIVE_URL_PARTS):
                keep.append((k, "[REDACTED]"))
            elif k == 'site':
                # Chrome's siteDetails route: retaining origin is useful, not its querystring.
                site = urlsplit(v)
                keep.append((k, urlunsplit((site.scheme, site.netloc, site.path, '', ''))))
            else:
                keep.append((k, v[:256]))
        return urlunsplit((sp.scheme, sp.netloc, sp.path, urlencode(keep), ''))
    except Exception:
        return "[UNPARSEABLE_URL]"


def cleaned_headers(raw_list):
    d = {}
    if not isinstance(raw_list, list):
        return d
    for h in raw_list:
        if not isinstance(h, dict):
            continue
        name = str(h.get('name', '')).lower()
        if name in ALLOW_HEADERS:
            value = str(h.get('value', ''))
            d[name] = value[:8192]
    return d


def parse_server_timing(value):
    if not value:
        return []
    result = []
    # Common Server-Timing syntax, not a full Structured Headers parser.
    # This split intentionally avoids breaking a comma within a quoted desc.
    for fragment in re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', value):
        m = TIMING_ENTRY.match(fragment)
        if not m:
            continue
        params = m.group('params') or ''
        dur = re.search(r'(?:^|;)\s*dur\s*=\s*([0-9]+(?:\.[0-9]+)?)\b', params, re.I)
        desc = re.search(r'(?:^|;)\s*desc\s*=\s*(?:"([^"]*)"|([^;,]*))', params, re.I)
        result.append({"name": m.group('name'), "duration_ms": float(dur.group(1)) if dur else 0.0,
                       "description": (desc.group(1) or desc.group(2) or '').strip() if desc else ''})
    return result


def receipt(entry, i):
    req = entry.get('request') or {}
    res = entry.get('response') or {}
    response_headers = cleaned_headers(res.get('headers'))
    request_headers = cleaned_headers(req.get('headers'))
    raw_url = str(req.get('url', ''))
    status = res.get('status')
    try:
        status = int(status)
    except (ValueError, TypeError):
        status = None
    duration = entry.get('time', None)
    try:
        duration = float(duration) if duration is not None else None
    except (ValueError, TypeError):
        duration = None
    source_id = hashlib.sha256((str(i) + '\0' + raw_url + '\0' + str(status)).encode('utf-8')).hexdigest()[:16]
    return {
        "source_index": i,
        "source_id": source_id,
        "startedDateTime": entry.get('startedDateTime'),
        "request": {"url": safe_url(raw_url), "method": req.get('method'), "headers": request_headers},
        "response": {"status": status, "statusText": res.get('statusText'), "headers": response_headers,
                     "content_type": (res.get('content') or {}).get('mimeType')},
        "total_time_ms": duration,
        "server_timing": parse_server_timing(response_headers.get('server-timing', '')),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Convert exported Chrome HAR into minimal, secret-filtered receipts")
    p.add_argument('har', type=Path, help='Chrome DevTools HAR export (prefer sanitized)')
    p.add_argument('--out', type=Path, default=Path('chrome_network_receipts'), help='Output directory')
    p.add_argument('--chrome-only', action='store_true', help='Keep only chrome:// resources')
    args = p.parse_args(argv)
    try:
        raw_bytes = args.har.read_bytes()
        data = json.loads(raw_bytes.decode('utf-8-sig'))
        entries = data['log']['entries']
        if not isinstance(entries, list):
            raise ValueError('log.entries must be an array')
    except (OSError, ValueError, KeyError, UnicodeDecodeError) as exc:
        p.error('Invalid HAR: ' + str(exc))
    args.out.mkdir(parents=True, exist_ok=True)
    all_receipts = []
    for idx, item in enumerate(entries):
        if not isinstance(item, dict):
            continue
        source_url = (item.get('request') or {}).get('url') or ''
        if args.chrome_only and not str(source_url).startswith('chrome://'):
            continue
        all_receipts.append(receipt(item, idx))
    jsonl = args.out / 'NETWORK_RECEIPTS.jsonl'
    jsonl.write_text(''.join(json.dumps(e, ensure_ascii=False, separators=(',', ':')) + '\n'
                            for e in all_receipts), encoding='utf-8')
    report = {
        'tool': 'SOL_CHROME_HAR_INGEST', 'version': VERSION, 'input_basename': args.har.name,
        'input_sha256': hashlib.sha256(raw_bytes).hexdigest(),
        'input_entries': len(entries), 'selected_entries': len(all_receipts),
        'chrome_resources': sum(1 for e in all_receipts if e['request']['url'].startswith('chrome://')),
        'server_timing_entries': sum(len(e['server_timing']) for e in all_receipts),
        'status_counts': {}, 'chrome_only': args.chrome_only,
        'source_type': 'HAR_EXPORT', 'raw_har_preserved': True,
        'record_policy': 'only allowlisted headers, query secrets redacted, no bodies saved',
    }
    for e in all_receipts:
        status = str(e['response']['status'])
        report['status_counts'][status] = report['status_counts'].get(status, 0) + 1
    summary = args.out / 'SUMMARY.json'
    summary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'OK | {len(all_receipts)} requests | {report["chrome_resources"]} chrome:// | '
          f'{report["server_timing_entries"]} server timings | {args.out.resolve()}')
    print(f'Input SHA-256: {report["input_sha256"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
