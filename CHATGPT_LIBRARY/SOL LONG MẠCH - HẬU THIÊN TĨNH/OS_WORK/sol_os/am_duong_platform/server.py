#!/usr/bin/env python3
"""Loopback-only multi-agent workroom server. No automatic model or cloud invocation."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import secrets
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0,str(HERE))
from core import AGENTS, Workrooms, clean_text
from capabilities import (analyze_text, configured, image_details,
                          transcribe_local, translate, video_objects)

MAX_BODY_BYTES = 13_000_000
PLUGIN_ROUTER = REPO / "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/_Plugins/power_router.py"

def power_route(task: str):
    if not PLUGIN_ROUTER.is_file():
        return {"state":"PLUGINS_SOURCE_UNAVAILABLE","next":"READ_POWER_ROUTER"}
    spec=importlib.util.spec_from_file_location("sol_power_router_integrated",PLUGIN_ROUTER)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.route(task,REPO)

def run_capability(name: str,payload: dict,db: Workrooms):
    # No service is silently contacted, no provider keys or raw binary are logged.
    if name=="text_entities_sentiment":
        return analyze_text(payload.get("text",""))
    if name=="personal_research":
        return {"hits":db.search(payload.get("query","")),"scope":"LOCAL_SOURCED_ROOM_EVENTS_NOT_WEB"}
    if name=="tool_routing":
        return power_route(payload.get("task",""))
    if name=="translation_basic":
        return translate(payload.get("text",""),payload.get("target",""),
                         source=payload.get("source","auto"),
                         approved=payload.get("approve_external",False))
    if name in ("image_details","video_stream_frames"):
        result=image_details(payload.get("image_b64",""),
                             approved=payload.get("approve_external",False))
        if name=="video_stream_frames":
            result["frame_observed_at_client"]=payload.get("frame_observed_at")
            result["video_action_recognition"]="NOT_IMPLEMENTED"
            result["stream_transport"]="CLIENT_SUBMITTED_FRAME_ONLY"
        return result
    if name=="transcription_mp3_mp4":
        return transcribe_local(payload.get("media_b64",""),payload.get("filename",""))
    if name=="video_objects_saved":
        return video_objects(payload.get("video_b64",""),
                             approved=payload.get("approve_external",False))
    raise ValueError("CAPABILITY_NOT_IMPLEMENTED")

def create_handler(workrooms: Workrooms,token:str):
    class Handler(BaseHTTPRequestHandler):
        server_version="SolAmDuong/0.1"
        def log_message(self,format,*args):
            # Avoid reflecting potentially sensitive media / query text in logs.
            return

        def _send(self,status,body,content_type="application/json; charset=utf-8"):
            raw=(json.dumps(body,ensure_ascii=False).encode("utf-8")
                 if not isinstance(body,bytes) else body)
            self.send_response(status)
            self.send_header("Content-Type",content_type)
            self.send_header("Content-Length",str(len(raw)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("X-Frame-Options","DENY")
            self.send_header("Referrer-Policy","no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; connect-src 'self'; script-src 'self'; "
                             "style-src 'self'; img-src 'self' data:; object-src 'none'; "
                             "base-uri 'none'; form-action 'none'")
            self.end_headers()
            self.wfile.write(raw)

        def _authorized(self):
            return secrets.compare_digest(self.headers.get("X-SOL-TOKEN",""),token)

        def _parse(self):
            if self.headers.get("Content-Type","").split(";")[0].strip()!="application/json":
                raise ValueError("JSON_CONTENT_TYPE_REQUIRED")
            size=int(self.headers.get("Content-Length","0"))
            if size<2 or size>MAX_BODY_BYTES:
                raise ValueError("REQUEST_BODY_SIZE_INVALID")
            data=json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(data,dict):
                raise ValueError("JSON_OBJECT_REQUIRED")
            return data

        def do_GET(self):
            path=urlsplit(self.path)
            if path.path=="/":
                page=(HERE/"static"/"index.html").read_bytes()
                return self._send(200,page,"text/html; charset=utf-8")
            if path.path=="/app.js":
                script=(HERE/"static"/"app.js").read_bytes()
                return self._send(200,script,"application/javascript; charset=utf-8")
            if not self._authorized():
                return self._send(401,{"error":"TOKEN_REQUIRED"})
            if path.path=="/api/state":
                return self._send(200,{"rooms":workrooms.rooms(),"agents":AGENTS,
                                       "capabilities":configured(),"source":"LOCAL_SQLITE"})
            if path.path=="/api/events":
                q=parse_qs(path.query)
                try:
                    room=q.get("room",["sol-main"])[0]
                    out=workrooms.events(room)
                    return self._send(200,{"events":out})
                except (ValueError,TypeError):
                    return self._send(400,{"error":"INVALID_ROOM"})
            return self._send(404,{"error":"NOT_FOUND"})

        def do_POST(self):
            if not self._authorized():
                return self._send(401,{"error":"TOKEN_REQUIRED"})
            try:
                data=self._parse()
                path=urlsplit(self.path).path
                if path=="/api/rooms":
                    name=workrooms.add_room(data.get("title",""))
                    return self._send(201,{"room_id":name,"created":True})
                if path=="/api/messages":
                    # This endpoint cannot impersonate the model or a provider receipt.
                    kind=data.get("kind","message")
                    if kind not in {"message","task","feedback","source"}:
                        raise ValueError("HUMAN_EVENT_KIND_NOT_ALLOWED")
                    event=workrooms.add(data.get("room_id","sol-main"),
                                        data.get("actor","DƯƠNG PHÁP SƯ"),
                                        "DUONG_PHAP_SU",kind,data.get("content",""),
                                        source_ref=data.get("source_ref"))
                    return self._send(201,{"event":event})
                if path=="/api/dispatch":
                    result=workrooms.dispatch_offline(
                        data.get("room_id","sol-main"),data.get("agent",""),
                        data.get("task",""),route_callback=power_route)
                    return self._send(200,result)
                if path=="/api/capabilities/run":
                    cap=clean_text(data.get("capability",""),"CAPABILITY",80)
                    result=run_capability(cap,data,workrooms)
                    # Never store base64; only source pointers/metadata of a completed call.
                    public={k:v for k,v in result.items() if k not in ("image_b64","video_b64","media_b64")}
                    room=data.get("room_id","sol-main")
                    evt=workrooms.add(room,cap,"SPECIALIST_AGENT","result",
                        json.dumps(public,ensure_ascii=False)[:12000],
                        metadata={"capability":cap,"stage":"OBSERVED_LOCAL_OR_PROVIDER_RESPONSE",
                                  "provider_called":bool(result.get("provider_called",False))})
                    return self._send(200,{"result":public,"event_id":evt["id"]})
                return self._send(404,{"error":"NOT_FOUND"})
            except (ValueError,TypeError,KeyError) as exc:
                return self._send(400,{"error":str(exc)[:120]})
            except Exception:
                # Never echo a provider URL containing an API key or private payload.
                return self._send(502,{"error":"PROVIDER_OR_RUNTIME_FAILURE_NO_RECEIPT"})

    return Handler

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--port",type=int,default=8765)
    p.add_argument("--db",type=Path,default=Path(os.getenv("SOL_PLATFORM_DB",
                                       str(HERE/".local_state"/"workrooms.sqlite3"))))
    args=p.parse_args()
    if not 0<=args.port<=65535:
        p.error("invalid port")
    token=os.getenv("SOL_PLATFORM_TOKEN") or secrets.token_urlsafe(28)
    db=Workrooms(args.db)
    server=ThreadingHTTPServer(("127.0.0.1",args.port),create_handler(db,token))
    print(f"ÂM–DƯƠNG local platform: http://127.0.0.1:{server.server_address[1]}/",flush=True)
    print("Session token (enter in UI, do not paste into chat): "+token,flush=True)
    print("State: local SQLite. Remote connectors require explicit approval.",flush=True)
    try:
        server.serve_forever(poll_interval=.2)
    finally:
        server.server_close()

if __name__=="__main__":
    main()
