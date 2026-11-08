"""Source-bound SSN/LIF runtime primitives. Semantic activation proposes candidates; it never grants permission to execute side effects."""
from dataclasses import dataclass
from math import exp, sqrt
from time import monotonic
from typing import Callable, Iterable, Mapping, Sequence

Vector = Sequence[float]
Action = Callable[[Mapping[str, object]], object]

def cosine_similarity(a: Vector, b: Vector) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(float(x)*float(y) for x,y in zip(a,b))
    na = sqrt(sum(float(x)**2 for x in a)); nb = sqrt(sum(float(y)**2 for y in b))
    return 0.0 if na == 0 or nb == 0 else max(-1.0, min(1.0, dot/(na*nb)))

@dataclass(frozen=True)
class LIFConfig:
    threshold: float = 0.8
    tau_seconds: float = 4.0
    refractory_seconds: float = 0.05
    reset_potential: float = 0.0
    max_potential: float = 2.0
    def __post_init__(self):
        if self.threshold <= 0 or self.tau_seconds <= 0 or self.refractory_seconds < 0 or self.max_potential < self.threshold:
            raise ValueError("invalid LIF configuration")

@dataclass(frozen=True)
class NeuronSpec:
    name: str
    semantic_signature: str
    signature_vector: Vector
    required_fields: tuple[str,...] = ()
    capability_id: str = ""
    source_ref: str = ""
    risk: str = "read_only"

@dataclass(frozen=True)
class ActionResult:
    neuron: str
    status: str
    output: object = None
    reason: str = ""

class SSNNeuron:
    def __init__(self, spec: NeuronSpec, lif: LIFConfig | None = None):
        self.spec = spec; self.lif = lif or LIFConfig()
        self.potential = 0.0; self.last_update = monotonic()
        self.last_spike = float("-inf"); self.spike_count = 0
    def decay(self, now: float | None = None) -> float:
        now = monotonic() if now is None else now
        dt = max(0.0, now-self.last_update)
        self.potential *= exp(-dt/self.lif.tau_seconds)
        self.last_update = max(self.last_update, now)
        if self.potential < 1e-9: self.potential = 0.0
        return self.potential
    def stimulate(self, vector: Vector, intensity: float = 1.0, now: float | None = None) -> float:
        if intensity < 0: raise ValueError("intensity must be non-negative")
        self.decay(now)
        self.potential = min(self.lif.max_potential, self.potential + max(0.0, cosine_similarity(vector,self.spec.signature_vector))*intensity)
        return self.potential
    def can_spike(self, now: float | None = None) -> bool:
        now = monotonic() if now is None else now
        self.decay(now)
        return self.potential >= self.lif.threshold and now-self.last_spike >= self.lif.refractory_seconds
    def reset_after_spike(self, now: float | None = None):
        now = monotonic() if now is None else now
        self.potential = self.lif.reset_potential; self.last_spike = now
        self.last_update = now; self.spike_count += 1
    def reset_context(self, now: float | None = None):
        self.potential = 0.0; self.last_update = monotonic() if now is None else now

class SynapticMatrix:
    """Sparse weighted adjacency matrix; no dense N×N allocation."""
    def __init__(self): self._weights: dict[str,dict[str,float]] = {}
    def connect(self, source: str, target: str, weight: float):
        if not -1.0 <= weight <= 1.0: raise ValueError("weight must be in [-1,1]")
        self._weights.setdefault(source,{})[target] = weight
    def outgoing(self, source: str) -> Mapping[str,float]: return dict(self._weights.get(source,{}))
    def weight(self, source: str, target: str) -> float: return self._weights.get(source,{}).get(target,0.0)
    @property
    def edge_count(self): return sum(map(len,self._weights.values()))
    def hebbian_update(self, source: str, target: str, learning_rate: float, pre: float, post: float) -> float:
        if not 0 <= learning_rate <= 0.1: raise ValueError("learning_rate must be in [0,0.1]")
        value = max(-1.0,min(1.0,self.weight(source,target)+learning_rate*pre*post))
        self.connect(source,target,value); return value

@dataclass(frozen=True)
class RuntimePolicy:
    allow_execution: bool = False
    allowed_risks: tuple[str,...] = ("read_only",)
    max_actions_per_cycle: int = 8

