"""TESSERACT 6D CPU profile scheduler; not hardware emulation."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
REGISTRY_PATH = Path(__file__).resolve().parents[1] / "config" / "INTEL_CORE_ULTRA_PROFILES.json"
@dataclass(frozen=True)
class CpuProfile:
    model: str
    cores: int
    reported_max_turbo_ghz: float
    smart_cache_mb: int
    integrated_gpu: str | None
    source_verified: bool
    @property
    def virtual_worker_slots(self) -> int:
        return self.cores
    @property
    def cache_budget_bytes(self) -> int:
        return self.smart_cache_mb * 1024 * 1024
def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("component") != "TESSERACT_6D_INTEL_CORE_ULTRA_SOFTWARE_EMULATION":
        raise ValueError("Unexpected CPU profile registry component")
    rows = data.get("profiles")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Registry must contain profiles")
    seen: set[str] = set()
    for row in rows:
        for field in ("model", "cores", "reported_max_turbo_ghz", "smart_cache_mb", "integrated_gpu", "source_verified"):
            if field not in row:
                raise ValueError(f"Profile missing field: {field}")
        if row["model"] in seen:
            raise ValueError(f"Duplicate CPU model: {row['model']}")
        seen.add(row["model"])
        if not isinstance(row["cores"], int) or row["cores"] <= 0:
            raise ValueError(f"Invalid core count: {row['model']}")
        if row["smart_cache_mb"] <= 0 or row["reported_max_turbo_ghz"] <= 0:
            raise ValueError(f"Invalid cache/frequency: {row['model']}")
    return data
def get_profile(model: str, path: Path = REGISTRY_PATH) -> CpuProfile:
    for row in load_registry(path)["profiles"]:
        if row["model"].casefold() == model.casefold():
            return CpuProfile(row["model"], row["cores"], row["reported_max_turbo_ghz"], row["smart_cache_mb"], row["integrated_gpu"], row["source_verified"])
    raise KeyError(f"CPU profile not found: {model}")
def plan_task_slots(model: str, task_count: int, path: Path = REGISTRY_PATH) -> dict[str, Any]:
    if task_count < 0:
        raise ValueError("task_count cannot be negative")
    p = get_profile(model, path)
    return {"model":p.model,"requested_tasks":task_count,"virtual_worker_slots":p.virtual_worker_slots,"planned_concurrent_tasks":min(task_count,p.virtual_worker_slots),"queued_tasks":max(0,task_count-p.virtual_worker_slots),"cache_budget_bytes":p.cache_budget_bytes,"integrated_gpu_profile":p.integrated_gpu,"gpu_execution_enabled":False,"hardware_equivalence_claim":False,"profile_source_verified":p.source_verified}
