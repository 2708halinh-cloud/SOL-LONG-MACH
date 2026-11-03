import json, tempfile, unittest
from pathlib import Path
from runtime.tesseract_snn.blackboard import ActiveBlackboard, VersionConflict
from runtime.tesseract_snn.journal import AppendOnlyJournal
from runtime.tesseract_snn.resource_guard import DiskGuard, DiskSample, GIB

class BlackboardTests(unittest.TestCase):
    def test_compare_and_set_versions_and_copies_payload(self):
        b=ActiveBlackboard(); source={"nested":[1]}
        first=b.compare_and_set("REG_00",0,source,"worker-a","test://source","state-1")
        source["nested"].append(2)
        self.assertEqual(first.version,1)
        self.assertEqual(b.read("REG_00").payload,{"nested":[1]})
        with self.assertRaises(VersionConflict):
            b.compare_and_set("REG_00",0,{}, "worker-b","test://source","state-2")

class JournalTests(unittest.TestCase):
    def test_hash_chain_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"journal.jsonl"; j=AppendOnlyJournal(path)
            j.append({"action":"WRITE","target":"REG_01"})
            j.append({"action":"READBACK","result":"MATCH"})
            self.assertTrue(j.verify())
            rows=path.read_text().splitlines()
            altered=json.loads(rows[0]); altered["event"]["target"]="OTHER"
            rows[0]=json.dumps(altered)
            path.write_text("\n".join(rows)+"\n")
            self.assertFalse(j.verify())

class DiskGuardTests(unittest.TestCase):
    def test_warn_trip_unknown_and_recovery_hysteresis(self):
        g=DiskGuard(absolute_free_floor=5*GIB)
        self.assertEqual(g.evaluate(DiskSample(100,15)).mode,"WARNING")
        self.assertEqual(g.evaluate(DiskSample(100,10)).mode,"DEGRADED")
        self.assertEqual(g.evaluate(DiskSample(100,20,False)).mode,"DEGRADED")
        self.assertEqual(g.evaluate(DiskSample(100,20)).mode,"DEGRADED")
        self.assertEqual(g.evaluate(DiskSample(100,20)).mode,"NORMAL")

if __name__ == "__main__": unittest.main()
