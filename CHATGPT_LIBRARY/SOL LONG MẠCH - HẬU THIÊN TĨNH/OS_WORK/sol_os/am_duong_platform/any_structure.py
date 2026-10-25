#!/usr/bin/env python3
"""Dịch Bất Kể Cấu Trúc — preserve Vietnamese source units and whitespace.

No automatic provider calls; translation needs an explicitly approved callable.
Zero grammar means no grammatical form is required, NOT a claim that
natural-language meaning can be proven from a single isolated word.
"""
from __future__ import annotations
import argparse
import json
import re
from typing import Callable

SCHEMA = "SOL_TRANSLATE_ANY_STRUCTURE/1.0"
MAX_INPUT = 12_000
# Keep spacing verbatim; line segment boundaries are structural carriers,
# not semantic judgments. No sentence detector / punctuation requirement.
LINE = re.compile(r"([^\r\n]*)(\r\n|\n|\r|$)")
EDGE_SPACES = re.compile(r"^(\s*)(.*?)(\s*)$", flags=re.DOTALL)


def units(raw: str) -> dict:
    if not isinstance(raw, str) or len(raw) > MAX_INPUT:
        raise ValueError("INPUT_TYPE_OR_LENGTH_INVALID")
    if "\x00" in raw:
        raise ValueError("NUL_INPUT_UNSUPPORTED")
    lines, pos = [], 0
    for match in LINE.finditer(raw):
        content, newline = match.groups()
        if content == "" and newline == "" and pos == len(raw):
            break
        m = EDGE_SPACES.fullmatch(content)
        assert m is not None
        lead, text, trail = m.groups()
        lines.append({"start":pos, "end":pos + len(content) + len(newline),
                      "prefix":lead, "raw":text, "suffix":trail, "newline":newline,
                      "has_text":bool(text.strip())})
        pos += len(content) + len(newline)
    if pos != len(raw):
        raise ValueError("SOURCE_NOT_LOSSLESS")
    if "".join(x["prefix"]+x["raw"]+x["suffix"]+x["newline"] for x in lines) != raw:
        raise ValueError("SOURCE_NOT_LOSSLESS")
    return {"schema":SCHEMA, "source":raw, "units":lines,
            "raw_bytes_utf8":len(raw.encode("utf-8")),
            "source_preserved":True, "grammatical_classification_required":False,
            "source_is_not_auto_rewritten":True}


def translate_any(raw: str, target: str, *, source: str="auto", approved: bool=False,
                  translate_part: Callable[[str,str,str],str] | None=None) -> dict:
    """Send each nonempty line through an approved actual translator.

    In tests, translate_part is injected; in production supplied by the authenticated
    provider adapter. Does not claim a human-quality semantic translation.
    """
    inspected = units(raw)
    if not isinstance(target,str) or not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z]{2,8})?",target):
        raise ValueError("TARGET_LANGUAGE_INVALID")
    if not isinstance(source,str) or not re.fullmatch(r"auto|[A-Za-z]{2,8}(?:-[A-Za-z]{2,8})?",source):
        raise ValueError("SOURCE_LANGUAGE_INVALID")
    if approved is not True:
        raise ValueError("EXTERNAL_TRANSFER_REQUIRES_EXPLICIT_APPROVAL")
    if translate_part is None:
        raise ValueError("TRANSLATION_PROVIDER_NOT_CONFIGURED")
    pieces, translated = [], 0
    for x in inspected["units"]:
        if x["has_text"]:
            part=translate_part(x["raw"],target,source)
            if not isinstance(part,str):
                raise ValueError("PROVIDER_TRANSLATION_INVALID")
            translated+=1
        else:
            part=x["raw"]
        pieces.append(x["prefix"]+part+x["suffix"]+x["newline"])
    return {"schema":SCHEMA, "translation":"".join(pieces),
            "source":raw, "target":target, "source_language_request":source,
            "nonempty_segments_translated":translated,
            "layout_preserved":True, "meaning_review_recommended_for_ambiguous_fragments":True,
            "source_preserved":True, "provider_called":translated>0,
            "no_sentence_or_standard_grammar_required":True}



# Multilingual, multi-structure v1.1: additive APIs, preserving legacy API contracts.
# This is Unicode-aware, not a claim of universal language understanding.
import unicodedata

