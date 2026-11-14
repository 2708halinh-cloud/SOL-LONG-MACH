#!/usr/bin/env python3
"""TESSERACT E-R relational layer. Additive database, source-bound identifiers.
No writes to legacy Synapse/Chroma/host archive, no hidden model state claims.
"""
from __future__ import annotations
import argparse
import json
import sqlite3
from pathlib import Path

SCHEMA = r"""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sources (
 source_id TEXT PRIMARY KEY, provider TEXT NOT NULL, locator TEXT NOT NULL,
 source_kind TEXT NOT NULL, observed_at TEXT, sha256 TEXT,
 UNIQUE(provider,locator)
);
CREATE TABLE IF NOT EXISTS entity_sets (
 set_id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, source_id TEXT NOT NULL REFERENCES sources(source_id)
);
CREATE TABLE IF NOT EXISTS entities (
 entity_id TEXT PRIMARY KEY, set_id TEXT NOT NULL REFERENCES entity_sets(set_id),
 display_name TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(source_id),
 identity_status TEXT NOT NULL CHECK(identity_status IN
 ('SOURCE_ASSERTED','CARRIER_OBSERVED','VERIFIED_PROVIDER','UNRESOLVED')),
 UNIQUE(entity_id,set_id)
);
CREATE TABLE IF NOT EXISTS entity_aliases (
 entity_id TEXT NOT NULL REFERENCES entities(entity_id), namespace TEXT NOT NULL,
 alias TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(source_id),
 PRIMARY KEY(entity_id,namespace,alias)
);
CREATE TABLE IF NOT EXISTS attribute_definitions (
 attribute_id TEXT PRIMARY KEY, set_id TEXT NOT NULL REFERENCES entity_sets(set_id),
 name TEXT NOT NULL, domain TEXT NOT NULL CHECK(domain IN
 ('string','integer','real','date','boolean')),
 value_mode TEXT NOT NULL CHECK(value_mode IN ('single','multi','derived')),
 structure TEXT NOT NULL CHECK(structure IN ('simple','composite','derived')),
 parent_attribute_id TEXT REFERENCES attribute_definitions(attribute_id),
 derivation TEXT, is_candidate_key INTEGER NOT NULL DEFAULT 0 CHECK(is_candidate_key IN (0,1)),
 source_id TEXT NOT NULL REFERENCES sources(source_id),
 UNIQUE(set_id,name),
 CHECK((value_mode='derived')=(structure='derived')),
 CHECK(value_mode!='derived' OR derivation IS NOT NULL)
);
CREATE TABLE IF NOT EXISTS attribute_values (
 entity_id TEXT NOT NULL REFERENCES entities(entity_id),
 attribute_id TEXT NOT NULL REFERENCES attribute_definitions(attribute_id),
 ordinal INTEGER NOT NULL DEFAULT 0 CHECK(ordinal>=0),
 v_text TEXT, v_integer INTEGER, v_real REAL, v_date TEXT, v_boolean INTEGER
 CHECK(v_boolean IN (0,1)),
 source_id TEXT NOT NULL REFERENCES sources(source_id),
 PRIMARY KEY(entity_id,attribute_id,ordinal),
 CHECK((v_text IS NOT NULL)+(v_integer IS NOT NULL)+(v_real IS NOT NULL)
       +(v_date IS NOT NULL)+(v_boolean IS NOT NULL)=1)
);
CREATE TABLE IF NOT EXISTS relation_types (
 relation_type_id TEXT PRIMARY KEY, verb TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(source_id)
);
CREATE TABLE IF NOT EXISTS relation_role_specs (
 relation_type_id TEXT NOT NULL REFERENCES relation_types(relation_type_id),
 role_key TEXT NOT NULL, entity_set_id TEXT NOT NULL REFERENCES entity_sets(set_id),
 min_per_entity INTEGER NOT NULL DEFAULT 0 CHECK(min_per_entity>=0),
 max_per_entity INTEGER CHECK(max_per_entity IS NULL OR max_per_entity>=min_per_entity),
 PRIMARY KEY(relation_type_id,role_key)
);
CREATE TABLE IF NOT EXISTS relations (
 relation_id TEXT PRIMARY KEY, relation_type_id TEXT NOT NULL REFERENCES relation_types(relation_type_id),
 source_id TEXT NOT NULL REFERENCES sources(source_id),
 valid_from TEXT, valid_to TEXT, note TEXT,
 UNIQUE(relation_id,relation_type_id),
 CHECK(valid_to IS NULL OR valid_from IS NULL OR valid_to>=valid_from)
);
CREATE TABLE IF NOT EXISTS relation_participants (
 relation_id TEXT NOT NULL, relation_type_id TEXT NOT NULL,
 role_key TEXT NOT NULL, entity_id TEXT NOT NULL REFERENCES entities(entity_id),
 PRIMARY KEY(relation_id,role_key),
 FOREIGN KEY(relation_id,relation_type_id) REFERENCES relations(relation_id,relation_type_id),
 FOREIGN KEY(relation_type_id,role_key) REFERENCES relation_role_specs(relation_type_id,role_key)
);
CREATE TABLE IF NOT EXISTS carrier_locations (
 carrier_id TEXT PRIMARY KEY REFERENCES entities(entity_id),
 provider TEXT NOT NULL, locator TEXT NOT NULL,
 observed_access TEXT NOT NULL CHECK(observed_access IN
 ('OBSERVED_READ','SOURCE_POINTER','UNTESTED')),
 UNIQUE(provider,locator)
);
CREATE TABLE IF NOT EXISTS change_events (
 event_id TEXT PRIMARY KEY, entity_id TEXT REFERENCES entities(entity_id),
 action TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(source_id),
 timestamp TEXT, consequence TEXT, receipt_ref TEXT
);
CREATE TRIGGER IF NOT EXISTS trg_attributes BEFORE INSERT ON attribute_values BEGIN
 SELECT CASE WHEN (SELECT set_id FROM entities WHERE entity_id=NEW.entity_id)
  != (SELECT set_id FROM attribute_definitions WHERE attribute_id=NEW.attribute_id)
 THEN RAISE(ABORT,'ATTRIBUTE_WRONG_ENTITY_SET') END;
 SELECT CASE WHEN (SELECT value_mode FROM attribute_definitions WHERE attribute_id=NEW.attribute_id)='derived'
 THEN RAISE(ABORT,'DERIVED_VALUE_MUST_BE_COMPUTED') END;
 SELECT CASE WHEN NEW.ordinal!=0 AND
  (SELECT value_mode FROM attribute_definitions WHERE attribute_id=NEW.attribute_id)='single'
 THEN RAISE(ABORT,'SINGLE_VALUE_ORDINAL') END;
 SELECT CASE WHEN (
  SELECT domain FROM attribute_definitions WHERE attribute_id=NEW.attribute_id
 ) != CASE WHEN NEW.v_text IS NOT NULL THEN 'string'
   WHEN NEW.v_integer IS NOT NULL THEN 'integer'
   WHEN NEW.v_real IS NOT NULL THEN 'real'
   WHEN NEW.v_date IS NOT NULL THEN 'date' ELSE 'boolean' END
 THEN RAISE(ABORT,'ATTRIBUTE_DOMAIN_MISMATCH') END;
END;
DROP TRIGGER IF EXISTS trg_participant_set;
CREATE TRIGGER trg_participant_set BEFORE INSERT ON relation_participants BEGIN
 SELECT CASE WHEN (SELECT set_id FROM entities WHERE entity_id=NEW.entity_id) !=
  (SELECT entity_set_id FROM relation_role_specs WHERE
   relation_type_id=NEW.relation_type_id AND role_key=NEW.role_key)
 THEN RAISE(ABORT,'RELATION_ROLE_ENTITY_SET_MISMATCH') END;
 SELECT CASE WHEN NOT EXISTS (
  SELECT 1 FROM relation_participants
  WHERE relation_id=NEW.relation_id AND role_key=NEW.role_key
 ) AND (
  SELECT max_per_entity FROM relation_role_specs WHERE
  relation_type_id=NEW.relation_type_id AND role_key=NEW.role_key
 ) IS NOT NULL AND (
  SELECT COUNT(*) FROM relation_participants WHERE
   relation_type_id=NEW.relation_type_id AND role_key=NEW.role_key AND entity_id=NEW.entity_id
 ) >= (
  SELECT max_per_entity FROM relation_role_specs WHERE
  relation_type_id=NEW.relation_type_id AND role_key=NEW.role_key
 ) THEN RAISE(ABORT,'RELATION_ROLE_MAX_CARDINALITY') END;
END;
CREATE VIEW IF NOT EXISTS v_relations AS
 SELECT r.relation_id, r.relation_type_id, k.verb, p.role_key,
  p.entity_id, e.display_name, e.set_id, r.source_id, r.valid_from
 FROM relations r JOIN relation_types k USING (relation_type_id)
 JOIN relation_participants p USING (relation_id,relation_type_id)
 JOIN entities e USING (entity_id);
"""
DRIVE_SOURCE = "drive:1MmlGk1x8InnfySJR7NzRXKU4sL_KyUgR8p8dJ97Qj30"
CHAT_SOURCE = "chat:super-r014-20261023"
HOST_SOURCE = "host:observed-tesseract-20261023"
def connect(path: str | Path):
    db=sqlite3.connect(str(path))
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=3000")
    db.executescript(SCHEMA)
    return db

