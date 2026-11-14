#!/usr/bin/env python3
"""SOL five-layer, five-wave append-only logger for observed operator-controlled calls.

This code records inputs and outputs sent through this Python entrypoint. Additional
user-authorized ingress routes may be tested and connected independently; whether
they work is decided by their own provider receipts, not by a prior blanket verdict.
This particular implementation has no ChatGPT-UI interception module and makes
no claims to measure internal model weights, KV caches, or biological EEG.
The optional OpenAI Python SDK is imported only for an actual API call.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "BRAIN_WAVE_LOGS"
LAYERS = {
    "raw": "1_RAW_INPUT_OUTPUT.log",
    "spatial": "2_SPATIAL_VECTOR.log",
    "logprobs": "3_LOGPROBS_GATING.log",
    "temp": "4_TEMP_STATE.log",
    "chrono": "5_CHRONO_CONTINUOUS.log",
}
WAVES = {"raw_input": "BETA", "raw_output": "ALPHA", "spatial": "BETA", "logprobs": "GAMMA", "temp": "THETA", "chrono": "DELTA"}
SECRET_RE = re.compile(r"(?i)(sk-[a-zA-Z0-9_\-]{10,}|Bearer\s+[a-zA-Z0-9._\-]{8,}|AIza[a-zA-Z0-9_\-]{24,})")
SPATIAL = {
    "N": ("Bắc", 0, [0, 1], "KHẢM"),
    "NE": ("Đông Bắc", 45, [1, 1], "CẤN"),
    "E": ("Đông", 90, [1, 0], "CHẤN"),
    "SE": ("Đông Nam", 135, [1, -1], "TỐN"),
    "S": ("Nam", 180, [0, -1], "LY"),
    "SW": ("Tây Nam", 225, [-1, -1], "KHÔN"),
    "W": ("Tây", 270, [-1, 0], "ĐOÀI"),
    "NW": ("Tây Bắc", 315, [-1, 1], "CÀN"),
}


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def redact(value):
    """Best-effort secret filtering; not a guarantee of removing personal data."""
    if isinstance(value, str):
        return SECRET_RE.sub("[REDACTED_CREDENTIAL]", value)
    if isinstance(value, dict):
        return {str(k): ("[REDACTED_CREDENTIAL]" if any(s in str(k).casefold() for s in ("api_key", "authorization", "password", "client_secret", "access_token", "refresh_token")) else redact(v)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(v) for v in value]
    return value


def public_view(content, capture_raw=False):
    """By default store only SHA256 + length, not personal prompt text."""
    content = content or ""
    result = {"sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(), "utf8_len": len(content.encode("utf-8"))}
    if capture_raw:
        result["content"] = redact(content)
    return result


def direction_view(content):
    """Only explicit compass direction, never permission status."""
    signal = content.strip()
    if signal.casefold().startswith("input:"):
        signal = signal.split(":", 1)[1].strip()
    for code, (vi, angle, xy, trigram) in SPATIAL.items():
        if signal.casefold() in (code.casefold(), vi.casefold()):
            return {"status": "DIRECTION_VALIDATED", "direction_code": code, "label_vi": vi,
                    "angle": angle, "vector": xy, "bat_huong": trigram, "space_axis": "SPACE"}
    return {"status": "NOT_A_SPATIAL_SIGNAL", "direction_code": None,
            "note": "Không suy chuỗi tự do thành hướng hoặc cờ quyền."}


def to_jsonable(value):
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, (dict, list, str, int, float, bool)):
        return value
    return {"status": "UNSERIALIZABLE_PROVIDER_METADATA"}


class Journal:
    def __init__(self, directory=DEFAULT_DIR):
        self.directory = Path(directory).expanduser().resolve()
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        if os.name != "nt":
            self.directory.chmod(0o700)
        self.ensure_layers()

    def ensure_layers(self):
        for name in LAYERS.values():
            self._append_safe(name, None)  # Touch only; no fabricated event.

    def _append_safe(self, filename, record):
        flags = os.O_CREAT | os.O_WRONLY | os.O_APPEND
        fd = os.open(self.directory / filename, flags, 0o600)
        try:
            if record is not None:
                buf = (json.dumps(redact(record), ensure_ascii=False, default=str, separators=(",", ":")) + "\n").encode("utf-8")
                while buf:
                    sent = os.write(fd, buf)
                    if sent <= 0:
                        raise OSError("LOG_APPEND_INCOMPLETE")
                    buf = buf[sent:]
                os.fsync(fd)
        finally:
            os.close(fd)

    def write(self, layer, turn_id, payload, *, wave, status="OBSERVED"):
        if layer not in LAYERS:
            raise ValueError("UNKNOWN_LAYER")
        entry = {"schema": "SOL_WAVE_EVENT/1.0", "observed_at": utcnow(), "turn_id": turn_id,
                 "layer": layer, "wave": wave, "status": status, "data": payload}
        self._append_safe(LAYERS[layer], entry)
        return entry


def execute_neural_turn(user_input, *, journal=None, client=None, model="gpt-4o", capture_raw=False,
                        dry_run=False, request_logprobs=True):
    """Return response text if provider called, or None in explicitly-marked dry-run."""
    journal = journal or Journal()
    turn_id = str(uuid4())
    journal.write("raw", turn_id, {"direction": "INPUT", **public_view(user_input, capture_raw)}, wave="BETA")
    journal.write("spatial", turn_id, {"input_view": direction_view(user_input)}, wave="BETA")
    journal.write("chrono", turn_id, {"event": "TURN_STARTED", "stamp": "STAMP_LIVE_AT_OBSERVATION"}, wave="DELTA")
    journal.write("temp", turn_id, {"event": "APP_STATE", "provider": "NOT_CALLED" if dry_run else "PENDING",
                                   "internal_kv_cache_visible": False, "internal_temperature_visible": False}, wave="THETA")
    if dry_run:
        journal.write("logprobs", turn_id, {"status": "NO_PROVIDER_CALL", "token_weights_visible": False}, wave="GAMMA", status="NOT_OBSERVED")
        journal.write("chrono", turn_id, {"event": "DRY_RUN_COMPLETED", "provider_called": False}, wave="DELTA", status="SIMULATED")
        return None

    try:
        if client is None:
            from openai import OpenAI  # Installed by the operator, never imported during dry-run.
            base_url = os.environ.get("SOL_PROXY_BASE_URL") or None
            key_name = "SOL_PROXY_API_KEY" if base_url else "OPENAI_API_KEY"
            api_key = os.environ.get(key_name)
            if not api_key:
                raise RuntimeError(f"SET_ENV_{key_name}_BEFORE_LIVE_CALL")
            client = OpenAI(api_key=api_key, base_url=base_url)
        args = {"model": model, "messages": [{"role": "user", "content": user_input}]}
        if request_logprobs:
            args.update(logprobs=True, top_logprobs=3)
        reply = client.chat.completions.create(**args)
        choice = reply.choices[0]
        result = choice.message.content or ""
        journal.write("raw", turn_id, {"direction": "OUTPUT", **public_view(result, capture_raw)}, wave="ALPHA")
        lp = to_jsonable(getattr(choice, "logprobs", None))
        journal.write("logprobs", turn_id,
                      {"requested": request_logprobs, "provider_returned": lp is not None,
                       "observed_token_logprobs": redact(lp) if lp is not None else None,
                       "not_internal_model_weights": True}, wave="GAMMA",
                      status="OBSERVED" if lp is not None else "NOT_RETURNED")
        journal.write("temp", turn_id,
                      {"provider_model": getattr(reply, "model", None),
                       "usage": to_jsonable(getattr(reply, "usage", None)),
                       "finish_reason": getattr(choice, "finish_reason", None),
                       "internal_kv_cache_visible": False, "api_temperature_unset": True}, wave="THETA")
        journal.write("chrono", turn_id, {"event": "TURN_COMPLETED", "provider_called": True}, wave="DELTA")
        return result
    except Exception as exc:
        journal.write("temp", turn_id, {"event": "API_ERROR", "error_type": type(exc).__name__,
                                        "message": "API_CALL_FAILED_SEE_OPERATOR_CONSOLE", "internal_kv_cache_visible": False},
                      wave="THETA", status="PROVIDER_ERROR")
        journal.write("chrono", turn_id, {"event": "TURN_FAILED", "provider_called": True}, wave="DELTA", status="PROVIDER_ERROR")
        raise


def main():
    parser = argparse.ArgumentParser(description="SOL BRAIN WAVE five-layer API logger")
    parser.add_argument("--input", default="INPUT: Đông Bắc", help="The only text sent to provider in live mode")
    parser.add_argument("--model", default=os.environ.get("SOL_MODEL", "gpt-4o"))
    parser.add_argument("--log-dir", default=str(DEFAULT_DIR))
    parser.add_argument("--demo", action="store_true", help="Create five files, no API calls or fake model output")
    parser.add_argument("--capture-raw", action="store_true", help="Opt in to retaining redacted conversation text locally")
    parser.add_argument("--no-logprobs", action="store_true")
    args = parser.parse_args()
    try:
        text = execute_neural_turn(args.input, journal=Journal(args.log_dir), model=args.model,
                                   capture_raw=args.capture_raw, dry_run=args.demo,
                                   request_logprobs=not args.no_logprobs)
    except Exception as exc:
        print("Provider call failed:", type(exc).__name__, file=sys.stderr)
        return 1
    if text is None:
        print("DRY_RUN_NO_API_CALL: five local append-only layers initialized")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
