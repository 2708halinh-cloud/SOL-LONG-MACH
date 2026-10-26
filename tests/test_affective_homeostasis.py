import sqlite3, tempfile, unittest
from pathlib import Path
from runtime.affective_homeostasis import AffectiveStore, Telemetry, derive_state

class HomeostasisTests(unittest.TestCase):
    def test_stress_reduces_gain_and_recommends_lock(self):
        calm = derive_state(Telemetry(cpu_load=.1, ram_used_fraction=.2, disk_used_fraction=.3))
        stress = derive_state(Telemetry(prediction_error=.9, tool_failure_fraction=.9,
            consecutive_failures=4, cpu_load=.9, ram_used_fraction=.9, disk_used_fraction=.4))
        self.assertLess(stress["response_gain"], calm["response_gain"])
        self.assertFalse(stress["write_sensitive_data_allowed"])
        self.assertEqual(stress["mode"], "STRESSED")
    def test_disk_threshold_defensive(self):
        self.assertEqual(derive_state(Telemetry(disk_used_fraction=.90))["mode"], "DEFENSIVE")
    def test_curiosity_from_novelty_and_uncertainty_reduction(self):
        state = derive_state(Telemetry(new_information_fraction=.8, uncertainty_before=.9, uncertainty_after=.2))
        self.assertGreater(state["curiosity"], .7)
        self.assertEqual(state["mode"], "CURIOUS")
    def test_additive_schema_and_readback(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td)/"state.sqlite"
            with sqlite3.connect(db) as c:
                c.execute("CREATE TABLE legacy_state(value TEXT)")
                c.execute("INSERT INTO legacy_state VALUES('preserve')")
            store = AffectiveStore(db); store.initialize()
            r = store.record(Telemetry(prediction_error=.2), "test://telemetry")
            self.assertEqual(r["readback"]["event_id"], r["event_id"])
            with sqlite3.connect(db) as c:
                self.assertEqual(c.execute("SELECT value FROM legacy_state").fetchone()[0], "preserve")
    def test_hash_chain_and_append_only(self):
        with tempfile.TemporaryDirectory() as td:
            store = AffectiveStore(Path(td)/"state.sqlite"); store.initialize()
            a = store.record(Telemetry(), "test://one")
            b = store.record(Telemetry(prediction_error=.2), "test://two")
            self.assertEqual(b["previous_event_hash"], a["event_hash"])
            with store.connect() as c:
                with self.assertRaises(sqlite3.IntegrityError):
                    c.execute("DELETE FROM affective_events WHERE event_id=?", (a["event_id"],))
    def test_policy_trace_bounded_and_auditable(self):
        with tempfile.TemporaryDirectory() as td:
            store = AffectiveStore(Path(td)/"state.sqlite"); store.initialize()
            event = store.record(Telemetry(), "test://event")["event_id"]
            store.imprint_trace(event, "avoid.failed.route", -9, .8, "Repeated observed failure")
            self.assertAlmostEqual(store.effective_policy_bias("avoid.failed.route"), -.08)

if __name__ == "__main__":
    unittest.main()