MAX_NODES = 512
MAX_DEPTH = 12
TOKEN = re.compile(r"\w+(?:['’\u2010-\u2015-]\w+)*|[^\w\s]", flags=re.UNICODE)
POS_EXAMPLES = {
    "vi": {
        "noun": {"người", "cha", "mẹ", "nhà", "sách", "hoa", "dữ liệu"},
        "verb": {"đọc", "viết", "học", "dịch", "chạy", "yêu"},
        "adjective": {"đẹp", "tốt", "vui", "buồn", "nhanh", "chậm"},
    },
    "en": {
        "noun": {"person", "book", "home", "language", "data"},
        "verb": {"read", "write", "learn", "translate", "run"},
        "adjective": {"beautiful", "good", "happy", "sad", "fast"},
    },
}


def _language_family(char: str) -> str:
    code = ord(char)
    if 0x4E00 <= code <= 0x9FFF:
        return "Han"
    if 0x3040 <= code <= 0x30FF:
        return "Japanese_kana"
    if 0xAC00 <= code <= 0xD7AF:
        return "Hangul"
    if 0x0600 <= code <= 0x06FF:
        return "Arabic"
    if 0x0900 <= code <= 0x097F:
        return "Devanagari"
    if 0x0E00 <= code <= 0x0E7F:
        return "Thai"
    if 0x0400 <= code <= 0x04FF:
        return "Cyrillic"
    if 0x0370 <= code <= 0x03FF:
        return "Greek"
    return "Latin_or_other"


def inspect_multilingual(raw: str, *, language_hint: str = "auto") -> dict:
    """Lossless original + token spans. POS is example lexicon only, not a classifier.

    Segmentation is *not* a dictionary word breaker for scripts without spaces;
    callers should use locale-specific NLP providers for morphological assertions.
    """
    old = units(raw)
    if not isinstance(language_hint, str) or len(language_hint) > 32:
        raise ValueError("LANGUAGE_HINT_INVALID")
    tokens = []
    for match in TOKEN.finditer(raw):
        val = match.group()
        category = "number" if val.isnumeric() else "punctuation" if not val[0].isalnum() else "text_unit"
        family = _language_family(val[0])
        locale = language_hint.split("-")[0].lower()
        lexicon = POS_EXAMPLES.get(locale, {})
        candidates = [k for k, dictionary in lexicon.items() if val.casefold() in dictionary]
        tokens.append({"raw": val, "start": match.start(), "end": match.end(),
                       "kind": category, "script_hint": family,
                       "pos_candidates": candidates, "pos_verified": False})
    words = [x for x in tokens if x["kind"] == "text_unit"]
    repeats = []
    for left, right in zip(words, words[1:]):
        bridge = raw[left["end"]:right["start"]]
        if left["raw"].casefold() == right["raw"].casefold() and bridge.strip(" -\t") == "":
            repeats.append({"start": left["start"], "end": right["end"],
                            "raw": raw[left["start"]:right["end"]],
                            "type": "reduplication_candidate_not_verified"})
    return {"schema": "SOL_TRANSLATE_ANY_STRUCTURE/1.1", "mode": "LOCAL_INSPECTION",
            "source": raw, "source_preserved": True, "raw_bytes_utf8": old["raw_bytes_utf8"],
            "lines": old["units"], "tokens": tokens, "repetitions": repeats,
            "part_of_speech_status": "EXAMPLE_LEXICON_ONLY_OR_UNKNOWN",
            "unspaced_scripts_word_segmentation_verified": False,
            "all_unicode_accepted_subject_to_input_limits": True,
            "provider_called": False}


