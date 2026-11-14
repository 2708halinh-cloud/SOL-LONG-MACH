"""Regression tests: python3 -m unittest discover -s tests -p test_sol_typed_data.py"""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "CHATGPT_LIBRARY" / "SOL LONG MẠCH - HẬU THIÊN TĨNH" / "OS_WORK" / "tools" / "Chuỗi công cụ" / "_Dụng cụ" / "Typed_Data_API" / "typed_data.py"
spec = importlib.util.spec_from_file_location("sol_typed_data", MODULE)
td = importlib.util.module_from_spec(spec)
spec.loader.exec_module(td)

DATA = {"node": {"title": "SOL Long Mạch", "flags": [True, 7]}, "account": {"canonical_url": "https://sol.example/uid/1"}}
class TypedDataContractTest(unittest.TestCase):
    def test_fetch_dict_and_list(self):
        self.assertEqual(td.fetch(DATA, "node.title"), "SOL Long Mạch")
        self.assertTrue(td.fetch(DATA, "node.flags[0]"))
        self.assertEqual(td.fetch(DATA, "node.flags[1]"), 7)
        self.assertEqual(td.fetch(DATA, "node.absent", default="none"), "none")
    def test_filter_pipeline(self):
        self.assertEqual(td.resolve_placeholder(DATA, "{{node.title|lower}}"), "sol long mạch")
        self.assertEqual(td.resolve_placeholder(DATA, "{{account|entity_url}}"), "https://sol.example/uid/1")
        self.assertEqual(td.resolve_placeholder(DATA, "{{node.flags|length}}"), 2)
    def test_preserves_types(self):
        self.assertIs(td.resolve_placeholder(DATA, "{{node.flags[0]}}"), True)
        self.assertEqual(td.resolve_placeholder(DATA, "{{node.flags}}"), [True, 7])
        self.assertEqual(td.resolve_placeholder(DATA, "Tên: {{node.title}}."), "Tên: SOL Long Mạch.")
    def test_denies_untrusted_operations(self):
        for expression in ("{{node.__class__}}", "{{node.title|__import__}}", "{{node.title|nosuch}}", "{{node.title.__class__}}", "{{node.title|lower()}}"):
            with self.subTest(expression=expression):
                with self.assertRaises(td.TypedDataError):
                    td.resolve_placeholder(DATA, expression)
        with self.assertRaises(td.TypedDataError):
            td.fetch(DATA, "node.title.__class__")
        with self.assertRaises(td.TypedDataError):
            td.resolve_placeholder(DATA, "{{node.title")
    def test_url_validation(self):
        with self.assertRaises(td.TypedDataError):
            td.filter_value({"url": "javascript:alert(1)"}, "entity_url")
        with self.assertRaises(td.TypedDataError):
            td.filter_value({"url": "https://user:pass@sol.example"}, "entity_url")
        self.assertEqual(td.filter_value({"url": "/user/1"}, "entity_url"), "/user/1")
    def test_form_widget(self):
        self.assertEqual(td.form_widget("integer", "Tuổi")["step"], 1)
        self.assertEqual(td.form_widget("boolean", "Bật")["widget"], "checkbox")
        with self.assertRaises(td.TypedDataError):
            td.form_widget("arbitrary", "Sai")
    def test_hierarchy_and_cycle(self):
        tree=td.hierarchy(DATA)
        self.assertEqual(tree["items"]["node"]["items"]["flags"]["items"][1], {"type": "integer", "value": 7})
        cyclic={}; cyclic["loop"]=cyclic
        with self.assertRaises(td.TypedDataError):
            td.hierarchy(cyclic)
    def test_no_mutation(self):
        snapshot=repr(DATA)
        td.resolve_placeholder(DATA, "{{node.title|upper}}")
        self.assertEqual(repr(DATA),snapshot)

if __name__ == "__main__":
    unittest.main()
