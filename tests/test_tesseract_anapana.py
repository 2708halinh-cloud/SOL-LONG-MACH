import asyncio, unittest
from runtime.tesseract_snn.anapana import AnapanaMonitor, TelemetrySnapshot

class AnapanaTests(unittest.IsolatedAsyncioTestCase):
    async def test_monitor_samples_without_chat_requests_and_stops(self):
        count={"n":0}; observed=asyncio.Event()
        async def sensor():
            count["n"] += 1
            return TelemetrySnapshot(1.0,0.25,100,1000,5000,42.0)
        async def observer(sample):
            if count["n"] >= 3: observed.set()
        monitor=AnapanaMonitor(sensor,interval_seconds=.001,history_limit=2,observer=observer)
        monitor.start()
        await asyncio.wait_for(observed.wait(),timeout=1)
        await monitor.stop()
        self.assertFalse(monitor.running)
        self.assertGreaterEqual(count["n"],3)
        self.assertEqual(len(monitor.history),2)

    async def test_invalid_sensor_value_fails_closed(self):
        async def sensor():
            return TelemetrySnapshot(1.0,1.5,10,100,1000)
        monitor=AnapanaMonitor(sensor,interval_seconds=.001)
        task=monitor.start()
        with self.assertRaises(ValueError): await task

if __name__ == "__main__": unittest.main()