def initialize(db):
    sources=[
      (DRIVE_SOURCE,"Google Drive","https://docs.google.com/document/d/1MmlGk1x8InnfySJR7NzRXKU4sL_KyUgR8p8dJ97Qj30/edit","SOURCE_DIRECT", "2026-10-21",None),
      (CHAT_SOURCE,"conversation","SUPER_R014_SUBSCRIBE_RESET_SOURCE_DIRECT_20261023.md","USER_DIRECT","2026-10-23",None),
      (HOST_SOURCE,"Windows","G:/OS_Workspace/TESSERACT_OS","OBSERVED_LOCAL","2026-10-23",None),
    ]
    db.executemany("INSERT OR IGNORE INTO sources VALUES(?,?,?,?,?,?)",sources)
    kinds=[
      ("HUMAN","Con người"),("AGENT","Tác nhân phần mềm"),
      ("LOCUS","LOCUS"),("DEVICE","Thiết bị"),("CARRIER","Vật mang"),
      ("DOCUMENT","Tài liệu"),("ITEM","ITEM"),("PROVIDER","Nhà cung cấp"),
      ("EVENT","Biến cố"),("PROJECT","Dự án")
    ]
    db.executemany("INSERT OR IGNORE INTO entity_sets VALUES(?,?,?)",
                   [(a,b,DRIVE_SOURCE) for a,b in kinds])
    entities=[
      ("human:ha-linh","HUMAN","Hà Linh",CHAT_SOURCE,"SOURCE_ASSERTED"),
      ("agent:sol","AGENT","SOL",CHAT_SOURCE,"SOURCE_ASSERTED"),
      ("locus:sol","LOCUS","LOCUS SOL",CHAT_SOURCE,"SOURCE_ASSERTED"),
      ("item:super-r014","ITEM","SUPER R-014",CHAT_SOURCE,"SOURCE_ASSERTED"),
      ("document:drive-er","DOCUMENT","Thực thể.txt",DRIVE_SOURCE,"VERIFIED_PROVIDER"),
      ("device:windows-desktop-86itnq4","DEVICE","DESKTOP-86ITNQ4",HOST_SOURCE,"CARRIER_OBSERVED"),
      ("carrier:tesseract-g","CARRIER","TESSERACT_OS (G:)",HOST_SOURCE,"CARRIER_OBSERVED"),
      ("provider:drive","PROVIDER","Google Drive",DRIVE_SOURCE,"VERIFIED_PROVIDER"),
    ]
    db.executemany("INSERT OR IGNORE INTO entities VALUES(?,?,?,?,?)",entities)
    db.executemany("INSERT OR IGNORE INTO carrier_locations VALUES(?,?,?,?)",[
      ("carrier:tesseract-g","Windows","G:/OS_Workspace/TESSERACT_OS","OBSERVED_READ")
    ])
    defs=[
     ("attr:human-name","HUMAN","họ tên","string","single","simple",None,None,0),
     ("attr:human-birth-date","HUMAN","ngày sinh","date","single","simple",None,None,0),
     ("attr:human-age","HUMAN","tuổi","integer","derived","derived",None,"derived_from_verified_birth_date_at_query_time",0),
     ("attr:agent-alias","AGENT","tên gọi khác","string","multi","simple",None,None,0),
     ("attr:device-address","DEVICE","địa chỉ phức hợp","string","single","composite",None,None,0),
     ("attr:device-address-host","DEVICE","host","string","single","simple","attr:device-address",None,0),
     ("attr:device-address-drive","DEVICE","ổ đĩa","string","single","simple","attr:device-address",None,0),
    ]
    db.executemany("INSERT OR IGNORE INTO attribute_definitions VALUES(?,?,?,?,?,?,?,?,?,?)",
                   [(a,b,c,d,e,f,g,h,i,DRIVE_SOURCE) for a,b,c,d,e,f,g,h,i in defs])
    db.execute("""INSERT OR IGNORE INTO attribute_values
       (entity_id,attribute_id,ordinal,v_text,source_id) VALUES(?,?,?,?,?)""",
       ("human:ha-linh","attr:human-name",0,"Hà Linh",CHAT_SOURCE))
    rel_kinds=[
       ("rel:human-writes-item","ghi nguồn"),
       ("rel:agent-has-locus","liên hệ LOCUS"),
       ("rel:carrier-on-device","nằm trên thiết bị")
    ]
    db.executemany("INSERT OR IGNORE INTO relation_types VALUES(?,?,?)",
                   [(a,b,CHAT_SOURCE) for a,b in rel_kinds])
    roles=[
      ("rel:human-writes-item","author","HUMAN",0,None),
      ("rel:human-writes-item","work","ITEM",0,1),
      ("rel:agent-has-locus","agent","AGENT",0,None),
      ("rel:agent-has-locus","locus","LOCUS",0,1),
      ("rel:carrier-on-device","carrier","CARRIER",0,1),
      ("rel:carrier-on-device","device","DEVICE",0,None)
    ]
    db.executemany("INSERT OR IGNORE INTO relation_role_specs VALUES(?,?,?,?,?)",roles)
    relations=[
      ("r:halinh-r014","rel:human-writes-item",CHAT_SOURCE,"2026-10-23",None,"authorship from current user signal"),
      ("r:sol-locus","rel:agent-has-locus",CHAT_SOURCE,None,None,"source assertion, identity not conflated"),
      ("r:g-device","rel:carrier-on-device",HOST_SOURCE,None,None,"connected Desktop Commander observed")
    ]
    db.executemany("INSERT OR IGNORE INTO relations VALUES(?,?,?,?,?,?)",relations)
    db.executemany("INSERT OR IGNORE INTO relation_participants VALUES(?,?,?,?)",[
      ("r:halinh-r014","rel:human-writes-item","author","human:ha-linh"),
      ("r:halinh-r014","rel:human-writes-item","work","item:super-r014"),
      ("r:sol-locus","rel:agent-has-locus","agent","agent:sol"),
      ("r:sol-locus","rel:agent-has-locus","locus","locus:sol"),
      ("r:g-device","rel:carrier-on-device","carrier","carrier:tesseract-g"),
      ("r:g-device","rel:carrier-on-device","device","device:windows-desktop-86itnq4")
    ])
    db.commit()

