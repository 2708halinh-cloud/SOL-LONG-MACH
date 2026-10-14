#!/usr/bin/env python3
"""Validate the real captured MCP tools/list response (no network, no secrets)."""
import json,sys
from pathlib import Path
REQ=("core_list_projects","core_list_project_teams","core_get_identity_ids")
def inspect(payload):
    d=payload.get("result",payload) if isinstance(payload,dict) else payload
    arr=d.get("tools",[]) if isinstance(d,dict) else d
    if not isinstance(arr,list): raise ValueError("Expected MCP tools array")
    details={}
    for needle in REQ:
        matches=[x for x in arr if isinstance(x,dict) and (x.get("name")==needle or x.get("name","").endswith("_"+needle))]
        details[needle]={"matches":[x["name"] for x in matches],
                         "unambiguous":len(matches)==1,
                         "schema_present":len(matches)==1 and isinstance(matches[0].get("inputSchema"),dict)}
    return {"status":"PASS" if all(x["unambiguous"] and x["schema_present"] for x in details.values()) else "OPEN","checks":details}
if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("Usage: python verify_tools_list.py tools-list.json")
    v=inspect(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print(json.dumps(v,ensure_ascii=False,indent=2))
    raise SystemExit(0 if v["status"]=="PASS" else 2)
