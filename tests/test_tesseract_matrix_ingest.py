import unittest

from runtime.tesseract_snn.matrix_ingest import (
    build_matrix_runtime,
    parse_item_matrix,
)


FIXTURE = """# MA TRẬN
<!-- BEGIN_ITEM_R-000 -->
ITEM R-000
# R-000 — SỰ THẬT
Nội dung nguồn R-000.
--- END ITEM_R-000 -->
<!-- END_ITEM_R-000 -->
<!-- BEGIN_ITEM_R-001 -->
ITEM R-001
# R-001 — QUAN HỆ
Nội dung nguồn R-001.
RELATED_ITEMS: R-002, R-003
--- END ITEM_R-001 -->
<!-- END_ITEM_R-001 -->
<!-- BEGIN_ITEM_R-002 -->
ITEM R-002
# R-002 — NHẬN DIỆN
Nội dung nguồn R-002.
--- END ITEM_R-002 -->
<!-- END_ITEM_R-002 -->
"""


class MatrixIngestTests(unittest.TestCase):
    def test_parses_one_region_per_explicit_item_boundary(self):
        regions = parse_item_matrix(FIXTURE, source_uri="github://owner/repo/matrix.md", source_sha256="a" * 64)
        self.assertEqual([r.facets["item_id"][0] for r in regions], ["R-000", "R-001", "R-002"])
        self.assertEqual(regions[1].facets["title"][0], "R-001 — QUAN HỆ")

    def test_only_explicit_related_items_become_relations(self):
        regions = parse_item_matrix(FIXTURE, source_uri="github://owner/repo/matrix.md", source_sha256="a" * 64)
        self.assertEqual(regions[1].relations, ("R-002", "R-003"))
        self.assertEqual(regions[2].relations, ())

    def test_source_revision_is_embedded_in_region_locator(self):
        regions = parse_item_matrix(FIXTURE, source_uri="github://owner/repo/matrix.md", source_sha256="a" * 64)
        self.assertIn("@sha256:" + "a" * 64, regions[0].source_ref)
        self.assertTrue(regions[0].region_ref.endswith("#R-000"))

    def test_duplicate_or_unclosed_item_boundary_fails_closed(self):
        duplicate = FIXTURE + FIXTURE.split("<!-- BEGIN_ITEM_R-001 -->", 1)[1].split("<!-- END_ITEM_R-001 -->", 1)[0]
        with self.assertRaises(ValueError):
            parse_item_matrix(duplicate, source_uri="source", source_sha256="a" * 64)
        malformed = FIXTURE.replace("--- END_ITEM_R-002 -->", "")
        with self.assertRaises(ValueError):
            parse_item_matrix(malformed, source_uri="source", source_sha256="a" * 64)

    def test_builds_stable_item_to_neuron_mapping_and_router(self):
        runtime = build_matrix_runtime(
            FIXTURE,
            source_uri="github://owner/repo/matrix.md",
            source_sha256="a" * 64,
        )
        self.assertEqual(len(runtime.region_index), 3)
        self.assertEqual(runtime.neuron_by_item["R-000"], 0)
        self.assertEqual(runtime.neuron_by_item["R-001"], 1)
        hits = runtime.router.route({"item_id": "R-001"})
        self.assertEqual([x.facets["item_id"][0] for x in hits], ["R-001"])
        self.assertEqual(runtime.engine.step(), [1])

    def test_source_text_is_not_copied_into_index_descriptors(self):
        regions = parse_item_matrix(FIXTURE, source_uri="source", source_sha256="a" * 64)
        self.assertFalse(hasattr(regions[0], "content"))
        self.assertFalse(any("Nội dung nguồn" in str(r.facets) for r in regions))


if __name__ == "__main__":
    unittest.main()
