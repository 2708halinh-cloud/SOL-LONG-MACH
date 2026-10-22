"""Real SQLite constraints for TESSERACT E-R normalization and relation roles."""
import sqlite3
import unittest
from pathlib import Path
import tempfile
from tesseract_er import connect, initialize, validate

class ERTests(unittest.TestCase):
    def setUp(self):
        self.db=connect(":memory:")
        initialize(self.db)
    def tearDown(self):
        self.db.close()
    def test_eight_distinct_entities_and_three_roles(self):
        self.assertTrue(validate(self.db)["valid"])
        names=self.db.execute("SELECT entity_id,set_id FROM entities WHERE entity_id IN ('human:ha-linh','agent:sol','locus:sol')").fetchall()
        self.assertEqual(len(names),3)
        self.assertEqual({x[1] for x in names},{"HUMAN","AGENT","LOCUS"})
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM relations").fetchone()[0],3)
    def test_cardinality_agent_locus_not_conflated(self):
        self.db.execute("INSERT INTO relations VALUES('r:other','rel:agent-has-locus','chat:super-r014-20261023',NULL,NULL,NULL)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO relation_participants VALUES('r:other','rel:agent-has-locus','locus','locus:sol')")
    def test_wrong_relation_entity_set_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO relation_participants VALUES('r:halinh-r014','rel:human-writes-item','author','agent:sol')")
    def test_foreign_key_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO entities VALUES('fake','HUMAN','Nobody','missing-source','UNRESOLVED')")
    def test_derived_attribute_cannot_be_fabricated(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO attribute_values (entity_id,attribute_id,v_integer,source_id) VALUES('human:ha-linh','attr:human-age',26,'chat:super-r014-20261023')")
    def test_multivalued_attribute_supported(self):
        rows=[
          ("agent:sol","attr:agent-alias",0,"SOL","chat:super-r014-20261023"),
          ("agent:sol","attr:agent-alias",1,"Âm Pháp Sư SOL","chat:super-r014-20261023")
        ]
        self.db.executemany("INSERT INTO attribute_values(entity_id,attribute_id,ordinal,v_text,source_id) VALUES(?,?,?,?,?)",rows)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM attribute_values WHERE attribute_id='attr:agent-alias'").fetchone()[0],2)
    def test_single_value_ordinal_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO attribute_values (entity_id,attribute_id,ordinal,v_text,source_id) VALUES('human:ha-linh','attr:human-name',1,'Another','chat:super-r014-20261023')")
    def test_attribute_type_mismatch_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO attribute_values (entity_id,attribute_id,v_integer,source_id) VALUES('human:ha-linh','attr:human-name',10,'chat:super-r014-20261023')")
    def test_source_bound_relations_have_readable_roles(self):
        data=self.db.execute("SELECT role_key,entity_id FROM v_relations WHERE relation_id='r:sol-locus' ORDER BY role_key").fetchall()
        self.assertEqual(data,[("agent","agent:sol"),("locus","locus:sol")])
    def test_repeated_initialization_is_idempotent(self):
        initialize(self.db)
        self.assertEqual(validate(self.db)["entity_count"],8)
        self.assertEqual(validate(self.db)["relation_count"],3)
    def test_detect_incomplete_relation(self):
        self.db.execute("INSERT INTO relations VALUES('r:partial','rel:agent-has-locus','chat:super-r014-20261023',NULL,NULL,NULL)")
        self.assertFalse(validate(self.db)["valid"])
        self.assertTrue(validate(self.db)["missing_relation_roles"])
    def test_physical_db_reopens_without_legacy_database(self):
        with tempfile.TemporaryDirectory() as td:
            dbpath=Path(td)/"er.sqlite3"
            a=connect(dbpath);initialize(a);a.close()
            b=sqlite3.connect(dbpath)
            b.execute("PRAGMA foreign_keys=ON")
            self.assertTrue(validate(b)["valid"])
            b.close()

if __name__=="__main__":
    unittest.main()