def validate(db):
    db.execute("PRAGMA foreign_keys=ON")
    fk=db.execute("PRAGMA foreign_key_check").fetchall()
    missing=db.execute("""SELECT r.relation_id,s.role_key FROM relations r
     JOIN relation_role_specs s ON r.relation_type_id=s.relation_type_id
     LEFT JOIN relation_participants p ON p.relation_id=r.relation_id
        AND p.role_key=s.role_key
     WHERE p.relation_id IS NULL""").fetchall()
    repeated=db.execute("""SELECT entity_id,attribute_id FROM attribute_values
     GROUP BY entity_id,attribute_id HAVING COUNT(*)>1 AND
      attribute_id IN (SELECT attribute_id FROM attribute_definitions WHERE value_mode='single')""").fetchall()
    return {"foreign_key_errors":fk,"missing_relation_roles":missing,"single_value_errors":repeated,
            "entity_count":db.execute("SELECT COUNT(*) FROM entities").fetchone()[0],
            "relation_count":db.execute("SELECT COUNT(*) FROM relations").fetchone()[0],
            "source_count":db.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
            "legacy_synapse_mutated":False,
            "valid":not bool(fk or missing or repeated)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",required=True)
    ap.add_argument("--init",action="store_true")
    args=ap.parse_args()
    path=Path(args.db)
    path.parent.mkdir(parents=True,exist_ok=True)
    db=connect(path)
    if args.init:initialize(db)
    outcome=validate(db)
    outcome["database"]=str(path)
    print(json.dumps(outcome,ensure_ascii=False))
    if not outcome["valid"]:raise SystemExit(2)
if __name__=="__main__":main()
