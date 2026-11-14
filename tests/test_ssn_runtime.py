import unittest
from time import monotonic
from runtime.ssn_npu import LIFConfig,NeuronSpec,SSNNeuron,SynapticMatrix,SSNNetwork,RuntimePolicy,PipelineConfig,cosine_similarity,run_pipeline

class SSNTests(unittest.TestCase):
    def neuron(self,name="db",threshold=.7,required=(),risk="read_only"):
        return SSNNeuron(NeuronSpec(name,"read database",(1.,0.),tuple(required),"cap.db","source://db",risk),LIFConfig(threshold=threshold,tau_seconds=2))
    def test_cosine_zero_and_dimension(self):
        self.assertEqual(cosine_similarity((0.,),(1.,)),0.)
        self.assertEqual(cosine_similarity((1.,),(1.,2.)),0.)
        self.assertAlmostEqual(cosine_similarity((1.,0.),(1.,0.)),1.)
    def test_lif_exponential_leak(self):
        n=self.neuron(); t=monotonic(); n.stimulate((1.,0.),now=t)
        self.assertAlmostEqual(n.decay(t+2),0.36787944117144233,places=6)
    def test_task_boundary_resets_charge(self):
        n=self.neuron(); n.stimulate((1.,0.)); n.reset_context(); self.assertEqual(n.potential,0.)
    def test_spike_is_not_authorization(self):
        n=self.neuron(threshold=.5); net=SSNNetwork([n]); calls=[]
        net.bind_action("db",lambda _:calls.append(1)); n.stimulate((1.,0.),now=5)
        out=net.dispatch({},RuntimePolicy(allow_execution=False),now=5)
        self.assertEqual(out[0].status,"PROPOSED"); self.assertEqual(calls,[])
    def test_required_fields_gate_action(self):
        n=self.neuron(threshold=.5,required=("customer_id",)); net=SSNNetwork([n])
        net.bind_action("db",lambda _: "bad"); n.stimulate((1.,0.),now=5)
        out=net.dispatch({},RuntimePolicy(allow_execution=True),now=5)
        self.assertEqual(out[0].status,"BLOCKED"); self.assertIn("customer_id",out[0].reason)
    def test_allowed_read_action(self):
        n=self.neuron(threshold=.5); net=SSNNetwork([n]); net.bind_action("db",lambda _:{"rows":3})
        n.stimulate((1.,0.),now=5); out=net.dispatch({},RuntimePolicy(allow_execution=True),now=5)
        self.assertEqual(out[0].status,"EXECUTED"); self.assertEqual(out[0].output,{"rows":3})
        self.assertEqual(n.potential,0.)
    def test_sparse_matrix_hundreds_of_edges(self):
        m=SynapticMatrix()
        for i in range(300): m.connect(f"n{i}",f"n{(i+1)%300}",.4)
        self.assertEqual(m.edge_count,300); self.assertAlmostEqual(m.hebbian_update("n0","n1",.1,1,1),.5)
        with self.assertRaises(ValueError): m.hebbian_update("n0","n1",.5,1,1)
    def test_pipeline_reports_cpu_and_proposal(self):
        n=self.neuron(threshold=.5); net=SSNNetwork([n])
        out=run_pipeline("lookup",lambda _:(1.,0.),net,{},RuntimePolicy(),now=10)
        self.assertEqual(out["backend"],"python_cpu_reference")
        self.assertEqual(out["results"][0]["status"],"PROPOSED")
    def test_config_refuses_overclock(self):
        with self.assertRaises(ValueError): PipelineConfig(allow_overclock=True)
        with self.assertRaises(ValueError): PipelineConfig(memory_high_watermark=.99)

if __name__=="__main__": unittest.main()
