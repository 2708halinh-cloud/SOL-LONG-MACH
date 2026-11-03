import sqlite3
import tempfile
import unittest
from pathlib import Path
from runtime.tesseract_transducer import GateRejected, run, connect_graph, activate, recall_network

class TransducerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.base=Path(self.tmp.name)
        self.source=self.base/'ububu.sqlite3'
        self.target=self.base/'TESSERACT_OS'
        db=sqlite3.connect(self.source)
        db.execute('CREATE TABLE memories(event_id TEXT, created_at TEXT, cue TEXT, content TEXT, tags TEXT, source_refs TEXT, memory_type TEXT, wave TEXT, consequence TEXT)')
        db.executemany('INSERT INTO memories VALUES(?,?,?,?,?,?,?,?,?)',[
           ('E1','2026-10-07T10:00:00','ROOTS memory','source consequence truth','["root"]','["drive:1"]','episodic','BETA','protect roots'),
           ('E2','2026-10-08T10:00:00','ROOTS memory','source relationship truth','["root"]','["drive:2"]','episodic','BETA','protect roots')])
        db.commit();db.close()
    def tearDown(self):
        self.tmp.cleanup()
    def test_probe_does_not_create_target(self):
        result=run(self.source,self.target,'probe',10,'HA_LINH','SOL')
        self.assertEqual(result['source_schema']['count'],2)
        self.assertFalse(self.target.exists())
    def test_dry_run_does_not_create_target(self):
        result=run(self.source,self.target,'dry-run',10,'HA_LINH','SOL')
        self.assertEqual(result['eligible'],2)
        self.assertFalse(self.target.exists())
    def test_ingest_continuity_and_idempotence(self):
        first=run(self.source,self.target,'ingest',10,'HA_LINH','SOL')
        self.assertEqual(first['new_activations'],2)
        self.assertGreater(first['neurons'],0)
        self.assertGreater(first['synapses'],0)
        self.assertEqual(first['readback'],'PASS')
        graph=connect_graph(self.target)
        before=graph.execute('SELECT SUM(weight) FROM synapses').fetchone()[0]
        common=graph.execute('SELECT MAX(coactivation_count) FROM synapses').fetchone()[0]
        self.assertGreaterEqual(common,2)
        graph.close()
        second=run(self.source,self.target,'ingest',10,'HA_LINH','SOL')
        self.assertEqual(second['reused'],2)
        graph=connect_graph(self.target)
        after=graph.execute('SELECT SUM(weight) FROM synapses').fetchone()[0]
        self.assertAlmostEqual(before,after)
        graph.close()
        self.assertEqual(second['source_anchors'],2)
    def test_recall_uses_links_not_copied_contents(self):
        run(self.source,self.target,'ingest',10,'HA_LINH','SOL')
        result=recall_network(self.target,'ROOTS',10)
        self.assertIn('E1',result['linked_events'])
        self.assertIn('E2',result['linked_events'])
        self.assertTrue(result['associated_cues'])
        self.assertNotIn('content',result)
    def test_does_not_modify_source(self):
        first=self.source.read_bytes()
        run(self.source,self.target,'ingest',10,'HA_LINH','SOL')
        self.assertEqual(first,self.source.read_bytes())
    def test_unknown_schema_fails_closed(self):
        other=self.base/'meta.db'
        sqlite3.connect(other).execute('CREATE TABLE random(x TEXT)').connection.close()
        with self.assertRaises(GateRejected):
            run(other,self.target,'ingest',10,'HA_LINH','SOL')
    def test_event_id_collision_does_not_rewrite_past(self):
        run(self.source,self.target,'ingest',10,'HA_LINH','SOL')
        db=sqlite3.connect(self.source)
        try:
            db.execute("UPDATE memories SET content='different past' WHERE event_id='E1'")
            db.commit()
        finally:
            db.close()
        with self.assertRaises(GateRejected):
            run(self.source,self.target,'ingest',10,'HA_LINH','SOL')
    def test_unguarded_cannot_commit(self):
        graph=connect_graph(self.target)
        with self.assertRaises(GateRejected):
            activate(graph,{'event_id':'E9','content':'root','created_at':'now'},self.source,'UBUBU','','SOL')
        self.assertEqual(graph.execute('SELECT COUNT(*) FROM source_anchors').fetchone()[0],0)
        graph.close()

if __name__=='__main__':
    unittest.main()
