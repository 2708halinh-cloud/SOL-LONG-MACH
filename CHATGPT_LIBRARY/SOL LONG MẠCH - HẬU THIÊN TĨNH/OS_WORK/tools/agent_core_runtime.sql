-- Same DDL embedded in agent_core_runtime.py; use Python CoreJournal to enforce invariants.
-- SQLite runtime journal is local/authorized private storage. Do not commit .db files.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY,global_goal TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE','PAUSED','COMPLETED','FAILED')),created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS agenda_steps(step_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,step_index INTEGER NOT NULL,title TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING','IN_PROGRESS','DONE','FAILED','ROLLBACK')),evidence_artifact TEXT,error_log TEXT,FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE,UNIQUE(run_id,step_index));
CREATE TABLE IF NOT EXISTS journal_entries(entry_id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT NOT NULL,step_id TEXT,actor TEXT NOT NULL,action_type TEXT NOT NULL,payload_json TEXT NOT NULL,provenance_hash TEXT NOT NULL,previous_hash TEXT NOT NULL,chain_hash TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(run_id) REFERENCES runs(run_id),FOREIGN KEY(step_id) REFERENCES agenda_steps(step_id));
CREATE TRIGGER IF NOT EXISTS journal_no_update BEFORE UPDATE ON journal_entries BEGIN SELECT RAISE(ABORT,'JOURNAL_APPEND_ONLY'); END;
CREATE TRIGGER IF NOT EXISTS journal_no_delete BEFORE DELETE ON journal_entries BEGIN SELECT RAISE(ABORT,'JOURNAL_APPEND_ONLY'); END;
CREATE TABLE IF NOT EXISTS checkpoints(checkpoint_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,step_index INTEGER NOT NULL,full_state_snapshot TEXT NOT NULL,checksum TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE);
CREATE INDEX IF NOT EXISTS idx_agenda_run ON agenda_steps(run_id,step_index);
CREATE INDEX IF NOT EXISTS idx_journal_run ON journal_entries(run_id,entry_id);
CREATE INDEX IF NOT EXISTS idx_checkpoints_run ON checkpoints(run_id,step_index);