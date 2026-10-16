"""ÂM–DƯƠNG: durable collaborative events, gated provider calls and HTTP readback."""
from __future__ import annotations
import importlib.util
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import request,error

HERE=Path(__file__).resolve().parents[1] / "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/sol_os/am_duong_platform"
sys.path.insert(0,str(HERE))
from core import AGENTS,Workrooms
from capabilities import analyze_text,configured,translate,image_details
from server import create_handler,run_capability,power_route

class PlatformTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.store=Workrooms(Path(temp.name)/"events.sqlite3")

    def test_human_event_persists_with_correct_identity_and_provenance(self):
        e=self.store.add("sol-main","Hà Linh","DUONG_PHAP_SU","source",
                         "Nhật ký trước đây","library://known")
        self.assertEqual(e["role"],"DUONG_PHAP_SU")
        other=Workrooms(self.store.db)
        old=other.events("sol-main")
        self.assertEqual(len(old),1)
        self.assertEqual(old[0]["source_ref"],"library://known")
        self.assertEqual(old[0]["id"],e["id"])

    def test_research_agent_search_uses_real_event_ids(self):
        direct=self.store.add("sol-main","Dương","DUONG_PHAP_SU","source",
                              "DANTE có sáu ID cũ; chưa chứng minh đã xóa")
        out=self.store.dispatch_offline("sol-main","researcher","DANTE sáu")
        hits=out["output"]["hits"]
        self.assertTrue(any(h["event_id"]==direct["id"] for h in hits))
        self.assertTrue(out["executed_locally"])
        self.assertFalse(out["external_provider_called"])

    def test_language_agent_returns_heuristic_not_neural_emotion(self):
        x=self.store.dispatch_offline("sol-main","analyst","Hà Linh rất vui")
        self.assertIn("HEURISTIC",x["output"]["mode"])
        self.assertFalse(x["output"]["entities_verified"])
        self.assertIsNone(x["output"]["emotion_subjectively_felt"])

    def test_power_router_returns_to_plugins_without_claiming_execution(self):
        result=power_route("trình duyệt browser")
        self.assertEqual(result["return_to"],"_Plugins")
        self.assertFalse(result["action_executed"])
        d=self.store.dispatch_offline("sol-main","router","trình duyệt browser",route_callback=power_route)
        self.assertEqual(d["output"]["return_to"],"_Plugins")

    def test_no_unapproved_external_api(self):
        with self.assertRaisesRegex(ValueError,"EXTERNAL_TRANSFER_REQUIRES_EXPLICIT_APPROVAL"):
            translate("xin chào","en",approved=False)
        with self.assertRaisesRegex(ValueError,"EXTERNAL_TRANSFER_REQUIRES_EXPLICIT_APPROVAL"):
            image_details("not_base64",approved=False)

    def test_external_missing_key_rejected_and_not_marked_connected(self):
        old=os.environ.pop("SOL_GOOGLE_CLOUD_API_KEY",None)
        try:
            self.assertIn("REQUIRES_ENV",configured()["translation_basic"]["state"])
            with self.assertRaisesRegex(ValueError,"CREDENTIAL_NOT_CONFIGURED"):
                translate("xin chào","en",approved=True)
        finally:
            if old is not None:os.environ["SOL_GOOGLE_CLOUD_API_KEY"]=old

    def test_internal_research_not_fabricated(self):
        result=run_capability("personal_research",{"query":"không có đoạn nào"},self.store)
        self.assertEqual(result["hits"],[])
        self.assertEqual(result["scope"],"LOCAL_SOURCED_ROOM_EVENTS_NOT_WEB")

    def test_no_arbitrary_remote_agent_impersonation(self):
        with self.assertRaisesRegex(ValueError,"EXTERNAL_OR_UNAVAILABLE_AGENT"):
            self.store.dispatch_offline("sol-main","video","nhận diện hành động video")

    def test_unknown_room_not_written_and_invalid_role_rejected(self):
        with self.assertRaisesRegex(ValueError,"ROOM_NOT_FOUND"):
            self.store.add("missing","human","DUONG_PHAP_SU","message","hello")
        with self.assertRaisesRegex(ValueError,"INVALID_ROLE_OR_EVENT_KIND"):
            self.store.add("sol-main","hacker","ADMIN","receipt","fake")

    def test_http_auth_403_and_agent_role_guard(self):
        token="loopback-testing-token"
        srv=ThreadingHTTPServer(("127.0.0.1",0),create_handler(self.store,token))
        thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
        self.addCleanup(lambda:(srv.shutdown(),srv.server_close(),thread.join(1)))
        base="http://127.0.0.1:"+str(srv.server_address[1])
        def call(path,payload=None,authorized=True):
            data=json.dumps(payload).encode() if payload is not None else None
            headers=({"X-SOL-TOKEN":token} if authorized else {})
            if payload is not None:headers["Content-Type"]="application/json"
            req=request.Request(base+path,data=data,headers=headers,
                                method="POST" if payload is not None else "GET")
            try:
                with request.urlopen(req,timeout=4) as response:
                    return response.status,json.loads(response.read())
            except error.HTTPError as exc:
                return exc.code,json.loads(exc.read())
        code,_=call("/api/state",authorized=False)
        self.assertEqual(code,401)
        code,data=call("/api/messages",{"kind":"receipt","content":"I verified receipt","role":"AM_PHAP_SU"})
        self.assertEqual(code,400)
        code,data=call("/api/messages",{"kind":"message","content":"Xin chào","role":"AM_PHAP_SU"})
        self.assertEqual(code,201)
        self.assertEqual(data["event"]["role"],"DUONG_PHAP_SU")
        code,state=call("/api/state")
        self.assertEqual(code,200)
        self.assertIn("sol",state["agents"])
        code,items=call("/api/events?room=sol-main")
        self.assertEqual(code,200)
        self.assertEqual(len(items["events"]),1)

if __name__=="__main__":
    unittest.main()
