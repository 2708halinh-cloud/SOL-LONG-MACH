import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import workspace_bridge as w

class BridgeTests(unittest.TestCase):
    def test_read_without_edit(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d, 'xiaomi.json')
            raw = {'notes': [{'id': 7, 'title': 'note', 'checklist': [{'text':'send', 'checked':False}, {'text':'done','checked':True}]}]}
            src.write_text(json.dumps(raw))
            before = src.read_bytes()
            obs = w.observe_export('xiaomi', src)
            self.assertEqual(len(obs), 1)
            self.assertEqual([x['title'] for x in w.proposed_tasks(obs)], ['send'])
            self.assertEqual(src.read_bytes(), before)
    def test_default_no_remote_writes(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d,'keep.json'); out = Path(d, 'state.json')
            src.write_text('[{"id":"k1","checkItems":["item"]}]')
            with patch.object(w, 'api_request', side_effect=AssertionError('network')):
                self.assertEqual(w.run(['--keep-json',str(src),'--output',str(out)]),0)
            state=json.loads(out.read_text())
            self.assertEqual(state['proposals'],[])
            self.assertFalse(state['writes_enabled'])
    def test_readback_and_idempotent_ledger(self):
        requests=[]
        def fake_req(method, uri, token, body=None):
            requests.append(method)
            if method=='POST':
                self.assertIn('SOL-WORKSPACE:', body['notes'])
                return {'id':'provider-task-id'}
            return {'id':'provider-task-id','title':'step','notes':'SOL-WORKSPACE:'+w.digest(['xiaomi','1',0,'step'])}
        with tempfile.TemporaryDirectory() as d:
            src=Path(d,'xiaomi.json'); out=Path(d,'snapshot.json'); ledger=Path(d,'ledger.json')
            src.write_text('[{"id":"1","checklist":["step"]}]')
            args=['--xiaomi-json',str(src),'--output',str(out),'--map-checklists','--execute','--allow-send','--tasklist-id','some-list','--ledger',str(ledger)]
            with patch.dict('os.environ',{'SOL_GOOGLE_TASKS_ACCESS_TOKEN':'fake'}):
                w.run(args,request=fake_req)
                w.run(args,request=fake_req)
            self.assertEqual(requests,['POST','GET'])
            self.assertEqual(len(json.loads(ledger.read_text())),1)
    def test_no_overwrite_of_input(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d,'keep.json');src.write_text('[]')
            with self.assertRaises(SystemExit):
                w.run(['--keep-json',str(src),'--output',str(src)])

if __name__=='__main__':
    unittest.main()