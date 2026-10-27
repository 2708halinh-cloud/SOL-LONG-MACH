"""Tests for a preallocated fixed-size scratch-buffer pool.

STAMP_LIVE_X: 2026-10-27 (UTC+07:00; minute not independently measured)
SOURCE_ID: SOL-LONG-MACH / ChatGPT Library / OS_WORK/tools
ACTOR: Hà Linh (design source); SOL (implementation and verification)
ACTIVE: TRUE
PROVENANCE: New isolated feature branch; tests precede implementation.
"""
import unittest

from fixed_buffer_pool import BufferPoolExhausted, FixedBufferPool


class FixedBufferPoolTests(unittest.TestCase):
    def test_capacity_is_preallocated_and_bounded(self):
        pool = FixedBufferPool(buffer_count=2, buffer_size=64)
        first = pool.acquire()
        second = pool.acquire()
        self.assertEqual(len(first), 64)
        self.assertEqual(len(second), 64)
        with self.assertRaises(BufferPoolExhausted):
            pool.acquire()
        pool.release(first)
        pool.release(second)

    def test_release_reuses_the_same_preallocated_storage(self):
        pool = FixedBufferPool(buffer_count=1, buffer_size=32)
        first = pool.acquire()
        backing_id = id(first.obj)
        first[:4] = b"test"
        pool.release(first)

        second = pool.acquire()
        self.assertEqual(id(second.obj), backing_id)
        self.assertEqual(second[:4].tobytes(), b"test")
        pool.release(second)

    def test_double_release_is_rejected(self):
        pool = FixedBufferPool(buffer_count=1, buffer_size=8)
        view = pool.acquire()
        pool.release(view)
        with self.assertRaises(ValueError):
            pool.release(view)

    def test_invalid_dimensions_are_rejected(self):
        for count, size in ((0, 8), (1, 0), (-1, 8), (1, -1)):
            with self.subTest(count=count, size=size):
                with self.assertRaises(ValueError):
                    FixedBufferPool(buffer_count=count, buffer_size=size)

    def test_release_rejects_foreign_view(self):
        pool = FixedBufferPool(buffer_count=1, buffer_size=8)
        foreign = memoryview(bytearray(8))
        with self.assertRaises(ValueError):
            pool.release(foreign)


if __name__ == "__main__":
    unittest.main()
