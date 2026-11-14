"""Run: python -m unittest -v test_agent_core_runtime.py"""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from agent_core_runtime import (CoreJournal, Hypothesis, Direction, BaguaMatrix,
                                EphemeralBlackboard, ToolRouter, precommit_gate,
                                stable_tool_id, semver_key)


def alpha(path: str) -> dict:
    return {"path": path, "value": "ok"}


def beta(path: str) -> dict:
    return {"path": path, "value": "new"}


def hollow(path: str) -> dict:
    return {}


def bad(path: str) -> dict:
    raise RuntimeError('unreachable')

SCHEMA = {"type": "object", "properties": {"path": {"type": "string"}},
          "required": ["path"], "additionalProperties": False}


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.j = CoreJournal(Path(self.temp.name) / "test.db")
        self.j.start('r1', 'One global goal')
        self.j.add_step('r1', 's1', 1, 'Retrieve')
        self.j.add_step('r1', 's2', 2, 'Validate')
        self.b = EphemeralBlackboard(session_id='test',turn_id=1)
        self.matrix = BaguaMatrix(**{
            k: Direction(observation='observed' if k == 'evidence' else 'open',
                         source_refs=['source:1'] if k == 'evidence' else [])
            for k in ('evidence','causality','contrarian','architecture','ram','risks','ground_reality','global_goal')
        })
    def tearDown(self):
        self.j.close()
        self.temp.cleanup()
    def divergences(self):
        return [Hypothesis(id=f'h{i}',description='hypothesis',divergent_angle='different',
                           risk_assessment='risk',feasibility_score=.6,evidence_refs=['source:1'])
                for i in range(3)]
    def live(self, caps=('file:read',), permission='granted', callable=True):
        return {'capabilities':list(caps),'permission':permission,'callable':callable}
    def test_divergent_then_converge(self):
        self.assertEqual(self.b.converge('h1')[1],'BAGUA_NOT_READY')
        self.b.open_divergence(self.divergences()[:2],self.matrix)
        self.assertEqual(self.b.converge('h1')[1],'DIVERGENT_POOL_NEEDS_3_DISTINCT_HYPOTHESES')
        self.b.open_divergence(self.divergences(),self.matrix)
        self.assertTrue(self.b.converge('h1')[0])
    def test_missing_evidence_blocks(self):
        hs=self.divergences(); hs[0].evidence_refs=[]
        self.b.open_divergence(hs,self.matrix)
        self.assertEqual(self.b.converge('h0')[1],'HYPOTHESIS_REQUIRES_SOURCE_REF')
    def test_hash_stable_per_source(self):
        self.assertEqual(stable_tool_id(alpha,SCHEMA),stable_tool_id(alpha,SCHEMA))
        self.assertNotEqual(stable_tool_id(alpha,SCHEMA),stable_tool_id(beta,SCHEMA))
    def test_semver_higher_and_release_precedence(self):
        self.assertGreater(semver_key('2.0.0'),semver_key('1.99.9'))
        self.assertGreater(semver_key('2.0.0'),semver_key('2.0.0-beta.1'))
    def test_fallback_older_less_capabilities(self):
        r=ToolRouter()
        r.register_tool(group_key='files',capabilities=['file:read'],version='1.0.0',argument_schema=SCHEMA)(alpha)
        r.register_tool(group_key='files',capabilities=['file:read','file:write'],version='2.0.0',argument_schema=SCHEMA)(beta)
        out=r.execute('files','file:read',{'path':'sample'},self.live())
        self.assertEqual(out['version'],'1.0.0')
        self.assertEqual(out['payload']['value'],'ok')
    def test_current_capabilities_and_version(self):
        r=ToolRouter()
        r.register_tool(group_key='files',capabilities=['file:read'],version='1.0.0',argument_schema=SCHEMA)(alpha)
        r.register_tool(group_key='files',capabilities=['file:read','file:write'],version='2.0.0',argument_schema=SCHEMA)(beta)
        out=r.execute('files','file:read',{'path':'sample'},self.live(('file:read','file:write')))
        self.assertEqual(out['version'],'2.0.0')
    def test_schema_and_unknown_name_never_executes(self):
        r=ToolRouter()
        r.register_tool(group_key='files',capabilities=['file:read'],version='1.0.0',argument_schema=SCHEMA)(alpha)
        out=r.execute('files','file:read',{'imagined_argument':'x'},self.live())
        self.assertEqual(out['status'],'NO_AUTHORIZED_VALID_RESULT')
        self.assertIn('SCHEMA_INVALID',out['attempts'][0]['reason'])
        self.assertEqual(r.execute('sys_delete','file:read',{},self.live())['status'],'NO_AUTHORIZED_VALID_RESULT')
    def test_approval_requirement_fails_closed(self):
        r=ToolRouter()
        r.register_tool(group_key='files',capabilities=['file:read'],version='1.0.0',argument_schema=SCHEMA)(alpha)
        self.assertEqual(r.execute('files','file:read',{'path':'ok'},self.live(permission='approval_required'))['status'],'NO_AUTHORIZED_VALID_RESULT')
    def test_high_risk_needs_approval(self):
        r=ToolRouter()
        r.register_tool(group_key='files',capabilities=['file:read'],version='1.0.0',risk='HIGH',argument_schema=SCHEMA)(alpha)
        self.assertEqual(r.execute('files','file:read',{'path':'ok'},self.live())['attempts'][0]['reason'],'HITL_APPROVAL_REQUIRED')
    def test_retry_after_empty_and_exception(self):
        r=ToolRouter()
        r.register_tool(group_key='files',capabilities=['file:read'],version='3.0.0',argument_schema=SCHEMA)(hollow)
        r.register_tool(group_key='files',capabilities=['file:read'],version='2.0.0',argument_schema=SCHEMA)(bad)
        r.register_tool(group_key='files',capabilities=['file:read'],version='1.0.0',argument_schema=SCHEMA)(alpha)
        out=r.execute('files','file:read',{'path':'ok'},self.live())
        self.assertEqual(out['version'],'1.0.0')
        self.assertEqual(len(out['attempts']),2)
    def test_chain_integrity_and_append_only(self):
        self.j.append('r1','planner','DIVERGENT',{'count':3},'s1')
        self.assertTrue(self.j.verify_chain('r1'))
        with self.assertRaises(sqlite3.IntegrityError):
            self.j.db.execute('DELETE FROM journal_entries')
    def test_timeline_drift(self):
        with self.assertRaisesRegex(ValueError,'TIMELINE_DRIFT'):
            self.j.complete_step('r1','s2',{'provider_receipt':'receipt'},
                                 {'verified':True,'source_ref':'ref','exact_target':'x'})
    def test_no_success_without_proof(self):
        with self.assertRaisesRegex(ValueError,'PROVIDER_RECEIPT_REQUIRED'):
            self.j.complete_step('r1','s1',{},
                                 {'verified':True,'source_ref':'ref','exact_target':'x'})
    def test_complete_with_receipt_and_readback(self):
        self.j.complete_step('r1','s1',{'provider_receipt':'r'},
                             {'verified':True,'source_ref':'source','exact_target':'path'})
        self.j.complete_step('r1','s2',{'provider_receipt':'r2'},
                             {'verified':True,'source_ref':'source2','exact_target':'path2'})
        self.assertTrue(self.j.verify_chain('r1'))
    def test_checkpoint_each_milestone_and_no_raw_secrets(self):
        self.b.open_divergence(self.divergences(),self.matrix)
        self.b.raw_tool_payload={'secret':'never-persist-me'}
        self.b.scratchpad={'token':'another-secret'}
        cp=self.j.checkpoint('r1',1,self.b)
        restored=self.j.restore_checkpoint('r1')
        self.assertEqual(restored.stage,'CRITIC')
        self.assertIsNone(restored.raw_tool_payload)
        self.assertNotIn('never-persist-me',str(self.j.db.execute('SELECT full_state_snapshot FROM checkpoints').fetchone()[0]))
        self.assertEqual(cp['checksum'],self.j.db.execute('SELECT checksum FROM checkpoints').fetchone()[0])
    def test_checkpoint_interval_and_milestone(self):
        self.b.open_divergence(self.divergences(), self.matrix)
        with self.assertRaisesRegex(ValueError, 'CHECKPOINT_REQUIRES_VERIFIED_DONE_STEP'):
            self.j.checkpoint_if_due('r1', 1, self.b, every_n=2)
        self.j.complete_step('r1','s1',{'provider_receipt':'r'},
                             {'verified':True,'source_ref':'source','exact_target':'path'})
        self.assertIsNone(self.j.checkpoint_if_due('r1', 1, self.b, every_n=2))
        self.assertIsNotNone(self.j.checkpoint_if_due('r1', 1, self.b, every_n=2, milestone=True))
        self.j.complete_step('r1','s2',{'provider_receipt':'r2'},
                             {'verified':True,'source_ref':'source2','exact_target':'path2'})
        self.assertIsNotNone(self.j.checkpoint_if_due('r1', 2, self.b, every_n=2))

    def test_precommit_guard_requires_real_readback(self):
        self.b.open_divergence(self.divergences(),self.matrix)
        self.assertTrue(self.b.converge('h0')[0])
        self.assertEqual(precommit_gate(self.b,self.j,'r1')[1],'READBACK_PENDING')
        self.j.complete_step('r1','s1',{'provider_receipt':'r'},
                             {'verified':True,'source_ref':'source','exact_target':'path'})
        self.j.complete_step('r1','s2',{'provider_receipt':'r2'},
                             {'verified':True,'source_ref':'source2','exact_target':'path2'})
        self.b.stage='READBACK';self.b.readback_passed=True
        self.assertTrue(precommit_gate(self.b,self.j,'r1')[0])

if __name__=='__main__':
    unittest.main()