"""Regression: TIME joins REALITY identity and SPACE position without inventing proof."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TIME_SOURCE = REPO / (
    "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/"
    "BRIDGE_TIME_TÓC🟢MỘC_TIME/time_bridge.py"
)
spec = importlib.util.spec_from_file_location("sol_time_bridge", TIME_SOURCE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


def sample(**changes):
    v = {
        "schema": bridge.SCHEMA, "event_id": "event-from-observation",
        "source_ref": "provider://observed-source", "identity_label": "HOME_SOL",
        "stamp_class": "STAMP_LIVE", "observed_at": "2026-10-16T10:00:00+07:00",
        "space": {"provider": "Provider-A", "stable_id": "record:123",
                  "parent_id": "parent:45", "surface": "source-ui"},
        "x_literal": None, "x_reference_frame": None
    }
    v.update(changes)
    return v


class TimeIndexTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name)
        p = self.repo / bridge.IDENTITY_INDEX
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"names": [
            {"label": "HOME_SOURCE", "kind": "SOURCE_HOME", "source": "source://a"},
            {"label": "HOME_SOL", "kind": "RUNTIME_HOME", "source": "source://b"},
            {"label": "LOCUS_SOL", "kind": "CONVERSATION_LOCUS", "source": "source://c"}
        ]}), encoding="utf-8")
        s = self.repo / bridge.SPACE_SOURCE
        s.parent.mkdir(parents=True)
        s.write_text(json.dumps({"stone": "SPACE"}), encoding="utf-8")

    def test_known_id_and_space_links_next_action_not_completed(self):
        r = bridge.connect(sample(), self.repo)
        self.assertEqual(r["state"], "REFERENT_TIME_SPACE_LINKED")
        self.assertEqual(r["next_callable_edge"], "CHOOSE_AUTHORIZED_MOTOR_AND_OBSERVE")
        self.assertEqual(r["identity_candidate"]["kind"], "RUNTIME_HOME")
        self.assertFalse(r["action_performed_by_this_operator"])
        self.assertFalse(r["provider_receipt_verified_live"])

    def test_unscoped_sol_is_not_single_identity(self):
        r = bridge.connect(sample(identity_label="Sol"), self.repo)
        self.assertEqual(r["state"], "IDENTITY_NEEDS_RESOLUTION")
        self.assertGreaterEqual(len(r["identity_candidates_if_ambiguous"]), 2)

    def test_missing_space_id_routes_provider_lookup(self):
        item = sample()
        item["space"]["stable_id"] = None
        r = bridge.connect(item, self.repo)
        self.assertEqual(r["state"], "SPACE_NEEDS_PROVIDER_ID")
        self.assertEqual(r["next_callable_edge"], "QUERY_PROVIDER_FOR_SCOPED_ID")

    def test_missing_parent_routes_frame_lookup(self):
        item = sample()
        del item["space"]["parent_id"]
        self.assertEqual(bridge.connect(item, self.repo)["state"], "SPACE_NEEDS_PARENT_FRAME")

    def test_x_minus_plus_not_inferred_from_timestamp(self):
        item = sample(x_literal="STAMP_LIVE - X(-)(+)N+")
        r = bridge.connect(item, self.repo)
        self.assertEqual(r["state"], "X_FRAME_NEEDS_SOURCE")
        self.assertEqual(r["x_literal"], "STAMP_LIVE - X(-)(+)N+")
        item["x_reference_frame"] = "source-frame-given"
        self.assertEqual(bridge.connect(item, self.repo)["state"], "REFERENT_TIME_SPACE_LINKED")

    def test_beta_cannot_claim_finished_action(self):
        item = sample(stamp_class="STAMP_BETA", action="action-template", provider_receipt="claim")
        r = bridge.connect(item, self.repo)
        self.assertEqual(r["state"], "BETA_NOT_OBSERVED_ACTION")
        self.assertEqual(r["next_callable_edge"], "SEPARATE_FORECAST_FROM_LIVE_RECEIPT")
        item["action"] = None
        item["provider_receipt"] = None
        self.assertEqual(bridge.connect(item, self.repo)["state"], "FORECAST_NOT_EXECUTED")

    def test_old_requires_original_event_time_when_not_provided(self):
        r = bridge.connect(sample(stamp_class="STAMP_OLD", observed_at=None), self.repo)
        self.assertEqual(r["state"], "HISTORICAL_EVENT_TIME_NEEDS_SOURCE")

    def test_partial_receipt_never_becomes_n_plus_one(self):
        partial = bridge.connect(sample(action="ran", provider_receipt="reported"), self.repo)
        self.assertEqual(partial["state"], "PARTIAL_ACTION_EVIDENCE")
        complete = bridge.connect(sample(action="ran", provider_receipt="reported",
                                         readback_ref="provider://check"), self.repo)
        self.assertEqual(complete["state"], "ACTION_RECORDED_UNVERIFIED_PROVIDER")
        self.assertFalse(complete["provider_receipt_verified_live"])

    def test_identity_role_conflict_kept_separate(self):
        r = bridge.connect(sample(identity_kind="SOURCE_HOME"), self.repo)
        self.assertEqual(r["state"], "IDENTITY_KIND_CONFLICT")

    def test_invalid_source_or_stamp_refused(self):
        with self.assertRaises(ValueError):
            bridge.connect(sample(stamp_class="STAMP_UNKNOWN"), self.repo)
        with self.assertRaises(ValueError):
            bridge.connect(sample(event_id=None), self.repo)


if __name__ == "__main__":
    unittest.main()
