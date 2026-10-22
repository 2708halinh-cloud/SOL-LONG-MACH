#!/usr/bin/env python3
"""Read-only E-R web API, scoped to an independently materialized SQLite file."""
from __future__ import annotations
import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
FRONT=BASE/"frontend"

def observed_state(db: Path):
    if not db.is_file():
        return None
    try:
        uri=db.resolve().as_uri()+"?mode=ro"
        with sqlite3.connect(uri,uri=True,timeout=1) as con:
            con.execute("PRAGMA query_only=ON")
            names={x[0] for x in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {"entities","relations","sources"}.issubset(names):
                return None
            return {"schema":"TESSERACT_THIT_THO_ER_STATE/1",
                    "entities":con.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
                    "relations":con.execute("SELECT COUNT(*) FROM relations").fetchone()[0],
                    "sources":con.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
                    "raw_private_data_included":False}
    except (sqlite3.Error,OSError):
        return None

def handler(db: Path):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_args):
            pass
        def send_data(self,code,body,typ):
            self.send_response(code)
            self.send_header("Content-Type",typ)
            self.send_header("Content-Length",str(len(body)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            path=self.path.split("?",1)[0]
            if path=="/":
                self.send_data(200,(FRONT/"index.html").read_bytes(),"text/html; charset=utf-8")
            elif path=="/api/health":
                self.send_data(200,b'{"status":"WEB_PROCESS_ALIVE_NOT_OS_BOOT"}',"application/json")
            elif path=="/api/state":
                state=observed_state(db)
                if state is None:
                    self.send_data(503,b'{"status":"ER_SOURCE_UNAVAILABLE"}',"application/json")
                else:
                    self.send_data(200,json.dumps(state).encode(),"application/json")
            else:
                self.send_data(404,b'{"status":"NOT_FOUND"}',"application/json")
    return Handler

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",type=Path,required=True)
    p.add_argument("--host",default="127.0.0.1")
    p.add_argument("--port",type=int,default=8765)
    p.add_argument("--container",action="store_true")
    a=p.parse_args()
    if a.host not in ("127.0.0.1","localhost") and not (a.container and a.host=="0.0.0.0"):
        raise SystemExit("HOST_LOOPBACK_ONLY_UNLESS_EXPLICIT_CONTAINER")
    ThreadingHTTPServer((a.host,a.port),handler(a.db)).serve_forever()

if __name__=="__main__":
    main()
