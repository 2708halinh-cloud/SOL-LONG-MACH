import unittest

from runtime.tesseract_snn.region_index import RegionDescriptor, RegionIndex


class RegionIndexTests(unittest.TestCase):
    def setUp(self):
        self.index = RegionIndex([
            RegionDescriptor(
                source_ref="library://tools/MCP/tool-a@rev1",
                region_ref="ITEM-001#auth",
                facets={"domain": ("MCP",), "function": ("authentication", "read")},
                relations=("ITEM-004#identity",),
            ),
            RegionDescriptor(
                source_ref="library://tools/Plugins/plugin-b@rev2",
                region_ref="ITEM-002#mail",
                facets={"domain": ("Plugins",), "function": ("email", "write")},
                relations=("ITEM-001#auth",),
            ),
            RegionDescriptor(
                source_ref="library://tools/Skills/skill-c@rev1",
                region_ref="ITEM-003#review",
                facets={"domain": ("Kỹ năng",), "function": ("review", "reasoning")},
            ),
        ])

    def test_exact_multifacet_query_returns_intersection(self):
        hits = self.index.query({"domain": "MCP", "function": "read"})
        self.assertEqual([h.region_ref for h in hits], ["ITEM-001#auth"])

    def test_one_source_can_expose_independent_regions(self):
        index = RegionIndex([
            RegionDescriptor("file://one.md@sha1", "file://one.md@sha1#part-a",
                             {"topic": ("alpha",)}),
            RegionDescriptor("file://one.md@sha1", "file://one.md@sha1#part-b",
                             {"topic": ("beta",)}),
        ])
        self.assertEqual(len(index.query({"topic": "alpha"})), 1)
        self.assertEqual(len(index.query({"topic": "beta"})), 1)

    def test_relation_lookup_does_not_read_source_payload(self):
        related = self.index.related("ITEM-001#auth")
        self.assertEqual([x.region_ref for x in related], ["ITEM-002#mail"])

    def test_source_revision_is_part_of_identity(self):
        with self.assertRaises(ValueError):
            RegionIndex([
                RegionDescriptor("file://a@rev1", "ITEM-1#x", {"topic": ("a",)}),
                RegionDescriptor("file://a@rev2", "ITEM-1#x", {"topic": ("b",)}),
            ])

    def test_unknown_facet_returns_empty(self):
        self.assertEqual(self.index.query({"dimension": "TIME"}), [])

    def test_query_limit_is_bounded(self):
        self.assertEqual(len(self.index.query({}, limit=1)), 1)

    def test_invalid_empty_source_is_rejected(self):
        with self.assertRaises(ValueError):
            RegionDescriptor("", "ITEM-1", {"topic": ("a",)})


if __name__ == "__main__":
    unittest.main()
