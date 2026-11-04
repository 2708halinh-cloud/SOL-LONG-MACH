import unittest

from runtime.tesseract_snn.region_index import RegionDescriptor, RegionIndex
from runtime.tesseract_snn.sparse_router import SparseRegionRouter
from runtime.tesseract_snn.core import EnergyCluster, Neuron, SNNEngine


class SparseRegionRouterTests(unittest.TestCase):
    def setUp(self):
        self.index = RegionIndex([
            RegionDescriptor("library://tools/MCP/a@r1", "ITEM-001#auth",
                             {"domain": ("MCP",), "function": ("read",)}),
            RegionDescriptor("library://tools/Plugins/b@r1", "ITEM-002#mail",
                             {"domain": ("Plugins",), "function": ("email",)}),
            RegionDescriptor("library://tools/Skills/c@r1", "ITEM-003#review",
                             {"domain": ("Kỹ năng",), "function": ("review",)}),
        ])
        self.engine = SNNEngine(
            [Neuron(threshold=1, leak=1) for _ in range(3)],
            [],
            [EnergyCluster(energy=1.0, neuron_ids=(0, 1, 2))],
            energy_per_spike=0.1,
        )
        self.router = SparseRegionRouter(
            self.index, self.engine,
            {"ITEM-001#auth": 0, "ITEM-002#mail": 1, "ITEM-003#review": 2},
        )

    def test_matching_region_is_the_only_neuron_stimulated(self):
        candidates = self.router.route({"domain": "MCP", "function": "read"})
        self.assertEqual([x.region_ref for x in candidates], ["ITEM-001#auth"])
        self.assertEqual(self.engine.step(), [0])
        self.assertEqual(self.router.fired_regions([0]), ["ITEM-001#auth"])
        self.assertEqual(self.engine.neurons[1].membrane, 0)
        self.assertEqual(self.engine.neurons[2].membrane, 0)

    def test_empty_query_is_rejected_instead_of_enumerating_library(self):
        with self.assertRaises(ValueError):
            self.router.route({})

    def test_unmapped_candidate_is_not_silently_ignored(self):
        router = SparseRegionRouter(self.index, self.engine, {"ITEM-001#auth": 0})
        with self.assertRaises(KeyError):
            router.route({"domain": "Plugins", "function": "email"})

    def test_invalid_stimulus_is_rejected_before_queueing(self):
        with self.assertRaises(ValueError):
            self.router.route({"domain": "MCP"}, stimulus=float("nan"))


if __name__ == "__main__":
    unittest.main()
