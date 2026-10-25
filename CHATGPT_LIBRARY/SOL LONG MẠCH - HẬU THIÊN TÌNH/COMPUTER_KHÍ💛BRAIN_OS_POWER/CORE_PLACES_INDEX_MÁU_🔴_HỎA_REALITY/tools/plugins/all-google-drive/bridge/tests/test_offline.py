"""Offline contract checks. Real Google OAuth/provider calls require user credentials and network."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from bridge.accounts import AccountVault
from bridge.drive_ops import DriveController, text_from_docs


class FakeKeyring:
    def __init__(self): self.items = {}
    def set_password(self, service, alias, value): self.items[(service, alias)] = value
    def get_password(self, service, alias): return self.items.get((service, alias))
    def delete_password(self, service, alias): del self.items[(service, alias)]


class TestVault(unittest.TestCase):
    def test_alias_sanitization(self):
        self.assertEqual(AccountVault.check_alias("office.2"), "office.2")
        for bad in ["../../creds", "two accounts", "", "../x", "#x", "a" * 65]:
            with self.assertRaises(ValueError): AccountVault.check_alias(bad)

    def test_non_secret_registry_and_remove(self):
        with tempfile.TemporaryDirectory() as root:
            vault = AccountVault(Path(root), FakeKeyring())
            vault._write_registry({"one": {"email": "user@example.test"}})
            vault.secrets.set_password("all-google-drive-oauth-v1", "one", "SECRET_TOKEN")
            self.assertNotIn("SECRET_TOKEN", vault.path.read_text())
            self.assertIn("one", vault.list_accounts())
            vault.remove("one")
            self.assertEqual(vault.list_accounts(), {})
            self.assertIsNone(vault.secrets.get_password("all-google-drive-oauth-v1", "one"))


class FakeDrive(DriveController):
    def __init__(self, vault, audit_path):
        self.vault = vault
        self.audit_path = audit_path
        self.invocations = []
    def list_files(self, alias, q="trashed = false", page_token=None, page_size=100):
        self.invocations.append((alias, q, page_token))
        if "'root'" in q and not page_token:
            return {"files": [{"id": "fileA", "name": "A", "mimeType": "text/plain"}], "nextPageToken": "page2"}
        if "'root'" in q and page_token == "page2":
            return {"files": [{"id": "sub", "name": "Sub", "mimeType": "application/vnd.google-apps.folder"}]}
        if "'sub'" in q:
            return {"files": [{"id": "fileB", "name": "B", "mimeType": "text/plain"}]}
        return {"files": []}


class TestBridge(unittest.TestCase):
    def test_docs_table_and_text(self):
        items = [{"paragraph": {"elements": [{"textRun": {"content": "Hi\n"}}]}}, {"table": {"tableRows": [{"tableCells": [{"content": [{"paragraph": {"elements": [{"textRun": {"content": "Cell"}}]}}]}]}]}}]
        self.assertIn("Hi\n", text_from_docs(items))
        self.assertIn("Cell", text_from_docs(items))

    def test_inventory_follows_all_pages_and_recursion(self):
        with tempfile.TemporaryDirectory() as root:
            d = FakeDrive(AccountVault(Path(root), FakeKeyring()), Path(root) / "audit.jsonl")
            result = d.folder_inventory("one", "root", recursive=True)
            self.assertEqual(result["total"], 3)
            self.assertEqual({x["id"] for x in result["entries"]}, {"fileA", "sub", "fileB"})
            self.assertIn(("one", "'root' in parents and trashed = false", "page2"), d.invocations)

    def test_audit_hash_chain(self):
        with tempfile.TemporaryDirectory() as root:
            d = FakeDrive(AccountVault(Path(root), FakeKeyring()), Path(root) / "audit.jsonl")
            d.audit("create", "one", "p", {"id": "one"})
            d.audit("rename", "one", "one", {"id": "one", "name": "N"})
            a, b = [json.loads(x) for x in d.audit_path.read_text().splitlines()]
            self.assertEqual(b["previous_hash"], a["hash"])
            self.assertNotEqual(a["hash"], b["hash"])
            self.assertNotIn("token", b)


if __name__ == "__main__":
    unittest.main()
