-- Additive TESSERACT E-R DDL, sourced from runtime/tesseract_er.py; do not modify legacy Synapse.
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
