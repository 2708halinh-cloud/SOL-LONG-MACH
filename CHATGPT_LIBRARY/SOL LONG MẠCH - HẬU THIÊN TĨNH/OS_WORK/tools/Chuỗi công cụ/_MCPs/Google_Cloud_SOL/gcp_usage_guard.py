#!/usr/bin/env python3
"""Zero-cloud-call diagnostic gate for Google Cloud API usage snapshots.

Accepts existing aggregate metrics exported from a dashboard as JSON or CSV.
Does not authenticate, contact a provider, retry APIs, or change cloud resources.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys
from typing import Any

ALIASES = {
    "api": ("api", "name", "Tên", "ten"),
    "requests": ("requests", "request_count", "Yêu cầu", "yeu_cau"),
    "error_percent": ("error_percent", "errors_percent", "Lỗi (%)", "loi_phan_tram"),
    "average_latency_ms": ("average_latency_ms", "mean_latency_ms", "Độ trễ trung bình (ms)"),
    "p95_latency_ms": ("p95_latency_ms", "p95_ms", "Độ trễ ở phân vị thứ 95 (ms)"),
}
MISSING = {"", "—", "–", "-", "n/a", "null"}


def field(item: dict[str, Any], name: str) -> Any:
    for alias in ALIASES[name]:
        if alias in item:
            return item[alias]
    return None


def number(value: Any, label: str) -> Decimal | None:
    if value is None or str(value).strip().lower() in MISSING:
        return None
    if isinstance(value, bool):
        raise ValueError("INVALID_" + label.upper())
    try:
        result = Decimal(str(value).strip().replace("%", ""))
    except InvalidOperation as exc:
        raise ValueError("INVALID_" + label.upper()) from exc
    if not result.is_finite() or result < 0:
        raise ValueError("INVALID_" + label.upper())
    return result


def analyse(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(rows, list) or len(rows) > 300 or not all(isinstance(x, dict) for x in rows):
        raise ValueError("INVALID_METRICS_ARRAY")
    items = []
    for row in rows:
        name = str(field(row, "api") or "").strip()
        if not name or len(name) > 180:
            raise ValueError("INVALID_API_NAME")
        requests = number(field(row, "requests"), "requests")
        rate = number(field(row, "error_percent"), "error_percent")
        avg = number(field(row, "average_latency_ms"), "average_latency_ms")
        p95 = number(field(row, "p95_latency_ms"), "p95_latency_ms")
        if requests is not None and requests != requests.to_integral_value():
            raise ValueError("REQUESTS_NOT_INTEGER")
        if rate is not None and rate > 100:
            raise ValueError("ERROR_PERCENT_ABOVE_100")
        if requests is None or rate is None:
            action, failed = "NO_DATA_DO_NOT_INFER_ZERO", None
        else:
            failed = requests * rate / 100
            if requests == 0:
                action = "NO_TRAFFIC"
            elif rate == 100:
                action = "STOP_AUTOMATIC_RETRY_INVESTIGATE_ERRORS"
            elif rate >= 50:
                action = "PAUSE_RETRY_INVESTIGATE_ERRORS"
            elif rate > 0:
                action = "REVIEW_ERRORS_BEFORE_RETRY"
            else:
                action = "NO_ERRORS_IN_REPORTED_WINDOW"
        items.append({
            "api": name,
            "requests": int(requests) if requests is not None else None,
            "error_percent": float(rate) if rate is not None else None,
            "estimated_failed_requests": float(failed) if failed is not None else None,
            "average_latency_ms": float(avg) if avg is not None else None,
            "p95_latency_ms": float(p95) if p95 is not None else None,
            "action": action,
        })
    known = [x for x in items if x["requests"] is not None and x["error_percent"] is not None]
    total = sum(x["requests"] for x in known)
    failed = sum(Decimal(str(x["estimated_failed_requests"])) for x in known)
    return {
        "schema": "SOL_GCP_USAGE_GUARD/1.0",
        "status": "SOURCE_AGGREGATES_ANALYSED_NO_PROVIDER_CALLS",
        "provider_api_calls": 0,
        "scope": "only rows containing both requests and error percentage",
        "known_requests": total,
        "estimated_failed_requests": float(failed),
        "cost": "UNKNOWN_REQUIRES_BILLING_EVIDENCE",
        "caller_identity": "UNKNOWN_REQUIRES_AUDIT_LOG_EVIDENCE",
        "diagnostic_next": "READ_AUDIT_LOGS_AND_BILLING_WITH_AUTHORIZED_TOOL_BEFORE_ANY_RETRY",
        "items": items,
    }


def load(path: str) -> list[dict[str, Any]]:
    if path == "-":
        raw = sys.stdin.read(1_000_001)
    else:
        source = Path(path)
        if source.stat().st_size > 1_000_000:
            raise ValueError("INPUT_TOO_LARGE")
        raw = source.read_text(encoding="utf-8-sig")
    if len(raw) > 1_000_000:
        raise ValueError("INPUT_TOO_LARGE")
    if raw.lstrip().startswith(("{", "[")):
        value = json.loads(raw)
        if isinstance(value, dict):
            value = value.get("metrics")
        return value
    return list(csv.DictReader(raw.splitlines()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GCP usage analysis, no cloud calls or retries")
    parser.add_argument("--input", required=True, help="JSON/CSV snapshot, or - for stdin")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(analyse(load(args.input)), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
        print(json.dumps({"status": "INPUT_REJECTED", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
