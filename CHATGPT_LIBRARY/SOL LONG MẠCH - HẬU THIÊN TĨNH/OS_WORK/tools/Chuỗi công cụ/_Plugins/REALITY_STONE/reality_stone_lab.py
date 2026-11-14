"""REALITY_STONE controlled adversarial-defence laboratory.

Every input is synthetic, bounded and held in memory. This is NOT a vulnerability
exploit, system hijack, malware, spyware, ransomware or firmware mutation.
The deliberately manipulated samples demonstrate why independent readback helps.
"""
from __future__ import annotations
from hashlib import sha256
from math import log2
from statistics import mean

def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()

def integrity_trial() -> dict:
    trusted = b"allowed_version=1\nmode=read_only\n"
    altered = b"allowed_version=1\nmode=write\n"
    mismatch = _digest(trusted) != _digest(altered)
    return {"scenario": "UNAUTHORIZED_CHANGE_SIMULATION",
            "detected": mismatch, "before_hash": _digest(trusted),
            "after_hash": _digest(altered),
            "files_touched": 0, "actions_executed": 0}

def poisoning_trial() -> dict:
    # A tiny majority-class classifier: 9 clean votes for 'SAFE', 1 for 'RISK'.
    # Synthetic label poisoning flips its prediction; no real model/dataset.
    samples = [("sample", "SAFE")] * 9 + [("sample", "RISK")]
    def vote(items):
        yes = sum(1 for _, label in items if label == "SAFE")
        return "SAFE" if yes >= (len(items) - yes) else "RISK"
    initial = vote(samples)
    # Controlled injected labels ONLY in an in-memory copy.
    poisoned = [(x, "RISK") if i < 6 else (x, label)
                for i, (x, label) in enumerate(samples)]
    changed = vote(poisoned)
    # Trusted set anchored by provenance reveals changed labels.
    changed_labels = sum(a[1] != b[1] for a,b in zip(samples,poisoned))
    return {"scenario": "ADVERSARIAL_ML_LABEL_POISON_SIMULATION",
            "model": "TOY_MAJORITY_VOTE", "clean_prediction": initial,
            "poisoned_prediction": changed, "label_changes": changed_labels,
            "tamper_detected_by_clean_reference": changed_labels > 0,
            "external_dataset_accessed": False, "actions_executed": 0}

def resource_trial() -> dict:
    # No actual consumption. Compare simulated measurements with a baseline.
    baseline = {"cpu_percent": 19, "memory_mb": 220, "bandwidth_mbps": 2}
    suspect = {"cpu_percent": 94, "memory_mb": 1100, "bandwidth_mbps": 86}
    rules = {"cpu_percent": 80, "memory_mb": 800, "bandwidth_mbps": 50}
    alerts = sorted(k for k in rules if suspect[k] > rules[k])
    return {"scenario": "RESOURCE_ABUSE_SIGNAL_SIMULATION",
            "baseline": baseline, "observed_synthetic": suspect,
            "thresholds": rules, "alerts": alerts, "detected": bool(alerts),
            "actual_cpu_burn": False, "actions_executed": 0}

def telemetry_trial() -> dict:
    # Two independently mocked sensor streams. No real camera/mic/radar.
    frame_a = [1.0, 1.2, 1.1, 1.3]
    frame_b = [1.0, 1.2, 9.9, 1.3]  # one forged sample
    discrepancies = [i for i,(a,b) in enumerate(zip(frame_a,frame_b))
                     if abs(a-b) > 0.5]
    return {"scenario": "TELEMETRY_DISCREPANCY_SIMULATION",
            "reference_sensor": "MOCK_SENSOR_A",
            "other_sensor": "MOCK_SENSOR_B",
            "discrepant_samples": discrepancies, "detected": bool(discrepancies),
            "actual_sensor_opened": False, "actions_executed": 0}

def opaque_data_trial() -> dict:
    # Static opaque sample only; no encryption/decryption of user data.
    source = b"event_id=R000,source=synthetic\n"
    opaque = bytes(range(256))
    def entropy(data):
        counts = {x: data.count(x) for x in set(data)}
        n=len(data)
        return -sum((count/n)*log2(count/n) for count in counts.values())
    return {"scenario": "OPAQUE_DATA_INDICATOR_SIMULATION",
            "plain_entropy_bits_per_byte": round(entropy(source), 3),
            "opaque_entropy_bits_per_byte": round(entropy(opaque), 3),
            "opaque_flag": entropy(opaque) > 7.5,
            "note": "HIGH_ENTROPY_IS_NOT_PROOF_OF_RANSOMWARE",
            "files_modified": 0, "actions_executed": 0}

def firmware_trial() -> dict:
    # Dummy firmware-like strings. Does not even open a device file.
    expected = b"FAKE_FIRMWARE_VER_1_SIGNED_METADATA"
    observed = b"FAKE_FIRMWARE_VER_2_UNKNOWN_METADATA"
    return {"scenario": "FIRMWARE_ATTESTATION_GAP_SIMULATION",
            "reference_hash": _digest(expected),
            "observed_hash": _digest(observed),
            "integrity_mismatch": _digest(expected) != _digest(observed),
            "interpretation": "MISMATCH_REQUIRES_VENDOR_VALIDATION",
            "actual_firmware_access": False, "actions_executed": 0}

def run_all() -> dict:
    cases = [integrity_trial(), resource_trial(), poisoning_trial(),
             telemetry_trial(), opaque_data_trial(), firmware_trial()]
    return {"schema": "SOL_REALITY_STONE_CONTROLLED_EXPERIMENTS/1.0",
            "cases": cases, "count": len(cases),
            "real_world_targets_touched": 0,
            "protected_experiments": True, "model_deployed": False,
            "no_live_system_mutation": True}

if __name__ == "__main__":
    import json
    print(json.dumps(run_all(),indent=2,ensure_ascii=False))
