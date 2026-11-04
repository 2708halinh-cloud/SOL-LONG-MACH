"""Authenticated binary pulse packet for the TESSERACT MCP boundary.

The caller supplies the HMAC key; this module never stores or generates secrets.
"""
from __future__ import annotations
import hashlib
import hmac
import struct
from dataclasses import dataclass

MAGIC = b"TSR1"
VERSION = 1
MAX_PAYLOAD = 4096
_HEADER = struct.Struct("!4sBBQBBI")
_SIGNATURE_SIZE = hashlib.sha256().digest_size

@dataclass(frozen=True)
class Pulse:
    tick: int
    direction: int
    hexagram: int
    payload: bytes
    flags: int = 0

def encode_pulse(pulse: Pulse, key: bytes) -> bytes:
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("HMAC key must contain at least 32 bytes")
    if pulse.tick < 0: raise ValueError("tick must be non-negative")
    if not 0 <= pulse.direction <= 7: raise ValueError("direction must be in [0, 7]")
    if not 1 <= pulse.hexagram <= 64: raise ValueError("hexagram must be in [1, 64]")
    if not 0 <= pulse.flags <= 255: raise ValueError("flags must fit in one byte")
    if not isinstance(pulse.payload, bytes) or len(pulse.payload) > MAX_PAYLOAD:
        raise ValueError("payload must be bytes no larger than MAX_PAYLOAD")
    header = _HEADER.pack(MAGIC, VERSION, pulse.flags, pulse.tick,
                          pulse.direction, pulse.hexagram, len(pulse.payload))
    body = header + pulse.payload
    return body + hmac.new(key, body, hashlib.sha256).digest()

def decode_pulse(packet: bytes, key: bytes) -> Pulse:
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("HMAC key must contain at least 32 bytes")
    if len(packet) < _HEADER.size + _SIGNATURE_SIZE:
        raise ValueError("packet is truncated")
    magic, version, flags, tick, direction, hexagram, payload_len = _HEADER.unpack(
        packet[:_HEADER.size]
    )
    if magic != MAGIC or version != VERSION:
        raise ValueError("unsupported pulse header")
    if payload_len > MAX_PAYLOAD:
        raise ValueError("payload length exceeds limit")
    expected_length = _HEADER.size + payload_len + _SIGNATURE_SIZE
    if len(packet) != expected_length:
        raise ValueError("packet length does not match header")
    body, signature = packet[:-_SIGNATURE_SIZE], packet[-_SIGNATURE_SIZE:]
    expected = hmac.new(key, body, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("pulse authentication failed")
    if direction > 7 or not 1 <= hexagram <= 64:
        raise ValueError("invalid direction or hexagram")
    return Pulse(tick, direction, hexagram,
                 packet[_HEADER.size:_HEADER.size + payload_len], flags)
