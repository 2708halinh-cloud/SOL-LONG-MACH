"""TESSERACT motherboard kernel: durable re-entry, bounded scheduling, tool observation and regression.

This is a local runtime component. It does not claim to intercept tools that are not wrapped
or to prove remote-provider health without fresh evidence.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

SCHEMA = "TESSERACT_MOTHERBOARD_KERNEL/1.0"
WAVE_BANDS = ("ALPHA", "BETA", "GAMMA", "DELTA", "THETA")
CANONICAL_WAVE_CYCLE = ("ALPHA", "BETA", "DELTA", "THETA", "GAMMA")
SECRET_MARKERS = ("token", "secret", "password", "cookie", "credential", "authorization", "api_key", "private_key")
BRAIN_LABELS = {
    "UBUBU": {"brain_id": "BRAIN-UBUBU", "canonical_label": "UBUBU", "provenance": "EXACT_LABEL_REQUIRED"},
    "UNTUNBU": {"brain_id": "BRAIN-UNTUNBU", "canonical_label": "UNTUNBU", "provenance": "EXACT_LABEL_REQUIRED"},
}


def _safe(value: Any, key: str = "") -> Any:
    """Return JSON-safe, secret-redacted evidence."""
    if any(marker in key.lower() for marker in SECRET_MARKERS):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(k): _safe(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(v) for v in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


def resolve_brain_label(label: str) -> dict[str, str]:
    """Resolve only exact brain labels; similar spellings are not aliases."""
    key = str(label).strip().upper()
    if key not in BRAIN_LABELS:
        raise ValueError(f"unknown or ambiguous brain label: {label!r}")
    return dict(BRAIN_LABELS[key])


def compare_capability_regression(previous: Iterable[str], current: Iterable[str]) -> dict[str, Any]:
    old = set(previous)
    new = set(current)
    preserved = sorted(old & new)
    missing = sorted(old - new)
    added = sorted(new - old)
    return {
        "preserved": preserved,
        "missing": missing,
        "added": added,
        "regression_pass": not missing,
        "status": "PASS" if not missing else "REGRESSION_DETECTED",
    }


def inspect_process(pid: int | None, heartbeat_path: str | Path | None,
                    max_age_seconds: float = 60.0, now_epoch: float | None = None) -> dict[str, Any]:
    """Probe process existence and heartbeat freshness independently."""
    now = time.time() if now_epoch is None else float(now_epoch)
    if not isinstance(pid, int) or pid <= 0:
        alive = False
        pid_state = "PID_UNRESOLVED"
    else:
        try:
            if os.name == "nt":
                probe = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                    capture_output=True, text=True, timeout=2, check=False,
                )
                alive = probe.returncode == 0 and str(pid) in probe.stdout
                pid_state = "PROCESS_PRESENT" if alive else "PROCESS_ABSENT_OR_UNRESOLVED"
            else:
                os.kill(pid, 0)
                alive, pid_state = True, "PROCESS_PRESENT"
        except PermissionError:
            alive, pid_state = True, "PROCESS_PRESENT_PERMISSION_LIMITED"
        except (ProcessLookupError, OSError, subprocess.TimeoutExpired):
            alive, pid_state = False, "PROCESS_ABSENT_OR_UNRESOLVED"

    heartbeat_epoch = None
    heartbeat_fresh = False
    heartbeat_state = "HEARTBEAT_UNAVAILABLE"
    if heartbeat_path is not None:
        try:
            data = json.loads(Path(heartbeat_path).read_text(encoding="utf-8"))
            heartbeat_epoch = float(data["observed_at_epoch"])
            age = max(0.0, now - heartbeat_epoch)
            heartbeat_fresh = age <= max_age_seconds
            heartbeat_state = "FRESH" if heartbeat_fresh else "STALE"
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            heartbeat_state = "HEARTBEAT_INVALID_OR_MISSING"

    if not alive:
        state = "NOT_RUNNING"
    elif not heartbeat_fresh:
        state = "STALE_HEARTBEAT"
    else:
        state = "RUNNING_VERIFIED"
    return {
        "pid": pid,
        "process_alive": alive,
        "pid_state": pid_state,
        "heartbeat_path": str(heartbeat_path) if heartbeat_path is not None else None,
        "heartbeat_epoch": heartbeat_epoch,
        "heartbeat_fresh": heartbeat_fresh,
        "heartbeat_state": heartbeat_state,
        "state": state,
        "observed_at_epoch": now,
    }


class MotherboardKernel:
    """Small durable motherboard coordinator with evidence-first state transitions."""

    def __init__(self, root: str | Path, clock: Callable[[], float] = time.time):
        self.root = Path(root)
        self.checkpoint_path = self.root / "state" / "tesseract_motherboard_checkpoint.json"
        self.journal_path = self.root / "journal" / "brainwaves.jsonl"
        self.weights_path = self.root / "state" / "neuron_weights.json"
        self.clock = clock
        self._state: dict[str, Any] = self._empty_state()
        self._weights: dict[str, dict[str, Any]] = {}
        self._seen_causal_ids: set[str] = set()
        self._load_weights()
        self.restore()

    @staticmethod
    def _empty_state() -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "state_n": 0,
            "state_n_plus_1": 0,
            "objective_id": None,
            "edges": [],
            "unfinished_edges": [],
            "last_event_id": None,
            "brain_labels": {k: dict(v) for k, v in BRAIN_LABELS.items()},
            "tool_observations": 0,
            "last_wave_band": None,
            "updated_at_epoch": None,
        }

    def _atomic_json(self, path: Path, value: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def _save(self) -> None:
        self._state["updated_at_epoch"] = self.clock()
        self._atomic_json(self.checkpoint_path, self._state)

    def restore(self) -> dict[str, Any]:
        """Restore durable checkpoint at every new kernel/process initialization."""
        if self.checkpoint_path.exists():
            loaded = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            if loaded.get("schema") != SCHEMA:
                raise ValueError("unsupported motherboard checkpoint schema")
            self._state = loaded
            self._seen_causal_ids = set(loaded.get("seen_causal_ids", []))
        else:
            self._state = self._empty_state()
            self._save()
        return json.loads(json.dumps(self._state))

    def set_objective(self, objective_id: str, edge_ids: Iterable[str]) -> dict[str, Any]:
        if not objective_id.strip():
            raise ValueError("objective_id is required")
        edges = [{"edge_id": str(edge), "state": "OPEN", "receipt": None, "readback": None}
                 for edge in edge_ids]
        self._state["objective_id"] = objective_id
        self._state["edges"] = edges
        self._state["unfinished_edges"] = [e["edge_id"] for e in edges]
        self._save()
        return json.loads(json.dumps(self._state))

    def complete_edge(self, edge_id: str, *, receipt: Mapping[str, Any],
                      readback: Mapping[str, Any]) -> dict[str, Any]:
        if not receipt or not readback or readback.get("verified") is not True:
            raise ValueError("edge completion requires a receipt and verified exact-target readback")
        edge = next((e for e in self._state["edges"] if e["edge_id"] == edge_id), None)
        if edge is None:
            raise KeyError(edge_id)
        edge.update({"state": "DONE", "receipt": _safe(receipt), "readback": _safe(readback)})
        self._state["unfinished_edges"] = [e["edge_id"] for e in self._state["edges"] if e["state"] != "DONE"]
        self._state["state_n"] = int(self._state.get("state_n_plus_1", 0))
        self._state["state_n_plus_1"] = self._state["state_n"] + 1
        self._save()
        return json.loads(json.dumps(self._state))

    def schedule(self, tasks: Iterable[Mapping[str, Any]], *, cpu_budget_ms: float,
                 memory_budget_mb: float, time_budget_ms: float) -> dict[str, Any]:
        """Greedy bounded dispatcher; deferred work remains explicit and resumable."""
        started = time.monotonic()
        selected, deferred = [], []
        cpu_used = memory_used = 0.0
        for raw in tasks:
            task = dict(raw)
            cpu = max(0.0, float(task.get("cpu_ms", 0)))
            memory = max(0.0, float(task.get("memory_mb", 0)))
            time_elapsed_ms = (time.monotonic() - started) * 1000
            fits = (cpu_used + cpu <= cpu_budget_ms and
                    memory_used + memory <= memory_budget_mb and
                    time_elapsed_ms + cpu <= time_budget_ms)
            if fits:
                selected.append(task)
                cpu_used += cpu
                memory_used += memory
            else:
                deferred.append(task)
        return {
            "selected": selected, "deferred": deferred,
            "budget": {"cpu_ms": cpu_budget_ms, "memory_mb": memory_budget_mb, "time_ms": time_budget_ms},
            "used": {"cpu_ms": cpu_used, "memory_mb": memory_used,
                     "elapsed_ms": (time.monotonic() - started) * 1000},
            "unfinished_count": len(deferred),
        }

    def observe_tool(self, *, tool_name: str, action: Mapping[str, Any],
                     provider_receipt: Mapping[str, Any] | None = None,
                     consequence: Mapping[str, Any] | None = None,
                     readback: Mapping[str, Any] | None = None,
                     causal_id: str | None = None,
                     wave_band: str | None = None) -> dict[str, Any]:
        """Append one sanitized observation; missing receipt/readback stays explicitly open."""
        causal = causal_id or f"{tool_name}:{self.clock():.6f}:{self._state['tool_observations']}"
        duplicate = causal in self._seen_causal_ids
        band = wave_band or CANONICAL_WAVE_CYCLE[self._state["tool_observations"] % len(CANONICAL_WAVE_CYCLE)]
        if band not in WAVE_BANDS:
            raise ValueError(f"unknown wave band: {band}")
        if duplicate:
            verification = "COALESCED_DUPLICATE"
        elif readback is None or readback.get("verified") is not True:
            verification = "OPEN_READBACK"
        elif not provider_receipt:
            verification = "OPEN_RECEIPT"
        elif consequence is None:
            verification = "OPEN_CONSEQUENCE"
        else:
            verification = "VERIFIED_EVIDENCE_CHAIN"
        event = {
            "schema": "TESSERACT_BRAINWAVE_EVENT/1.0",
            "event_id": f"TBK-{self._state['tool_observations'] + 1:08d}",
            "causal_id": causal,
            "observed_at_epoch": self.clock(),
            "tool_name": tool_name,
            "action": _safe(action),
            "provider_receipt": _safe(provider_receipt),
            "consequence": _safe(consequence),
            "readback": _safe(readback),
            "wave_band": band,
            "wave_cycle": list(CANONICAL_WAVE_CYCLE),
            "verification_state": verification,
            "duplicate_causal_event": duplicate,
            "state_n": self._state["state_n"],
            "state_n_plus_1": self._state["state_n_plus_1"],
        }
        score_progress = 1.0 if verification == "VERIFIED_EVIDENCE_CHAIN" else (0.1 if consequence else 0.0)
        score_novelty = 0.0 if duplicate else (0.8 if tool_name not in self._weights else 0.4)
        duration = float(consequence.get("duration_seconds", 0.0)) if isinstance(consequence, Mapping) else 0.0
        score_efficiency = min(1.0, 1.0 / (1.0 + max(0.0, duration))) if consequence else 0.2
        score_risk = 0.1 if verification == "VERIFIED_EVIDENCE_CHAIN" else (0.8 if verification == "OPEN_READBACK" else 0.6)
        score = self.update_neuron_weights(
            tool_name, category=str(action.get("kind", "TOOL")) if isinstance(action, Mapping) else "TOOL",
            progress=score_progress, novelty=score_novelty, efficiency=score_efficiency,
            risk=score_risk, repetition=1.0 if duplicate else 0.0, evidence_ref=causal,
        )
        event["neuron_scoring"] = {
            "weights": score["weights"], "reward": score["reward"],
            "evidence_ref": score["evidence_ref"],
            "weight_semantics": score["weight_semantics"],
        }
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        with self.journal_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        if not duplicate:
            self._seen_causal_ids.add(causal)
        self._state["seen_causal_ids"] = sorted(self._seen_causal_ids)
        self._state["tool_observations"] += 1
        self._state["last_event_id"] = event["event_id"]
        self._state["last_wave_band"] = band
        self._save()
        return event

    def wrap_tool(self, tool_name: str, tool_callable: Callable[..., Any],
                  readback: Callable[[Any], Mapping[str, Any] | None] | None = None) -> Callable[..., Any]:
        """Wrap a callable neuron/tool so calls through this adapter are journaled."""
        @wraps(tool_callable)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            started = self.clock()
            try:
                result = tool_callable(*args, **kwargs)
                receipt = {"wrapper": "tesseract_motherboard_kernel", "returned": True}
                consequence = {"result_type": type(result).__name__, "duration_seconds": max(0.0, self.clock() - started)}
                rb = readback(result) if readback else None
                self.observe_tool(tool_name=tool_name,
                                  action={"kind": "CALL", "argument_count": len(args) + len(kwargs)},
                                  provider_receipt=receipt, consequence=consequence, readback=rb)
                return result
            except Exception as exc:
                self.observe_tool(tool_name=tool_name,
                                  action={"kind": "CALL", "argument_count": len(args) + len(kwargs)},
                                  provider_receipt={"wrapper": "tesseract_motherboard_kernel", "returned": False},
                                  consequence={"exception_type": type(exc).__name__},
                                  readback=None)
                raise
        return wrapped

    def update_neuron_weights(self, neuron_id: str, *, category: str, progress: float,
                              novelty: float, efficiency: float, risk: float, repetition: float,
                              evidence_ref: str) -> dict[str, Any]:
        """Generate event-conditioned heuristic weights; this is not a learned neural model."""
        if not evidence_ref.strip():
            raise ValueError("evidence_ref is required for weight updates")
        values = {k: min(1.0, max(0.0, float(v))) for k, v in {
            "progress": progress, "novelty": novelty, "efficiency": efficiency,
            "risk": risk, "repetition": repetition}.items()}
        weights = {
            "progress": round(0.2 + 0.5 * values["progress"], 6),
            "novelty": round(0.1 + 0.4 * values["novelty"], 6),
            "efficiency": round(0.1 + 0.4 * values["efficiency"], 6),
            "risk": round(0.3 + 0.7 * values["risk"], 6),
            "repetition": round(0.3 + 0.7 * values["repetition"], 6),
        }
        reward = (weights["progress"] * values["progress"] +
                  weights["novelty"] * values["novelty"] +
                  weights["efficiency"] * values["efficiency"] -
                  weights["risk"] * values["risk"] -
                  weights["repetition"] * values["repetition"])
        item = {
            "neuron_id": neuron_id, "category": category, "weights": weights,
            "inputs": values, "reward": round(reward, 6),
            "evidence_ref": evidence_ref, "updated_at_epoch": self.clock(),
            "weight_semantics": "EVENT_CONDITIONED_HEURISTIC_NOT_MODEL_WEIGHTS",
        }
        self._weights[neuron_id] = item
        self._atomic_json(self.weights_path, self._weights)
        return json.loads(json.dumps(item))

    def run_cycle(self, heartbeat_path: str | Path | None = None) -> dict[str, Any]:
        """Run one bounded re-entry cycle; never equate an open edge with completion."""
        state = self.restore()
        heartbeat = Path(heartbeat_path) if heartbeat_path is not None else self.root / "state" / "heartbeat.json"
        capability_regression = None
        manifest_path = self.root.parent / "config" / "TESSERACT_MOTHERBOARD_CAPABILITIES_CURRENT.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            capability_regression = self.reconcile_capabilities(
                manifest.get("current_capabilities", []),
                previous_capabilities=manifest.get("baseline_capabilities", []),
                snapshot_path=self.root / "state" / "capability_regression_current.json",
            )
        pulse = write_heartbeat(heartbeat, process_id=os.getpid(), clock=self.clock)
        monitor = inspect_process(os.getpid(), heartbeat, max_age_seconds=60.0, now_epoch=self.clock())
        unfinished = list(state.get("unfinished_edges", []))
        loop_state = "CONTINUE_OPEN_EDGES" if unfinished else "WAIT_RECEPTIVE"
        cycle = {
            "schema": "TESSERACT_MOTHERBOARD_LOOP_CYCLE/1.0",
            "cycle_id": f"TBKC-{os.getpid()}-{int(self.clock() * 1000000)}",
            "observed_at_epoch": self.clock(),
            "pid": os.getpid(),
            "loop_state": loop_state,
            "objective_id": state.get("objective_id"),
            "unfinished_edges": unfinished,
            "state_n": state.get("state_n", 0),
            "state_n_plus_1": state.get("state_n_plus_1", 0),
            "heartbeat": pulse,
            "monitor": monitor,
            "action_policy": "NO_UNREGISTERED_ACTION_EXECUTION",
            "capability_regression": capability_regression,
        }
        path = self.root / "state" / "loop_cycles.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(cycle, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return cycle
    def reconcile_capabilities(self, current_capabilities: Iterable[str],
                               previous_capabilities: Iterable[str] | None = None,
                               snapshot_path: str | Path | None = None) -> dict[str, Any]:
        """Run 5D capability regression and retain the historical union without flattening history."""
        path = Path(snapshot_path) if snapshot_path is not None else self.root / "state" / "capability_regression_current.json"
        current = sorted(set(str(x) for x in current_capabilities))
        previous = sorted(set(str(x) for x in previous_capabilities or []))
        historical = set(previous)
        if path.exists():
            prior = json.loads(path.read_text(encoding="utf-8"))
            previous = sorted(set(prior.get("current_capabilities", [])))
            historical.update(prior.get("historical_union", []))
            historical.update(previous)
        comparison = compare_capability_regression(previous, current)
        historical.update(current)
        record = {
            "schema": "TESSERACT_5D_CAPABILITY_REGRESSION/1.0",
            "observed_at_epoch": self.clock(),
            "previous_capabilities": previous,
            "current_capabilities": current,
            "preserved": comparison["preserved"],
            "missing": comparison["missing"],
            "added": comparison["added"],
            "regression_pass": comparison["regression_pass"],
            "status": comparison["status"],
            "historical_union": sorted(historical),
            "runtime_truth": "CAPABILITY_INVENTORY_COMPARISON_NOT_PROVIDER_HEALTH_PROOF",
        }
        self._atomic_json(path, record)
        return json.loads(json.dumps(record))
    def _load_weights(self) -> None:
        if self.weights_path.exists():
            loaded = json.loads(self.weights_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self._weights = loaded


def write_heartbeat(path: str | Path, *, process_id: int | None = None,
                    clock: Callable[[], float] = time.time) -> dict[str, Any]:
    """Write an explicit heartbeat for the process that owns this call."""
    payload = {"observed_at_epoch": clock(), "pid": process_id or os.getpid(),
               "source": "TESSERACT_MOTHERBOARD_KERNEL"}
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, target)
    return payload