"""TESSERACT 6D CPU profile scheduler; resource-profile emulation, not hardware emulation."""
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
    gpu_status: str
    source_verified: bool

    @property
    def virtual_worker_slots(self) -> int:
        """Logical scheduling slots, not a claim about Intel P/E core topology."""
        return self.cores

    @property
    def cache_budget_bytes(self) -> int:
        """A software budget derived from listed cache size; not actual CPU cache."""
        return self.smart_cache_mb * 1024 * 1024

def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("component") != "TESSERACT_6D_INTEL_CORE_ULTRA_SOFTWARE_EMULATION":
        raise ValueError("Unexpected CPU profile registry component")
    profiles = data.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("Registry must contain at least one profile")
    seen: set[str] = set()
    for row in profiles:
        for field in ("model", "cores", "reported_max_turbo_ghz", "smart_cache_mb", "integrated_gpu", "source_verified"):
            if field not in row:
                raise ValueError(f"Profile missing required field: {field}")
        if row["model"] in seen:
            raise ValueError(f"Duplicate CPU model: {row['model']}")
        seen.add(row["model"])
        if not isinstance(row["cores"], int) or row["cores"] <= 0:
            raise ValueError(f"Invalid core count for {row['model']}")
        if row["smart_cache_mb"] <= 0 or row["reported_max_turbo_ghz"] <= 0:
            raise ValueError(f"Invalid cache/frequency for {row['model']}")
        if row["integrated_gpu"] is not None and not isinstance(row["integrated_gpu"], str):
            raise ValueError(f"Invalid integrated GPU label for {row['model']}")
        gpu_status = row.get(
            "gpu_status",
            "USER_PROVIDED" if row["integrated_gpu"] else "NOT_PROVIDED_IN_USER_LIST",
        )
        if gpu_status not in {"USER_PROVIDED", "NOT_PROVIDED_IN_USER_LIST"}:
            raise ValueError(f"Invalid GPU status for {row['model']}")
        if (gpu_status == "USER_PROVIDED") != (row["integrated_gpu"] is not None):
            raise ValueError(f"GPU label/status mismatch for {row['model']}")
    return data

def get_profile(model: str, path: Path = REGISTRY_PATH) -> CpuProfile:
    rows = load_registry(path)["profiles"]
    for row in rows:
        if row["model"].casefold() == model.casefold():
            return CpuProfile(
                model=row["model"], cores=row["cores"],
                reported_max_turbo_ghz=row["reported_max_turbo_ghz"],
                smart_cache_mb=row["smart_cache_mb"],
                integrated_gpu=row["integrated_gpu"],
                gpu_status=row.get(
                    "gpu_status",
                    "USER_PROVIDED" if row["integrated_gpu"] else "NOT_PROVIDED_IN_USER_LIST",
                ),
                source_verified=row["source_verified"],
            )
    raise KeyError(f"CPU profile not found: {model}")

def plan_task_slots(model: str, task_count: int, path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """Produce deterministic worker-slot allocation; does not execute or benchmark tasks."""
    if task_count < 0:
        raise ValueError("task_count cannot be negative")
    profile = get_profile(model, path)
    return {
        "model": profile.model,
        "requested_tasks": task_count,
        "virtual_worker_slots": profile.virtual_worker_slots,
        "planned_concurrent_tasks": min(task_count, profile.virtual_worker_slots),
        "queued_tasks": max(0, task_count - profile.virtual_worker_slots),
        "cache_budget_bytes": profile.cache_budget_bytes,
        "integrated_gpu_profile": profile.integrated_gpu,
        "integrated_gpu_status": profile.gpu_status,
        "gpu_execution_enabled": False,
        "hardware_equivalence_claim": False,
        "profile_source_verified": profile.source_verified,
    }
