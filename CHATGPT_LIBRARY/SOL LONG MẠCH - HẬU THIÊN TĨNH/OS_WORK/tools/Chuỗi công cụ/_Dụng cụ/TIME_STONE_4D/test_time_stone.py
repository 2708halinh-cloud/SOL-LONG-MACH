import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
import time_stone as t

NOW=dt.datetime(2026,10,17,1,30,tzinfo=dt.timezone(dt.timedelta(hours=7)))

def event(key,stamp='STAMP_LIVE',at='2026-10-16T20:00:00+07:00',wave='DELTA'):
    return {'event_id':key,'stamp_class':stamp,'observed_at':at,'event_time':at,
            'source_ref':'test://source', 'wave':wave}

class TestStone(unittest.TestCase):
    def test_live_ages(self):
        status,step=t.resolve_status(event('A'),NOW)
        self.assertEqual(status,'STAMP_OLD')
        self.assertIn('STALE',step)
    def test_recent_live(self):
        self.assertEqual(t.resolve_status(event('A',at='2026-10-17T01:29:30+07:00'),NOW)[0], 'STAMP_LIVE_AT_OBSERVATION')
    def test_future_beta_never_promotes(self):
        self.assertEqual(t.resolve_status(event('A','STAMP_BETA','2026-10-16T00:00:00+07:00'),NOW)[0], 'STAMP_BETA_DUE_UNVERIFIED')
    def test_old_persists(self):
        self.assertEqual(t.resolve_status(event('A','STAMP_OLD'),NOW)[0], 'STAMP_OLD')
    def test_future_live_timelock(self):
        self.assertEqual(t.resolve_status(event('A',at='2026-10-19T00:00:00+07:00'),NOW)[0], 'TIME_LOCK_FUTURE_OBSERVATION')
    def test_naive_time_rejected(self):
        with self.assertRaisesRegex(ValueError,'TIME_ZONE_REQUIRED'):
            t.resolve_status(event('A',at='2026-10-16T20:00:00'),NOW)
    def test_raw_log_immutable_projection_and_transitions(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'raw.jsonl';s=Path(d)/'state'
            raw=json.dumps(event('one',at='2026-10-17T01:29:50+07:00'),ensure_ascii=False)+'\n'
            p.write_text(raw,encoding='utf-8')
            a=t.sync(p,s,NOW,60,force_active=True)
            b=t.sync(p,s,NOW+dt.timedelta(minutes=3),60,force_active=True)
            self.assertEqual(p.read_text(encoding='utf-8'),raw)
            self.assertTrue(a['active']);self.assertEqual(b['old_live_reclassified'],1)
            self.assertEqual(b['events'][0]['current_stamp'],'STAMP_OLD')
            tr=(s/'TRANSITIONS.jsonl').read_text(encoding='utf-8')
            self.assertEqual(len(tr.splitlines()),1)
            self.assertEqual(json.loads(tr)['from'],'STAMP_LIVE_AT_OBSERVATION')
    def test_backward_time_lock_avoids_demote_or_promote(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'events.jsonl';s=Path(d)/'state'
            p.write_text(json.dumps(event('one'))+'\n')
            t.sync(p,s,NOW)
            a=t.sync(p,s,NOW-dt.timedelta(hours=1))
            self.assertEqual(a['state'],'TIME_LOCK_CLOCK_BACKWARD')
            self.assertEqual(json.loads((s/'CURRENT.json').read_text())['checked_at_utc'],t.iso(NOW))
    def test_duplicate_conflict_quarantined_no_deletion(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'events.jsonl';s=Path(d)/'state'
            p.write_text(json.dumps(event('same'))+'\n'+json.dumps(event('same',at='2026-10-15T00:00:00+07:00'))+'\n')
            z=t.sync(p,s,NOW)
            self.assertEqual(len(z['events']),1)
            self.assertIn('CONFLICTING_EVENT_ID',z['rejected'][0]['reason'])
            self.assertEqual(len(p.read_text().splitlines()),2)
    def test_record_validates_source_and_wave(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'e.jsonl'
            with self.assertRaises(ValueError):t.command_record(p,{'event_id':'x','stamp_class':'STAMP_LIVE','wave':'BETA','observed_at':'2026-10-17T01:00:00+07:00'})
            t.command_record(p,event('ok'))
            with self.assertRaisesRegex(ValueError,'ALREADY_EXISTS'):t.command_record(p,event('ok'))
    def test_wave_paths_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'wave.log';f.write_text('w')
            data=t.inspect_wave_carriers([f,Path(d)/'missing'])
            self.assertTrue(data[0]['found']);self.assertFalse(data[1]['found'])
    def test_missing_event_file_does_not_fake_raw(self):
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d)/'nonexistent.jsonl'
            v=t.sync(raw,Path(d)/'state',NOW)
            self.assertFalse(raw.exists());self.assertIsNone(v['input_sha256'])

if __name__=='__main__': unittest.main()
