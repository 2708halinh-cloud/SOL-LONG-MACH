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
        self.assertNotIn("VERIFIED_STATUS_REQUIRES_ID_AND_BOOLEAN_READBACK", errors)

    def test_verified_requires_id_and_boolean_readback(self):
        data = manifest()
        data["identity_status"] = "VERIFIED"
        self.assertIn("VERIFIED_STATUS_REQUIRES_ID_AND_BOOLEAN_READBACK", validate_manifest(data))

    def test_verified_rejects_truthy_non_boolean_readback(self):
        for value in ("false", "true", 1, [], {}):
            with self.subTest(value=value):
                data = manifest()
                data["identity"]["agent_id"] = "sol-agent-id-from-authorized-source"
                data["identity_status"] = "VERIFIED"
                data["independent_readback"] = value
                self.assertIn(
                    "VERIFIED_STATUS_REQUIRES_ID_AND_BOOLEAN_READBACK",
                    validate_manifest(data),
                )

    def test_verified_accepts_only_nonempty_string_id_and_true_readback(self):
        data = manifest()
        data["identity"]["agent_id"] = "sol-agent-id-from-authorized-source"
        data["identity_status"] = "VERIFIED"
        data["independent_readback"] = True
        self.assertNotIn("VERIFIED_STATUS_REQUIRES_ID_AND_BOOLEAN_READBACK", validate_manifest(data))

    def test_non_string_stable_id_is_rejected(self):
        data = manifest()
        data["identity"]["agent_id"] = {"id": "guessed"}
        data["identity_status"] = "VERIFIED"
        data["independent_readback"] = True
        self.assertIn("STABLE_AGENT_ID_TYPE_INVALID", validate_manifest(data))
        self.assertIn("VERIFIED_STATUS_REQUIRES_ID_AND_BOOLEAN_READBACK", validate_manifest(data))

    def test_source_refs_must_be_nonempty_list_of_strings(self):
        for refs in ("github:commit:abc", [], [" "], [None]):
            with self.subTest(refs=refs):
                data = manifest()
                data["source_refs"] = refs
                self.assertIn("SOURCE_PROVENANCE_REQUIRED", validate_manifest(data))

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

    def test_event_rejects_unstructured_source_refs(self):
        with self.assertRaisesRegex(ValueError, "EVENT_ID_KIND_AND_SOURCE_REFS_REQUIRED"):
            make_event({
                "event_id": "e1", "kind": "source_read",
                "source_refs": "github:commit:abc",
            })

    def test_mutation_is_detected(self):
        event = make_event({
            "event_id": "e1", "kind": "source_read",
            "source_refs": ["github:commit:abc"], "observation": "source fetched",
        })
        event["observation"] = "silently altered"
        self.assertEqual("FAIL", verify_events([event])["chain_integrity"])

    def test_malformed_event_record_fails_closed(self):
        result = verify_events([{"schema": "SOL_AGENT_EVENT_V1"}, None])
        self.assertEqual("FAIL", result["chain_integrity"])
        self.assertIn("EVENT_ID_INVALID:0", result["errors"])
        self.assertIn("EVENT_OBJECT_REQUIRED:1", result["errors"])

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
