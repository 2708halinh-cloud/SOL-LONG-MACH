"""DANTE 404 regression: inaccessible IDs must not be mistaken for deleted data."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("dante_gate", REPO / "runtime" / "dante_carrier_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class DanteCarrierGateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        actual = json.loads((REPO / gate.CONFIG).read_text(encoding="utf-8"))
        dest = self.base / gate.CONFIG
        dest.parent.mkdir(parents=True)
        dest.write_text(json.dumps(actual), encoding="utf-8")
        self.snapshot = self.base / gate.SKILL_SNAPSHOT
        self.snapshot.parent.mkdir(parents=True)
        self.snapshot.write_bytes((REPO / gate.SKILL_SNAPSHOT).read_bytes())

    def test_all_six_404_keep_unknown_deletion_and_choose_preserved_skill(self):
        r = gate.audit(self.base)
        self.assertEqual(r["historical_404_carriers"], 6)
        self.assertEqual(r["fresh_provider_observations_supplied"], 0)
        self.assertFalse(r["provider_calls_performed_by_this_gate"])
        self.assertTrue(all(x["fresh_provider_status"] is None for x in r["carriers"]))
        self.assertTrue(all(x["state"] == "HISTORICAL_404_SNAPSHOT_ONLY" for x in r["carriers"]))
        self.assertEqual(r["accessible_reported_count"], 0)
        self.assertEqual(r["next_action"], "RECOVER_ROUTER_SEMANTICS_FROM_GITHUB_SNAPSHOT")
        self.assertTrue(r["skill_snapshot_covers_historical_ids"])
        self.assertIsNone(r["deleted_source_conclusion"])
        self.assertFalse(r["external_drive_data_recovered"])
        self.assertTrue(all(x["source_deleted"] is None for x in r["carriers"]))

    def test_provider_read_ok_does_not_automatically_certify_restoration(self):
        r = gate.audit(self.base, availability={"README": "READ_OK"})
        self.assertEqual(r["accessible_reported_count"], 1)
        self.assertEqual(r["fresh_provider_observations_supplied"], 1)
        self.assertFalse(r["provider_calls_performed_by_this_gate"])
        self.assertEqual(r["next_action"], "VERIFY_LIVE_PROVIDER_IDS")
        self.assertFalse(r["external_drive_data_recovered"])
        target = next(x for x in r["carriers"] if x["role"] == "README")
        self.assertEqual(target["state"], "PROVIDER_READ_REPORTED_UNVERIFIED")

    def test_skill_missing_gives_search_next_edge_not_source_destroyed(self):
        self.snapshot.unlink()
        r = gate.audit(self.base)
        self.assertEqual(r["next_action"], "SEARCH_AUTHORIZED_SOURCE_CARRIERS")
        self.assertFalse(r["skill_snapshot_exists"])
        self.assertIsNone(r["deleted_source_conclusion"])

    def test_bad_source_classification_is_rejected(self):
        p = self.base / gate.CONFIG
        o = json.loads(p.read_text(encoding="utf-8"))
        o["carriers"][0]["source_deleted"] = True
        p.write_text(json.dumps(o), encoding="utf-8")
        with self.assertRaises(ValueError):
            gate.audit(self.base)

    def test_missing_role_or_unsupported_status_fails_closed(self):
        with self.assertRaises(ValueError):
            gate.audit(self.base, availability={"README": "PROVEN_DELETED"})
        p = self.base / gate.CONFIG
        o = json.loads(p.read_text(encoding="utf-8"))
        o["carriers"].pop()
        p.write_text(json.dumps(o), encoding="utf-8")
        with self.assertRaises(ValueError):
            gate.audit(self.base)


if __name__ == "__main__":
    unittest.main()
