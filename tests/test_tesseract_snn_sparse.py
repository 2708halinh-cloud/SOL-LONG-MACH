import unittest

from runtime.tesseract_snn.core import EnergyCluster, Neuron, SNNEngine, Synapse


class NoIterationList(list):
    """A sequence that allows indexed access but rejects full-population scans."""

    def __iter__(self):
        raise AssertionError("scheduler performed a full collection scan")


class SparseSchedulerTests(unittest.TestCase):
    def test_step_does_not_iterate_the_full_neuron_population(self):
        neurons = [Neuron(threshold=1, leak=1) for _ in range(128)]
        engine = SNNEngine(
            neurons,
            [],
            [EnergyCluster(energy=1.0, neuron_ids=tuple(range(128)))],
            energy_per_spike=0.1,
        )
        engine.neurons = NoIterationList(engine.neurons)
        engine.inject(37, 1.0)

        self.assertEqual(engine.step(), [37])

    def test_spike_propagation_does_not_scan_the_full_synapse_population(self):
        neurons = [
            Neuron(threshold=1, leak=1),
            Neuron(threshold=0.5, leak=1),
            Neuron(threshold=1, leak=1),
        ]
        synapses = [
            Synapse(0, 1, 0.75, delay=1),
            Synapse(2, 1, 0.25, delay=1),
        ]
        engine = SNNEngine(
            neurons,
            synapses,
            [EnergyCluster(energy=1.0, neuron_ids=(0, 1, 2))],
            energy_per_spike=0.1,
        )
        engine.synapses = NoIterationList(engine.synapses)
        engine.inject(0, 1.0)

        self.assertEqual(engine.step(), [0])
        self.assertEqual(engine.step(), [1])


if __name__ == "__main__":
    unittest.main()
