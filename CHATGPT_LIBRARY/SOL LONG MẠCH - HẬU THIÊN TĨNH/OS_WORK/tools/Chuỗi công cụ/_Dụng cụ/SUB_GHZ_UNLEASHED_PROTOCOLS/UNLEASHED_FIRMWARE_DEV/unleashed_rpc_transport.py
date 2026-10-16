#!/usr/bin/env python3
"""Host-side safe read-only tools for Flipper CDC enumeration and delimited RPC frame inspection.

The firmware uses nanopb PB_ENCODE_DELIMITED / PB_DECODE_DELIMITED; this module
validates the varint length prefix, NOT the PB_Main schema (missing submodule).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

MAX_FRAME = 65536

def encode_varint(value:int)->bytes:
    if not 0<=value<=MAX_FRAME:raise ValueError('length out of bounds')
    out=bytearray()
    while value>127:
        out.append((value&0x7f)|0x80);value >>=7
    out.append(value)
    return bytes(out)

class RpcFrameStream:
    """Bounded incremental length-delimited frame parser for split USB CDC reads.

    Metadata only: no raw payload leaves next_chunk().
    """
    def __init__(self):
        self.buffer=bytearray()
        self.wire_offset=0
        self.frame_count=0

    def next_chunk(self, chunk:bytes, final:bool=False):
        if len(chunk)>2_000_000:raise ValueError('chunk exceeds input limit')
        self.buffer.extend(chunk)
        output=[]
        while self.buffer:
            length=0
            prefix_size=0
            for i,b in enumerate(self.buffer[:5]):
                length|=(b & 0x7f) << (7*i)
                prefix_size=i+1
                if not b & 0x80:break
            else:
                if len(self.buffer)>=5:raise ValueError('varint too long')
                break
            if length>MAX_FRAME:raise ValueError('frame exceeds limit')
            if len(self.buffer)<prefix_size+length:break
            payload=bytes(self.buffer[prefix_size:prefix_size+length])
            output.append({'offset':self.wire_offset,'protobuf_length':length,
                'sha256':hashlib.sha256(payload).hexdigest(),
                'protobuf_decoded':False,'schema_loaded':False})
            consumed=prefix_size+length
            del self.buffer[:consumed]
            self.wire_offset+=consumed
            self.frame_count+=1
        if final and self.buffer:raise ValueError('truncated length-delimited frame')
        return output


def decode_frames(data:bytes):
    parser=RpcFrameStream()
    return parser.next_chunk(data,final=True)

def device_ports():
    try:
        from serial.tools import list_ports
    except ImportError:
        return {"ports":[],"dependency":"pyserial (not installed)","connected_hardware_verified":False}
    return {"ports":[{"device":p.device,"vid":p.vid,"pid":p.pid,"description":p.description} for p in list_ports.comports()],
            "dependency":"pyserial","connected_hardware_verified":False}

def read_serial(port:str,timeout:float=1.0,max_bytes:int=4096):
    if not port:raise ValueError('explicit --port is required')
    if not 0<timeout<=10 or not 1<=max_bytes<=MAX_FRAME:raise ValueError('invalid read bound')
    try:
        import serial
    except ImportError as exc:
        raise RuntimeError('pyserial required; no device opened') from exc
    # Never send commands, RF payloads, keys or GPIO writes. This is a passive CDC read.
    with serial.Serial(port=port,baudrate=230400,timeout=timeout,write_timeout=timeout) as device:
        b=device.read(max_bytes)
    return {"port":port,"read_bytes":len(b),"payload_sha256":hashlib.sha256(b).hexdigest(),
            "write_bytes":0,"rpc_decoded":False,"raw_serial_sample_logged":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='cmd',required=True)
    f=sub.add_parser('frame-check');f.add_argument('path',type=Path)
    sub.add_parser('ports')
    s=sub.add_parser('serial-read');s.add_argument('--port',required=True);s.add_argument('--timeout',type=float,default=1)
    a=p.parse_args()
    try:
        if a.cmd=='frame-check':
            data=a.path.read_bytes()
            if len(data)>2_000_000:raise ValueError('input file exceeds limit')
            result={"framing":"nanopb length-delimited","frames":decode_frames(data),"hardware_contact":False}
        elif a.cmd=='ports':result=device_ports()
        else:result=read_serial(a.port,a.timeout)
    except (OSError,RuntimeError,ValueError) as exc:
        print(json.dumps({"error":str(exc),"operation":a.cmd}),file=sys.stderr);return 2
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':sys.exit(main())
