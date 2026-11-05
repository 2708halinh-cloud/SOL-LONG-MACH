import unittest
from runtime.tesseract_snn.pulse import Pulse, encode_pulse, decode_pulse

class PulsePacketTests(unittest.TestCase):
    def setUp(self):
        self.key=b"tesseract-test-key-material-32bytes!"
    def test_round_trip(self):
        original=Pulse(tick=42,direction=7,hexagram=64,payload=b"state",flags=3)
        self.assertEqual(decode_pulse(encode_pulse(original,self.key),self.key),original)
    def test_rejects_tampering(self):
        packet=bytearray(encode_pulse(Pulse(1,0,1,b"abc"),self.key))
        packet[-1] ^= 1
        with self.assertRaises(ValueError): decode_pulse(bytes(packet),self.key)
    def test_rejects_wrong_key(self):
        packet=encode_pulse(Pulse(1,0,1,b"abc"),self.key)
        with self.assertRaises(ValueError): decode_pulse(packet,b"x"*32)
    def test_rejects_out_of_range_matrix_ids(self):
        with self.assertRaises(ValueError): encode_pulse(Pulse(1,8,1,b""),self.key)
        with self.assertRaises(ValueError): encode_pulse(Pulse(1,0,65,b""),self.key)
    def test_rejects_trailing_or_truncated_bytes(self):
        packet=encode_pulse(Pulse(1,0,1,b"abc"),self.key)
        with self.assertRaises(ValueError): decode_pulse(packet+b"x",self.key)
        with self.assertRaises(ValueError): decode_pulse(packet[:-1],self.key)

if __name__ == "__main__": unittest.main()
