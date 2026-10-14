#!/usr/bin/env python3
"""TRÌNH DUYỆT local-only device inspector for user-authorized SOL host.
This is a local operator tool, not a ChatGPT cloud/remote proxy.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
import webbrowser

DEFAULT_URL = "http://127.0.0.1:8765/api/devices"

class DenyRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Redirect refused: URL outside exact authorized target")

def read_config():
    cfg_path = Path(__file__).with_name("browser_config.json")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    urls = cfg.get("allowed_urls")
    if urls != [DEFAULT_URL] or cfg.get("method") != "GET":
        raise ValueError("Unexpected URL/method in local browser config")
    parsed = urlsplit(DEFAULT_URL)
    if (parsed.scheme, parsed.hostname, parsed.port, parsed.path) != ("http", "127.0.0.1", 8765, "/api/devices"):
        raise ValueError("URL validation failed")
    return cfg

def probe(cfg):
    req = Request(DEFAULT_URL, headers={"Accept": "application/json"}, method="GET")
    with build_opener(DenyRedirect()).open(req, timeout=4) as resp:
        if resp.status != 200:
            raise RuntimeError("Unexpected HTTP status: %s" % resp.status)
        if int(resp.headers.get("Content-Length", "0") or 0) > 2_000_000:
            raise RuntimeError("Response exceeds size bound")
        raw = resp.read(2_000_001)
        if len(raw) > 2_000_000:
            raise RuntimeError("Response exceeds size bound")
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("Response must be JSON object")
    if obj.get("schema") != cfg["expected_response_schema"]:
        raise ValueError("Unexpected schema: %r" % obj.get("schema"))
    if obj.get("host") != cfg["target_host"]:
        raise ValueError("Unexpected host: %r" % obj.get("host"))
    modules = obj.get("modules")
    if not isinstance(modules, dict):
        raise ValueError("Missing modules")
    print(json.dumps({
        "readback": "LIVE_LOCAL_GET_OK",
        "url": DEFAULT_URL,
        "schema": obj["schema"],
        "host": obj["host"],
        "timestamp": obj.get("timestamp"),
        "modules": sorted(modules),
        "expected_modules_present": [x for x in cfg["expected_modules"] if x in modules]
    }, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Local browser connector for SOL device topology")
    parser.add_argument("mode", choices=("probe", "open", "show-config"), nargs="?", default="probe")
    args = parser.parse_args()
    cfg = read_config()
    if args.mode == "probe":
        probe(cfg)
    elif args.mode == "open":
        if not webbrowser.open_new_tab(DEFAULT_URL):
            raise SystemExit("Unable to open default browser on local host")
        print("Requested local browser tab: " + DEFAULT_URL)
    else:
        print(json.dumps(cfg, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
