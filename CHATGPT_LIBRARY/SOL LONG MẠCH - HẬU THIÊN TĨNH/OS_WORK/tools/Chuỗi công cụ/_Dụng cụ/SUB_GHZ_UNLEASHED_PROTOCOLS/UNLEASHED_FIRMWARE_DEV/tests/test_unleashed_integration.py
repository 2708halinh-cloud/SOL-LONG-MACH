"""Deterministic offline tests: no provider, device, RF, network or firmware flash."""
import hashlib
import shutil
import subprocess
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from unleashed_source_index import build_index, parse_submodules, CAPABILITIES
from unleashed_build_diagnostics import diagnose,build_preflight
from unleashed_rpc_transport import decode_frames,encode_varint
from unleashed_sensorimotor import append,verify,CHANNELS,read_journal,rebuild_mirrors

class FirmwareToolsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parent.parent
    def test_stm32wb_driver_host_syntax(self):
        cc=shutil.which("cc") or shutil.which("gcc")
        if not cc:self.skipTest("C compiler unavailable")
        base=Path(__file__).resolve().parents[1]
        src=base/"fap/sol_gpio_observer"
        cmd=[cc,"-std=c11","-Wall","-Wextra","-fsyntax-only","-I",str(base/"tests/mock_hal"),"-I",str(src),str(src/"sol_stm32wb_gpio.c"),str(src/"sol_gpio_observer.c")]
        result=subprocess.run(cmd,capture_output=True,text=True,check=False)
        self.assertEqual(result.returncode,0,result.stderr)
    def test_index_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'.gitmodules').write_text('[submodule "lib/nanopb"]\n path = lib/nanopb\n url = https://github.com/nanopb/nanopb.git\n')
            (p/'fbt').write_text('#!/bin/sh\n')
            m=build_index(p,'sample')
            self.assertEqual(m['submodule_count'],1)
            self.assertEqual(m['submodule_payloads_present'],0)
            self.assertEqual(m['submodules'][0]['path'],'lib/nanopb')
            self.assertFalse(m['git_metadata_present'])
    def test_rpc_varint_and_frame(self):
        blob=b'\x08\x01'*150
        frame=encode_varint(len(blob))+blob
        result=decode_frames(frame)
        self.assertEqual(result[0]['protobuf_length'],300)
        self.assertEqual(result[0]['sha256'],hashlib.sha256(blob).hexdigest())
        self.assertFalse(result[0]['protobuf_decoded'])
        for malformed in [b'\x80',b'\xff\xff\xff\xff\xff',b'\x06a']:
            with self.assertRaises(ValueError):decode_frames(malformed)
    def test_diagnosis_classes(self):
        report=diagnose('Rpc ERROR_DECODE invalid frame\nHardFault at PC=0x1234\nSD Card storage error FR_DISK_ERR')
        classes={x['category'] for x in report['categories']}
        self.assertTrue({'rpc_decode','crash_assert','storage'}.issubset(classes))
    def test_build_preflight_archive_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'fbt').write_text('');(p/'.gitmodules').write_text('')
            result=build_preflight(p,'updater_package')
            self.assertFalse(result['ready']);self.assertIn('fbt',result['cwd']+'/fbt')
    def test_journal_chain_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            first=append(root,'input','SOURCE_INSPECTED',{'status':'VERIFIED','sha256':'f'*64})
            second=append(root,'spatial','SENSOR_READBACK',{'interface':'GPIO','status':'TEST_ONLY'})
            third=append(root,'chrono','TEST_SIMULATION',{'event_count':2})
            self.assertTrue(third['readback_verified'])
            self.assertEqual(verify(root)['events'],3)
            self.assertEqual(len(read_journal(root)),3)
            log=root/CHANNELS['chrono'];log.write_text(log.read_text().replace('GPIO','NFC'))
            self.assertFalse(verify(root)['valid'])
            with self.assertRaises(ValueError):append(root,'state','APP_EVENT',{'status':'FAIL'})
    def test_derived_mirror_reconstruction(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            append(root,'state','BUILD_PREFLIGHT',{'status':'BLOCKED'})
            (root/CHANNELS['state']).write_text('tampered\n')
            self.assertFalse(verify(root)['valid'])
            self.assertTrue(verify(root,mirrors=False)['valid'])
            self.assertTrue(rebuild_mirrors(root,True)['readback_verified'])
            self.assertEqual(verify(root)['events'],1)
    def test_journal_reject_unknown_sensitive_fields(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):append(Path(d),'input','SOURCE_INSPECTED',{'password':'no'})

if __name__=='__main__':unittest.main()
