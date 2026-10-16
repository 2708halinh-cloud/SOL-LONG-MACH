import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT))
import power_capability_router as pr

class TestRouteIntegration(unittest.TestCase):
    def test_one_tag_entry_outranks_time_and_terex(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/pr.ROOT_REL/pr.REGISTRY
            p.parent.mkdir(parents=True)
            p.write_bytes((ROOT/'POWER_CAPABILITY_ROUTES_V2.json').read_bytes())
            result=pr.route('Anh gọi @SPACE_STONE và @TEREX, X-TIME du hành thời gian',Path(td))
            self.assertEqual(result['candidates'][0]['capability_id'],'space-stone-unified')
            self.assertEqual(result['next_action'],'RESOLVE_FIVE_CAPABILITIES_AND_DISPATCH_AUTHORIZED_PROVIDER_THEN_READBACK')
            self.assertFalse(result['action_executed'])
            self.assertTrue(any(c['capability_id']=='x-time-multi-agent' for c in result['candidates']))

if __name__=='__main__':unittest.main()
