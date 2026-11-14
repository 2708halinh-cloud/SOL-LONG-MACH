import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import space_stone_gateway as g

class FakeProvider:
    def __init__(self,store=None): self.store=dict(store or {})
    def read(self,id): return self.store[id]
    def write(self,id,raw,*,overwrite=False):
        if not overwrite and id in self.store: raise FileExistsError(id)
        self.store[id]=raw
        return {'provider_write_receipt':id}
    def move(self,a,b):
        if b in self.store: raise FileExistsError(b)
        self.store[b]=self.store.pop(a)
        return {'move':(a,b)}
    def probe(self,id): return {'reachable':id in self.store,'authorized':True,'id':id}

class TestUnifiedSpaceStone(unittest.TestCase):
    def test_five_modes(self):
        for mode in ['TELEPORTATION','WORMHOLE_PORTAL','SPACE_CONTROL','TESSERACT_POWER','SPACE_TIME_TRAVEL']:
            self.assertEqual(g.plan('@SPACE_STONE',mode)['operation'],mode)
    def test_delegates_time(self):
        self.assertEqual(g.plan('@SPACE_STONE + @TIME_STONE du hành thời gian')['operation'],'SPACE_TIME_TRAVEL')
    def test_copy_cross_provider_real_bytes_and_readback(self):
        src,dst=FakeProvider({'s':b'raw evidence'}),FakeProvider()
        receipt=g.copy_verified(src,dst,'s','t')
        self.assertEqual(dst.store['t'],b'raw evidence')
        self.assertEqual(src.store['s'],b'raw evidence')
        self.assertFalse(receipt['source_deleted'])
    def test_copy_never_silently_overwrites(self):
        with self.assertRaises(FileExistsError):
            g.copy_verified(FakeProvider({'s':b'a'}),FakeProvider({'t':b'b'}),'s','t')
    def test_same_provider_move_readback(self):
        p=FakeProvider({'s':b'original'})
        receipt=g.move_verified(p,'s','t')
        self.assertEqual(receipt['status'],'DESTINATION_READBACK_VERIFIED')
        self.assertNotIn('s',p.store)
    def test_portal_needs_live_callability(self):
        a,b=FakeProvider({'a':b'x'}),FakeProvider()
        self.assertFalse(g.portal_probe(a,b,'a','b')['ready'])
    def test_space_control_logical_only(self):
        self.assertFalse(g.space_transform((106.9,10.8),(0.1,0.1))['physical_space_modified'])
    def test_budget_non_physical(self):
        self.assertFalse(g.resource_budget(10,500)['physical_energy_generated'])
    def test_reentry_is_historical_and_not_time_travel(self):
        e=[{'entity_id':'anchor','revision':'t1'}]
        self.assertEqual(g.spacetime_reentry('anchor','t1',e)['status'],'REVISION_FOUND')
        self.assertFalse(g.spacetime_reentry('anchor','t1',e)['real_time_reversed'])
    def test_selector_is_integrated_and_tag_priority(self):
        registry=json.loads((Path(__file__).parent/'POWER_CAPABILITY_ROUTES_V2.json').read_text(encoding='utf-8'))
        cap=[x for x in registry['capabilities'] if x['id']=='space-stone-unified']
        self.assertEqual(len(cap),1)
        self.assertIn('@SPACE_STONE',cap[0]['aliases'])
        text=(Path(__file__).parent/'power_capability_router.py').read_text(encoding='utf-8')
        self.assertIn('choice["score"] = 10000',text)

if __name__=='__main__': unittest.main()
