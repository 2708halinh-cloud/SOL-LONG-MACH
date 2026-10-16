#!/usr/bin/env python3
"""Offline test uses only synthetic bytes; no hardware or original ROM."""
from pathlib import Path
import tempfile,hashlib
from inspect_rom import inspect

def main():
    with tempfile.TemporaryDirectory(prefix='pcxt_bios_test_') as d:
        p=Path(d)/'synthetic.bin'
        b=bytes(8192)
        p.write_bytes(b)
        x=inspect(p)
        assert x['is_8k_core_size'] and x['bytes']==8192
        assert x['sha256']==hashlib.sha256(b).hexdigest()
        assert x['full_image_sum_mod_256']==0 and x['full_image_zero_checksum']
        assert x['extension_rom']['signature']=='absent'
        assert x['repeats_8k_block'] is False
        p.write_bytes(bytes.fromhex('55aa01')+bytes(509))
        y=inspect(p)
        assert y['extension_rom']['signature']=='55aa'
        assert y['extension_rom']['declared_bytes']==512
        assert y['extension_rom']['declared_size_valid']
    print('PASS synthetic_rom_selftest; physical BIOS NOT_TESTED')
if __name__=='__main__':main()
