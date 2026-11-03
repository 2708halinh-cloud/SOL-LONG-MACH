"""TESSERACT CPU reference SNN and runtime primitives."""
from .anapana import AnapanaMonitor, TelemetrySnapshot
from .blackboard import ActiveBlackboard, Register, VersionConflict
from .core import EnergyCluster, Neuron, SNNEngine, Synapse
from .journal import AppendOnlyJournal
from .matrix_ingest import MatrixRuntime, build_matrix_runtime, parse_item_matrix
from .pulse import Pulse, decode_pulse, encode_pulse
from .region_index import RegionDescriptor, RegionIndex
from .resource_guard import DiskGuard, DiskSample, GuardResult
from .sparse_router import SparseRegionRouter

__all__ = [
    "ActiveBlackboard", "AnapanaMonitor", "AppendOnlyJournal", "DiskGuard", "DiskSample",
    "EnergyCluster", "GuardResult", "MatrixRuntime", "Neuron", "Pulse", "Register",
    "RegionDescriptor", "RegionIndex", "SNNEngine", "SparseRegionRouter",
    "TelemetrySnapshot", "Synapse", "VersionConflict", "build_matrix_runtime",
    "decode_pulse", "encode_pulse", "parse_item_matrix",
]
