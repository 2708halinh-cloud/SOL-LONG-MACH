"""Small, dependency-free typed-data adapter for SOL. Not Drupal PHP runtime.

The only input lookup is Mapping/list; never evaluate expressions, Python
attributes, callables, or arbitrary filter names from templates.
"""
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

class TypedDataError(ValueError):
    """Invalid data path, filter, value or template."""

_MISSING = object()
_PATH = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*|\[[0-9]+\])*$")
_SEGMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[0-9]+")
_TOKEN = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
_ALLOWED_TEMPLATE = 65536
_MAX_TOKENS = 64

def fetch(data: Mapping[str, Any], path: str, default: Any = _MISSING) -> Any:
    """Resolve only dict keys and list indexes; no Python attribute traversal."""
    if not isinstance(data, Mapping) or not isinstance(path, str) or not _PATH.fullmatch(path):
        raise TypedDataError("Invalid typed-data path")
    node: Any = data
    for match in _SEGMENT.finditer(path):
        key = match.group()
        if isinstance(node, Mapping) and key in node:
            node = node[key]
        elif isinstance(node, (list, tuple)) and key.isdecimal() and int(key) < len(node):
            node = node[int(key)]
        elif default is not _MISSING:
            return default
        else:
            raise TypedDataError("Typed-data path not found")
    return node

def _to_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    if isinstance(value, (Mapping, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)

def _entity_url(value: Any) -> str:
    if not isinstance(value, Mapping):
        raise TypedDataError("entity_url requires a mapping")
    url = value.get("canonical_url", value.get("url"))
    if not isinstance(url, str) or not url or "\n" in url or "\r" in url:
        raise TypedDataError("Invalid entity URL")
    if url.startswith("/") and not url.startswith("//"):
        return url
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise TypedDataError("Entity URL must be a relative path or HTTPS URL")
    return url

def filter_value(value: Any, name: str) -> Any:
    """Allowlisted pure typed-data filters. No eval or dynamic import."""
    filters = {
        "lower": lambda x: _to_text(x).lower(),
        "upper": lambda x: _to_text(x).upper(),
        "trim": lambda x: _to_text(x).strip(),
        "length": lambda x: len(x) if isinstance(x, (str, list, tuple, Mapping)) else 0,
        "json": lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True),
        "string": _to_text,
        "entity_url": _entity_url,
    }
    if name not in filters:
        raise TypedDataError("Unknown typed-data filter")
    return filters[name](value)

def resolve_expression(data: Mapping[str, Any], expression: str) -> Any:
    """Resolve a Twig-like token expression: node.title|lower."""
    if not isinstance(expression, str) or len(expression) > 256:
        raise TypedDataError("Invalid typed-data expression")
    parts = [item.strip() for item in expression.split("|")]
    if not parts or any(not item for item in parts) or len(parts) > 6:
        raise TypedDataError("Invalid typed-data expression")
    value = fetch(data, parts[0])
    for name in parts[1:]:
        value = filter_value(value, name)
    return value

def resolve_placeholder(data: Mapping[str, Any], template: str) -> Any:
    """Preserve non-string types for a sole token; interpolate text otherwise."""
    if not isinstance(template, str) or len(template) > _ALLOWED_TEMPLATE:
        raise TypedDataError("Invalid template size")
    matches = list(_TOKEN.finditer(template))
    if len(matches) > _MAX_TOKENS:
        raise TypedDataError("Too many placeholders")
    if "{{" in _TOKEN.sub("", template) or "}}" in _TOKEN.sub("", template):
        raise TypedDataError("Malformed placeholder")
    if len(matches) == 1 and template.strip() == matches[0].group(0):
        return resolve_expression(data, matches[0].group(1))
    rendered = _TOKEN.sub(lambda m: _to_text(resolve_expression(data, m.group(1))), template)
    if len(rendered) > _ALLOWED_TEMPLATE:
        raise TypedDataError("Rendered template too large")
    return rendered

def form_widget(data_type: str, label: str, required: bool = False) -> dict[str, Any]:
    """UI-neutral typed form metadata; does not mutate a Drupal form or core API."""
    kinds = {
        "string": {"widget": "text", "input_type": "text"},
        "integer": {"widget": "number", "input_type": "number", "step": 1},
        "float": {"widget": "number", "input_type": "number", "step": "any"},
        "boolean": {"widget": "checkbox", "input_type": "checkbox"},
        "date": {"widget": "date", "input_type": "date"},
        "list": {"widget": "list", "input_type": "collection"},
    }
    if data_type not in kinds or not isinstance(label, str):
        raise TypedDataError("Unsupported form widget type")
    return {"data_type": data_type, "label": label, "required": bool(required), **kinds[data_type]}

def hierarchy(value: Any, max_depth: int = 16) -> dict[str, Any]:
    """Typed hierarchy for structured values, bounded to avoid recursive loops."""
    def walk(v: Any, depth: int, seen: set[int]) -> dict[str, Any]:
        if depth > max_depth:
            raise TypedDataError("Maximum hierarchy depth exceeded")
        if isinstance(v, (Mapping, list, tuple)):
            if id(v) in seen:
                raise TypedDataError("Cycle in typed-data structure")
            seen.add(id(v))
            try:
                if isinstance(v, Mapping):
                    if not all(isinstance(k, str) for k in v):
                        raise TypedDataError("Map keys must be strings")
                    return {"type": "map", "items": {k: walk(w, depth + 1, seen) for k, w in v.items()}}
                return {"type": "list", "items": [walk(w, depth + 1, seen) for w in v]}
            finally:
                seen.remove(id(v))
        if v is None or isinstance(v, (str, bool, int, float)):
            kind = "null" if v is None else "boolean" if isinstance(v, bool) else "integer" if isinstance(v, int) else "float" if isinstance(v, float) else "string"
            return {"type": kind, "value": v}
        raise TypedDataError("Unsupported typed-data value")
    return walk(value, 0, set())
