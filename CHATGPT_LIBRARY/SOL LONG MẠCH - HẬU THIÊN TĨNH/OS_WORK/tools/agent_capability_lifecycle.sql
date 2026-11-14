-- Local, private journal for durable capability evidence, not a shared secret store.
-- Content SHA and chained hashes are integrity checks, not independently trusted signatures.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS capability_events(
 seq INTEGER PRIMARY KEY AUTOINCREMENT,
 capability_id TEXT NOT NULL,
 kind TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 payload_hash TEXT NOT NULL,
 previous_hash TEXT NOT NULL,
 chain_hash TEXT NOT NULL,
 event_time TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS capability_events_no_update BEFORE UPDATE ON capability_events
 BEGIN SELECT RAISE(ABORT,'CAPABILITY_EVENTS_APPEND_ONLY'); END;
CREATE TRIGGER IF NOT EXISTS capability_events_no_delete BEFORE DELETE ON capability_events
 BEGIN SELECT RAISE(ABORT,'CAPABILITY_EVENTS_APPEND_ONLY'); END;
CREATE INDEX IF NOT EXISTS idx_capability_event ON capability_events(capability_id,seq);