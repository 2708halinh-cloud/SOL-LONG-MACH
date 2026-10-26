import json
import tempfile
import unittest
from pathlib import Path

from runtime.sol_agent_continuity import (
    SCHEMA, IDENTITY_FIELDS, append_event, make_event, validate_manifest, verify_events,
)


def manifest():
    identity = {key: None for key in IDENTITY_FIELDS}
    identity.update({"name": "Sol Cu Nhỏ", "agent_id": None})
    return {
        "schema": SCHEMA,
        "identity_status": "OPEN",
        "identity": identity,
        "source_refs": ["GitHub:2708halinh-cloud/SOL-LONG-MACH@9cf5f97"],
        "independent_readback": False,
    }


class ContinuityTests(unittest.TestCase):
    def test_missing_stable_id_remains_open_not_guessed(self):
        errors = validate_manifest(manifest())
        self.assertIn("STABLE_AGENT_ID_UNRESOLVED", errors)
        self.assertNotIn("VERIFIED_STATUS_REQUIRES_ID_AND_READBACK", errors)

    def test_verified_requires_id_and_independent_readback(self):
        data = manifest()
        data["identity_status"] = "VERIFIED"
        self.assertIn("VERIFIED_STATUS_REQUIRES_ID_AND_READBACK", validate_manifest(data))

    def test_event_hash_chain_passes(self):
        first = make_event({
            "event_id": "e1", "kind": "source_read",
            "source_refs": ["github:commit:abc"], "observation": "source fetched",
        })
        second = make_event({
            "event_id": "e2", "kind": "test",
            "source_refs": ["local:test-run"], "outcome": "pass",
        }, previous_hash=first["event_hash"])
        self.assertEqual("PASS", verify_events([first, second])["chain_integrity"])

    def test_mutation_is_detected(self):
        event = make_event({
            "event_id": "e1", "kind": "source_read",
            "source_refs": ["github:commit:abc"], "observation": "source fetched",
        })
        event["observation"] = "silently altered"
        self.assertEqual("FAIL", verify_events([event])["chain_integrity"])

    def test_append_preserves_existing_event_and_refuses_corrupt_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal = Path(tmp) / "events.jsonl"
            append_event(journal, {
                "event_id": "e1", "kind": "source_read",
                "source_refs": ["github:commit:abc"],
            })
            append_event(journal, {
                "event_id": "e2", "kind": "test",
                "source_refs": ["local:test-run"],
            })
            events = [json.loads(line) for line in journal.read_text().splitlines()]
            self.assertEqual(2, len(events))
            self.assertEqual("PASS", verify_events(events)["chain_integrity"])
            events[0]["outcome"] = "altered"
            journal.write_text("\n".join(json.dumps(x) for x in events) + "\n")
            with self.assertRaisesRegex(ValueError, "EXISTING_EVENT_CHAIN_INVALID"):
                append_event(journal, {
                    "event_id": "e3", "kind": "repair",
                    "source_refs": ["local:repair"],
                })


if __name__ == "__main__":
    unittest.main()