def translate_structure(data, target: str, *, source: str = "auto", approved: bool = False,
                        translate_part: Callable[[str, str, str], str] | None = None) -> dict:
    """Translate string values in JSON-like structures without changing keys/types.

    Callable contract matches translate_any(text, target, source); source content is
    kept, all leaf paths are reported, and requests are bounded. No cloud calls
    without explicit approval. Does not promise every language's grammar is known.
    """
    if not isinstance(target, str) or not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z]{2,8})?", target):
        raise ValueError("TARGET_LANGUAGE_INVALID")
    if not isinstance(source, str) or not re.fullmatch(r"auto|[A-Za-z]{2,8}(?:-[A-Za-z]{2,8})?", source):
        raise ValueError("SOURCE_LANGUAGE_INVALID")
    if approved is not True:
        raise ValueError("EXTERNAL_TRANSFER_REQUIRES_EXPLICIT_APPROVAL")
    if translate_part is None:
        raise ValueError("TRANSLATION_PROVIDER_NOT_CONFIGURED")
    events = []
    count = [0]
    def visit(value, path, depth):
        count[0] += 1
        if count[0] > MAX_NODES or depth > MAX_DEPTH:
            raise ValueError("STRUCTURE_LIMIT_EXCEEDED")
        if isinstance(value, str):
            if len(value) > MAX_INPUT:
                raise ValueError("INPUT_TYPE_OR_LENGTH_INVALID")
            if not value.strip():
                return value
            out = translate_any(value, target, source=source, approved=True, translate_part=translate_part)
            events.append({"path": path, "segments": out["nonempty_segments_translated"]})
            return out["translation"]
        if isinstance(value, dict):
            if any(not isinstance(k, str) for k in value):
                raise ValueError("STRUCTURE_KEYS_MUST_BE_STRINGS")
            return {k: visit(v, path + [k], depth + 1) for k, v in value.items()}
        if isinstance(value, list):
            return [visit(v, path + [i], depth + 1) for i, v in enumerate(value)]
        if value is None or isinstance(value, (bool, int, float)):
            return value
        raise ValueError("UNSUPPORTED_STRUCTURE_VALUE")
    result = visit(data, [], 0)
    return {"schema": "SOL_TRANSLATE_ANY_STRUCTURE/1.1",
            "source": data, "translation": result, "target": target,
            "paths_translated": events, "structure_preserved": True,
            "translation_keys_unchanged": True,
            "provider_called": bool(events), "external_approval": True,
            "semantic_accuracy_not_guaranteed": True}



def inspect_structure(data, *, language_hint="auto"):
    """Inspect text leaves of JSON-compatible values; never rewrite source data."""
    samples=[]
    nodes=[0]
    def walk(v, path, depth):
        nodes[0]+=1
        if nodes[0]>MAX_NODES or depth>MAX_DEPTH:
            raise ValueError("STRUCTURE_LIMIT_EXCEEDED")
        if isinstance(v,str):
            samples.append({"path":path,"inspection":inspect_multilingual(v,language_hint=language_hint)})
        elif isinstance(v,dict):
            if any(not isinstance(k,str) for k in v):
                raise ValueError("STRUCTURE_KEYS_MUST_BE_STRINGS")
            for key,val in v.items(): walk(val,path+[key],depth+1)
        elif isinstance(v,list):
            for i,val in enumerate(v):walk(val,path+[i],depth+1)
        elif v is None or isinstance(v,(bool,int,float)):
            return
        else:
            raise ValueError("UNSUPPORTED_STRUCTURE_VALUE")
    walk(data,[],0)
    return {"schema":"SOL_TRANSLATE_ANY_STRUCTURE/1.1", "mode":"LOCAL_INSPECTION",
            "source":data,"paths":samples,"source_preserved":True,"provider_called":False}


def main(argv=None):
    p=argparse.ArgumentParser(description="ÂM–DƯƠNG PHÁP SƯ — multilingual/structured data")
    p.add_argument("--text",help="Direct Unicode text")
    p.add_argument("--stdin",action="store_true",help="Read text/JSON from stdin")
    p.add_argument("--json-input",action="store_true",help="Parse stdin/text as a JSON value")
    p.add_argument("--mode",choices=("inspect","translate"),default="inspect")
    p.add_argument("--language-hint",default="auto")
    p.add_argument("--target",default="en")
    p.add_argument("--source",default="auto")
    p.add_argument("--approve-external",action="store_true",help="Consent to external text transfer")
    a=p.parse_args(argv)
    if (a.text is None) == (not a.stdin):
        p.error("choose exactly one of --text or --stdin")
    import sys
    incoming=sys.stdin.read() if a.stdin else a.text
    data=json.loads(incoming) if a.json_input else incoming
    if a.mode=="inspect":
        result=inspect_structure(data,language_hint=a.language_hint) if a.json_input else inspect_multilingual(data,language_hint=a.language_hint)
    else:
        if not a.approve_external:
            p.error("translation requires --approve-external")
        # Already integrated provider adapter; no new service, credentials or permissions.
        from capabilities import translate
        def provider(text,target,source):
            return translate(text,target,source=source,approved=True)["translation"]
        result=translate_structure(data,a.target,source=a.source,approved=True,translate_part=provider) if a.json_input else translate_any(data,a.target,source=a.source,approved=True,translate_part=provider)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()