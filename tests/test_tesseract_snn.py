import unittest
from runtime.tesseract_snn.core import EnergyCluster, Neuron, SNNEngine, Synapse

class SNNEngineTests(unittest.TestCase):
    def make_engine(self, energy=1.0):
        return SNNEngine([Neuron(threshold=1, leak=1), Neuron(threshold=.5, leak=1)], [Synapse(0, 1, .75, delay=1)], [EnergyCluster(energy, (0, 1))], energy_per_spike=.1)
    def test_event_propagates_with_delay(self):
        e=self.make_engine(); e.inject(0,1)
        self.assertEqual(e.step(),[0]); self.assertEqual(e.step(),[1])
    def test_energy_exhaustion_blocks_spike(self):
        e=self.make_engine(0); e.inject(0,1)
        self.assertEqual(e.step(),[]); self.assertEqual(e.neurons[0].spikes,0)
    def test_tombstone_preserves_slot(self):
        e=self.make_engine(); n=e.neurons[1]; e.tombstone_neuron(0)
        self.assertIs(e.neurons[1],n); self.assertFalse(e.synapses[0].active)
    def test_leapfrog_energy_drift_bounded(self):
        e=self.make_engine(); initial=.5*e.synapses[0].weight**2
        energies=[e.update_hamiltonian_synapse(0,.01) for _ in range(1000)]
        self.assertLess(max(abs(x-initial) for x in energies),.001)
    def test_reject_nan(self):
        e=self.make_engine()
        with self.assertRaises(ValueError): e.inject(0,float("nan"))

if __name__ == "__main__": unittest.main()
