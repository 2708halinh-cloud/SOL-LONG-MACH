#!/usr/bin/env python3
"""Loopback-only, read-only API over SENSORIMOTOR's five durable journal files.

Provides checkpoint/readback for an interrupted agent, not a model's neural state.
No mutation endpoint; no filesystem traversal, no raw hardware/RPC payload endpoint.
"""
from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from unleashed_sensorimotor import verify,read_journal,CHANNELS

MAX_EVENTS=100

def checkpoint(root:Path)->dict:
    state=verify(root)
    if not state.get('valid'):
        return {'schema':'SOL_SENSORIMOTOR_READBACK/1.0','status':'ERROR','journal':state,'next':'REPAIR_CANONICAL_OR_MIRRORS'}
    return {'schema':'SOL_SENSORIMOTOR_READBACK/1.0','status':'VERIFIED',
            'event_count':state['events'],'last_hash':state['last_hash'],
            'five_logs':list(CHANNELS.values()),'next':'RESUME_FROM_LAST_HASH',
            'hardware_readback':False}

def query_events(root:Path,after:int=0,limit:int=20)->dict:
    state=checkpoint(root)
    if state['status']!='VERIFIED':return state
    if after<0 or limit<1 or limit>MAX_EVENTS:raise ValueError('invalid pagination')
    entries=[e for e in read_journal(root) if e['sequence']>after][:limit]
    # Deliberately only a small provenance allowlist, not raw metadata.
    selected=[{k:e[k] for k in ('sequence','timestamp_utc','kind','channel','observation','hash','previous_hash')}
              for e in entries]
    return {'schema':'SOL_SENSORIMOTOR_EVENTS/1.0','events':selected,'count':len(selected),
            'tip_sequence':state['event_count'],'tip_hash':state['last_hash'],
            'next_after':entries[-1]['sequence'] if entries else after}

def handler_factory(root:Path):
    class Handler(BaseHTTPRequestHandler):
        def _respond(self,code:int,body:dict):
            data=json.dumps(body,ensure_ascii=False,sort_keys=True).encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers()
            self.wfile.write(data)
        def do_GET(self):
            u=urlsplit(self.path)
            try:
                if u.path in ('/v1/readback','/health') and not u.query:
                    data=checkpoint(root)
                elif u.path=='/v1/events':
                    qs=parse_qs(u.query,strict_parsing=True)
                    if set(qs)-{'after','limit'}:raise ValueError('unknown query parameter')
                    data=query_events(root,int(qs.get('after',['0'])[0]),int(qs.get('limit',['20'])[0]))
                else:
                    self._respond(404,{'error':'NOT_FOUND'});return
                self._respond(200 if data.get('status')!='ERROR' else 409,data)
            except (ValueError,KeyError) as exc:
                self._respond(400,{'error':'INVALID_QUERY','reason':str(exc)})
        def do_POST(self):self._respond(405,{'error':'READ_ONLY_API'})
        def do_PUT(self):self._respond(405,{'error':'READ_ONLY_API'})
        def do_DELETE(self):self._respond(405,{'error':'READ_ONLY_API'})
        def log_message(self,format,*args):pass  # No event metadata in HTTP logs
    return Handler

def create_server(root:Path,port:int=8767)->ThreadingHTTPServer:
    if not 0<=port<=65535:raise ValueError('invalid port')
    return ThreadingHTTPServer(('127.0.0.1',port),handler_factory(root))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--logs-dir',type=Path,required=True)
    p.add_argument('--port',type=int,default=8767)
    p.add_argument('--readback-only',action='store_true')
    a=p.parse_args()
    if a.readback_only:print(json.dumps(checkpoint(a.logs_dir),ensure_ascii=False,indent=2));return
    server=create_server(a.logs_dir,a.port)
    print(json.dumps({'status':'LISTENING','bind':'127.0.0.1','port':server.server_address[1]},ensure_ascii=False),flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
