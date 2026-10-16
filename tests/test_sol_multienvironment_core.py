"""Regression tests for SOL's read-only cross-environment Core operators."""
import unittest
from runtime.sol_multienvironment_core import (
    SCHEMA, get_identity_ids, list_projects, list_project_groups
)


def data():
    return {"schema": SCHEMA, "records": [
        {"provider": "GitHub", "kind": "project", "stable_id": "repo:55",
         "name": "SOL", "source_ref": "github://owner/SOL", "observed_at": "2026-10-16T00:00:00Z",
         "revision": "a1"},
        {"provider": "GoogleDrive", "kind": "project_candidate", "stable_id": "folder:88",
         "name": "SOL", "source_ref": "drive://folder/88", "observed_at": "2026-10-16T00:00:00Z",
         "revision": "r1"},
        {"provider": "GitHub", "kind": "group", "stable_id": "tree:12",
         "name": "CONFIG_SOL", "parent_id": "repo:55",
         "source_ref": "github://owner/SOL/tree/main/CONFIG_SOL",
         "observed_at": "2026-10-16T00:01:00Z", "revision": "a1"},
        {"provider": "GitHub", "kind": "project", "stable_id": "repo:55",
         "name": "SOL", "source_ref": "github://owner/SOL",
         "observed_at": "2026-10-16T00:02:00Z", "revision": "a2"}
    ]}


class CoreTests(unittest.TestCase):
    def test_do_not_merge_same_name_different_provider(self):
        found = list_projects(data())
        self.assertEqual(len(found), 3)
        self.assertEqual(len({(x["provider"], x["stable_id"]) for x in found}), 2)
        self.assertEqual(found[1]["kind"], "project_candidate")

    def test_group_parent_exact_and_scoped(self):
        self.assertEqual(len(list_project_groups(data(), provider="GitHub", project_id="repo:55")), 1)
        self.assertEqual(list_project_groups(data(), provider="GoogleDrive", project_id="repo:55"), [])

    def test_no_name_as_identity(self):
        state = get_identity_ids(data(), name="SOL")
        self.assertEqual(state["state"], "CANDIDATES_NEED_ID_CONFIRMATION")

    def test_revision_history_retained(self):
        state = get_identity_ids(data(), provider="GitHub", stable_id="repo:55")
        self.assertEqual(state["state"], "HISTORY_MULTIPLE_REVISIONS")
        self.assertEqual(len(state["records"]), 2)

    def test_no_claim_of_truth(self):
        state = get_identity_ids(data(), provider="GoogleDrive", stable_id="folder:88")
        self.assertTrue(state["raw_source_is_not_truth"])
        self.assertEqual(state["state"], "SCOPED_ID_OBSERVED_NOT_TRUTH_VERIFIED")

    def test_no_source_no_identity(self):
        v = data()
        v["records"][0].pop("source_ref")
        with self.assertRaises(ValueError):
            list_projects(v)

    def test_unknown_id_remains_unobserved(self):
        self.assertEqual(get_identity_ids(data(), stable_id="absent")["state"], "NO_OBSERVATION")


if __name__ == "__main__":
    unittest.main()
