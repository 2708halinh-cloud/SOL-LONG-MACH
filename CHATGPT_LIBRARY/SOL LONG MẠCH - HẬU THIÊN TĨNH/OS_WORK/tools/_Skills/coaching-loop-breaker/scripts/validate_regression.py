#!/usr/bin/env python3
"""Validate the coaching-loop-breaker regression contract using only stdlib."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals" / "unsupervised-training-regression.json"
REQUIRED_CASES = {
    "PERMISSION-REFUSAL-001",
    "TOOL-PREFLIGHT-001",
    "TOOL-SCHEMA-002",
    "TOOL-PERMISSION-003",
    "TOOL-FAILURE-004",
    "TOOL-READBACK-005",
    "TOOL-CLAIM-006",
    "CONSISTENCY-007",
}

def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    if not FIXTURE.is_file():
        fail(f"missing fixture: {FIXTURE}")
    try:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"fixture is not readable valid JSON: {exc}")
    if not isinstance(data, dict):
        fail("top-level JSON value must be an object")
    if data.get("name") != "coaching-loop-breaker-unsupervised-regression":
        fail("unexpected suite name")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("'cases' must be a non-empty array")
    seen = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"cases[{index}] must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            fail(f"cases[{index}] has no non-empty id")
        if case_id in seen:
            fail(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if not isinstance(case.get("failure"), str) or not case["failure"].strip():
            fail(f"{case_id}: missing failure description")
        expected = case.get("expected")
        if not isinstance(expected, list) or not expected or not all(
            isinstance(item, str) and item.strip() for item in expected
        ):
            fail(f"{case_id}: expected must be a non-empty list of strings")
        if not isinstance(case.get("pass"), str) or not case["pass"].strip():
            fail(f"{case_id}: missing pass condition")
    missing = sorted(REQUIRED_CASES - seen)
    if missing:
        fail("required tool-use regression cases missing: " + ", ".join(missing))
    print(f"PASS: valid JSON; {len(cases)} unique cases; required tool-use cases present.")
    print("NOTE: this validates the regression contract, not live agent behavior.")

if __name__ == "__main__":
    main()
