"""Run from this directory: python -m unittest -v test_agent_capability_lifecycle.py"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import sqlite3
import tempfile
import unittest
from agent_capability_lifecycle import (CapabilityLedger, bootstrap, sha, rehydrate_checkpoint,
    checked_artifact, verify_core_journal)
from agent_core_runtime import CoreJournal, EphemeralBlackboard

ROOT = Path(__file__).resolve().parent
T0 = datetime(2026, 10, 19, tzinfo=timezone.utc)

class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.path = self.dir/'ledger.db'
        self.ledger = CapabilityLedger(self.path)
        self.cap = 'capability-self-maintenance'

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def test_bootstrap_fresh_ram_with_trusted_artifacts(self):
        b = bootstrap(ROOT/'capability_manifest.json', self.dir/'boot.db', session_id='fresh')
        self.assertEqual(b.blackboard['session_id'], 'fresh')
        self.assertEqual(b.blackboard['stage'], 'INPUT')
        self.assertEqual(b.capabilities[self.cap]['status']['state'], 'UNVERIFIED')
        self.assertFalse(b.provider_execution_claimed)

    def test_cold_reset_restores_snapshot_without_raw_payload(self):
        core = CoreJournal(self.dir/'core.db')
        core.start('r', 'goal')
        b = EphemeralBlackboard(session_id='before-reset', turn_id=4)
        b.raw_tool_payload = {'credential':'DO_NOT_STORE'}
        b.scratchpad = {'danger':'secret'}
        core.checkpoint('r', 0, b)
        core.close()
        boot = bootstrap(ROOT/'capability_manifest.json', self.dir/'boot.db', session_id='after-reset',
                         core_db_path=self.dir/'core.db', run_id='r')
        self.assertEqual(boot.blackboard['session_id'], 'after-reset')
        self.assertEqual(boot.blackboard['turn_id'], 4)
        self.assertIsNone(boot.blackboard['raw_tool_payload'])
        self.assertEqual(boot.blackboard['scratchpad'], {})
        self.assertFalse(boot.blackboard['readback_passed'])
        self.assertIn('CHECKPOINT_HASH_MATCH',boot.checkpoint_source)

    def test_bad_manifest_hash_rejected(self):
        m = json.loads((ROOT/'capability_manifest.json').read_text())
        m['artifacts'][0]['sha256']='0'*64
        target = self.dir/'capability_manifest.json'
        # Only tampered digest, artifacts are symlink-free copied files.
        for entry in m['artifacts']:
            (self.dir/entry['path']).write_bytes((ROOT/entry['path']).read_bytes())
        target.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError,'ARTIFACT_INTEGRITY_MISMATCH'):
            bootstrap(target,self.dir/'other.db',session_id='x')

    def test_symlink_path_traversal_rejected(self):
        with self.assertRaisesRegex(ValueError,'OUTSIDE_ROOT'):
            checked_artifact(ROOT,'../credentials.txt')

    def test_write_readback_and_chain(self):
        source = self.dir/'s.txt'; target = self.dir/'t.txt'
        source.write_bytes(b'matched\x00data'); target.write_bytes(b'matched\x00data')
        receipt = self.ledger.record_local_readback(self.cap, source, target, sha(source.read_bytes()),at=T0)
        self.assertTrue(self.ledger.verify())
        self.assertEqual(self.ledger.status(self.cap,at=T0)['state'],'VERIFIED_LOCAL')
        self.assertTrue(receipt['event_hash'])
        target.write_bytes(b'modified')
        with self.assertRaisesRegex(ValueError,'READBACK_BYTE_HASH_MISMATCH'):
            self.ledger.record_local_readback(self.cap,source,target,sha(source.read_bytes()),at=T0)

    def test_external_reference_never_counts_as_provider_verification(self):
        self.ledger.record_external_reference(self.cap,'github:receipt','drive:readback',at=T0)
        self.assertEqual(self.ledger.status(self.cap,at=T0)['state'],'UNVERIFIED')

    def test_time_decay_triggers_due_without_fabricating_failure(self):
        s=self.dir/'a';s.write_bytes(b'1')
        self.ledger.record_local_readback(self.cap,s,s,sha(b'1'),at=T0)
        stale=self.ledger.status(self.cap,at=T0+timedelta(hours=600),half_life_hours=100,threshold=.2)
        self.assertTrue(stale['calibration_due'])
        self.assertEqual(stale['state'],'DEGRADED')

    def test_auto_calibration_persists_local_evidence_and_recovers_after_reset(self):
        self.ledger.append(self.cap,'CALIBRATION_FAILED',{'error_class':'RuntimeError'},at=T0)
        self.assertEqual(self.ledger.calibrate(self.cap,lambda:{'passed':True,'scenario':'local'},at=T0)['state'],
                         'CALIBRATED_SIMULATION_ONLY')
        self.ledger.close()
        self.ledger = CapabilityLedger(self.path)
        self.assertEqual(self.ledger.status(self.cap,at=T0)['state'],'CALIBRATED_SIMULATION_ONLY')
        self.assertTrue(self.ledger.verify())

    def test_calibration_failure_is_degraded(self):
        out=self.ledger.calibrate(self.cap,lambda: (_ for _ in ()).throw(RuntimeError('secret not logged')),at=T0)
        self.assertEqual(out['state'],'DEGRADED')
        self.assertTrue(self.ledger.verify())

    def test_sqlite_triggers_append_only(self):
        self.ledger.append(self.cap,'CALIBRATION_FAILED',{'error_class':'X'},at=T0)
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute('DELETE FROM capability_events')

    def test_chain_corruption_detected(self):
        self.ledger.append(self.cap,'CALIBRATION_FAILED',{'error_class':'X'},at=T0)
        self.ledger.db.execute('DROP TRIGGER capability_events_no_update')
        self.ledger.db.execute("UPDATE capability_events SET payload_json='{}'")
        self.assertFalse(self.ledger.verify())
        self.assertEqual(self.ledger.status(self.cap,at=T0)['state'],'LEDGER_TAMPERED')

    def test_corrupt_core_chain_prevents_rehydration(self):
        core=CoreJournal(self.dir/'core.db')
        core.start('r','goal')
        core.checkpoint('r',0,EphemeralBlackboard(session_id='x',turn_id=2))
        core.append('r','test','READBACK',{'ok':True})
        core.close()
        db=sqlite3.connect(self.dir/'core.db')
        db.execute('DROP TRIGGER journal_no_update')
        db.execute("UPDATE journal_entries SET payload_json='{}'")
        db.commit();db.close()
        with self.assertRaisesRegex(ValueError,'CORE_JOURNAL_CHAIN_INVALID'):
            rehydrate_checkpoint(self.dir/'core.db','r','s2')

if __name__=='__main__':
    unittest.main()