class SSNNetwork:
    def __init__(self, neurons: Iterable[SSNNeuron], synapses: SynapticMatrix | None = None):
        self.neurons = {n.spec.name:n for n in neurons}
        if not self.neurons: raise ValueError("network requires at least one neuron")
        self.synapses = synapses or SynapticMatrix(); self.actions: dict[str,Action] = {}
    def bind_action(self, name: str, action: Action):
        if name not in self.neurons: raise KeyError(name)
        self.actions[name] = action
    def stimulate_all(self, vector: Vector, intensity: float = 1.0, now: float | None = None):
        return {name:n.stimulate(vector,intensity,now) for name,n in self.neurons.items()}
    def dispatch(self, context: Mapping[str,object], policy: RuntimePolicy | None = None, now: float | None = None):
        policy = policy or RuntimePolicy(); now = monotonic() if now is None else now
        candidates = sorted((n for n in self.neurons.values() if n.can_spike(now)),key=lambda n:n.potential,reverse=True)
        results = []
        for neuron in candidates[:policy.max_actions_per_cycle]:
            spec = neuron.spec
            missing = [k for k in spec.required_fields if k not in context]
            if not policy.allow_execution:
                results.append(ActionResult(spec.name,"PROPOSED",reason="execution_not_authorized")); continue
            if spec.risk not in policy.allowed_risks:
                results.append(ActionResult(spec.name,"BLOCKED",reason="risk_not_allowed")); continue
            if missing:
                results.append(ActionResult(spec.name,"BLOCKED",reason="missing_fields:"+",".join(missing))); continue
            action = self.actions.get(spec.name)
            if action is None:
                results.append(ActionResult(spec.name,"BLOCKED",reason="action_not_bound")); continue
            try:
                output = action(context); results.append(ActionResult(spec.name,"EXECUTED",output=output))
                self._propagate(spec.name,now)
            except Exception as exc:
                results.append(ActionResult(spec.name,"ERROR",reason=type(exc).__name__))
            finally: neuron.reset_after_spike(now)
        return results
    def _propagate(self, source: str, now: float):
        # A spike transmits bounded activation, never execution permission.
        for target,weight in self.synapses.outgoing(source).items():
            if target in self.neurons and weight > 0:
                n=self.neurons[target]; n.decay(now)
                n.potential=min(n.lif.max_potential,n.potential+min(1.0,weight))
    def reset_task_boundary(self, now: float | None = None):
        for n in self.neurons.values(): n.reset_context(now)

def semantic_candidates(neurons: Iterable[SSNNeuron], vector: Vector, limit: int = 10):
    scored=[(n.spec.name,cosine_similarity(vector,n.spec.signature_vector)) for n in neurons]
    return sorted(scored,key=lambda x:x[1],reverse=True)[:max(0,limit)]

@dataclass(frozen=True)
class PipelineConfig:
    max_batch_size: int = 64
    max_parallel_candidates: int = 16
    max_actions_per_cycle: int = 8
    max_context_bytes: int = 1_000_000
    thermal_limit_c: float = 80.0
    memory_high_watermark: float = 0.85
    allow_overclock: bool = False
    def __post_init__(self):
        if self.max_batch_size < 1 or self.max_parallel_candidates < 1: raise ValueError("batch limits must be positive")
        if not 0.1 <= self.memory_high_watermark <= 0.95: raise ValueError("unsafe memory watermark")
        if self.allow_overclock: raise ValueError("overclocking is disabled; use safe throttling")

def run_pipeline(user_text: str, encoder: Callable[[str],Vector], network: SSNNetwork,
                 context: Mapping[str,object], policy: RuntimePolicy | None = None,
                 config: PipelineConfig | None = None, now: float | None = None):
    """Vertex -> Fragment -> Render CPU reference pipeline, not a GPU claim."""
    config=config or PipelineConfig(); vector=encoder(user_text)
    if not vector: return {"status":"OPEN_NO_EMBEDDING","candidates":[],"results":[]}
    activations=network.stimulate_all(vector,now=now)
    ranked=semantic_candidates(network.neurons.values(),vector,config.max_parallel_candidates)
    effective=policy or RuntimePolicy(max_actions_per_cycle=config.max_actions_per_cycle)
    results=network.dispatch(context,effective,now)
    return {
        "status":"OK","pipeline":["VERTEX_INPUT","FRAGMENT_SEMANTIC_FIELD","RENDER_RECEIPT"],
        "candidate_count":len(ranked),
        "candidates":[{"neuron":name,"similarity":round(score,6),"potential":round(activations[name],6)} for name,score in ranked],
        "results":[r.__dict__ for r in results],
        "execution_authorized":effective.allow_execution,"backend":"python_cpu_reference"
    }
