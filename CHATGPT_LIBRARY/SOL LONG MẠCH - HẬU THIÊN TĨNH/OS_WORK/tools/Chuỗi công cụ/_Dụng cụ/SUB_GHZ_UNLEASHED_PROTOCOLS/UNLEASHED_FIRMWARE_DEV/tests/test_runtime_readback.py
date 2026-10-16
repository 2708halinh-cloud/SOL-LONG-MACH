"""Actual offline API, streaming RPC and gitlink source checks; no network provider."""
import http.client
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from unleashed_rpc_transport import RpcFrameStream,encode_varint,decode_frames
from unleashed_sensorimotor import append
from unleashed_sensorimotor_api import create_server,checkpoint,query_events
from unleashed_submodule_sync import inspect

class ApiAndRpc(unittest.TestCase):
    def test_protobuf_fragmentation_and_offsets(self):
        frames=[b'abc',b'x'*400,b'']
        b=b''.join(encode_varint(len(f))+f for f in frames)
        s=RpcFrameStream();out=[]
        for octet in b:out+=s.next_chunk(bytes([octet]))
        out+=s.next_chunk(b'',final=True)
        self.assertEqual([x['protobuf_length'] for x in out],[3,400,0])
        self.assertEqual([x['offset'] for x in out],[0,4,406])
        self.assertEqual(out,decode_frames(b))
    def test_truncated_frame_and_varint(self):
        for blob in [b'\x82\x01a',b'\x80',b'\xff\xff\xff\xff\xff']:
            parser=RpcFrameStream()
            with self.assertRaises(ValueError):parser.next_chunk(blob,final=True)
    def test_readback_api_real_http(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            e=append(root,'input','SOURCE_INSPECTED',{'status':'VERIFIED'},'SOURCE_READBACK')
            with create_server(root,0) as server:
                t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
                try:
                    conn=http.client.HTTPConnection('127.0.0.1',server.server_address[1],timeout=3)
                    conn.request('GET','/v1/readback');r=conn.getresponse();info=json.loads(r.read())
                    self.assertEqual(r.status,200)
                    self.assertEqual(info['last_hash'],e['hash'])
                    self.assertEqual(info['next'],'RESUME_FROM_LAST_HASH')
                    conn.request('GET','/v1/events?after=0&limit=2');r=conn.getresponse();out=json.loads(r.read())
                    self.assertEqual(out['count'],1)
                    self.assertNotIn('details',out['events'][0])
                    conn.request('POST','/v1/readback');r=conn.getresponse();r.read()
                    self.assertEqual(r.status,405)
                    conn.close()
                finally:server.shutdown();t.join(3)
    def test_tampered_journal_refuses_api_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            append(root,'chrono','TEST_SIMULATION',{'status':'TEST_ONLY'})
            (root/'5_CHRONO_CONTINUOUS.log').write_text('broken\n')
            self.assertEqual(checkpoint(root)['status'],'ERROR')
    def test_submodule_zip_root_is_not_git_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'.gitmodules').write_text('[submodule "lib/nanopb"]\n path = lib/nanopb\n url = https://github.com/nanopb/nanopb.git\n')
            state=inspect(root)
            self.assertEqual(state['error'],'ARCHIVE_NOT_CHECKOUT')
            self.assertFalse(state['ready_for_recursive_build'])

if __name__=='__main__':unittest.main()
