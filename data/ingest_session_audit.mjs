import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';

const root = 'G:\\OS_Workspace\\data';
const source = path.join(root, 'ChatGPT-Xác minh kết nối thiết bị-20261103-2055.json');
const dbPath = path.join(root, 'ChatGPT-Xác minh kết nối thiết bị-20261103-2055.sqlite');
const taskPath = path.join(root, 'ChatGPT-Xác minh kết nối thiết bị-Pending-Actions.json');
const auditPath = path.join(root, 'ChatGPT-Xác minh kết nối thiết bị-Agent-Audit.jsonl');
const raw = fs.readFileSync(source);
const sourceHash = crypto.createHash('sha256').update(raw).digest('hex');
const doc = JSON.parse(raw.toString('utf8'));
if (!Array.isArray(doc.messages)) throw new Error('messages[] missing');

const db = new DatabaseSync(dbPath);
db.exec("PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;" +
"CREATE TABLE IF NOT EXISTS source_files (source_hash TEXT PRIMARY KEY, source_path TEXT NOT NULL, imported_at TEXT NOT NULL, source_bytes INTEGER NOT NULL, message_count INTEGER NOT NULL);" +
"CREATE TABLE IF NOT EXISTS messages (source_hash TEXT NOT NULL, source_index INTEGER NOT NULL, message_id TEXT NOT NULL, message_id_origin TEXT NOT NULL, role TEXT NOT NULL, source_role TEXT NOT NULL, timestamp TEXT, model TEXT, content TEXT NOT NULL, raw_message_json TEXT NOT NULL, PRIMARY KEY(source_hash,source_index), FOREIGN KEY(source_hash) REFERENCES source_files(source_hash));" +
"CREATE TABLE IF NOT EXISTS pending_actions (action_id TEXT PRIMARY KEY, title TEXT NOT NULL, owner TEXT NOT NULL, status TEXT NOT NULL, acceptance_criteria TEXT NOT NULL, source_hash TEXT NOT NULL, source_index INTEGER NOT NULL, source_excerpt TEXT NOT NULL, created_at TEXT NOT NULL);" +
"CREATE TABLE IF NOT EXISTS audit_events (event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, source_hash TEXT NOT NULL, source_index INTEGER, evidence TEXT NOT NULL, recorded_at TEXT NOT NULL);" +
"CREATE INDEX IF NOT EXISTS idx_messages_role_time ON messages(role,timestamp);" +
"CREATE INDEX IF NOT EXISTS idx_actions_status ON pending_actions(status);" +
"CREATE INDEX IF NOT EXISTS idx_audit_source ON audit_events(source_hash,source_index);");

const exists = db.prepare('SELECT 1 FROM source_files WHERE source_hash=?').get(sourceHash);
if (!exists) {
 const now = new Date().toISOString();
 db.prepare('INSERT INTO source_files VALUES(?,?,?,?,?)').run(sourceHash,source,now,raw.length,doc.messages.length);
 const insert = db.prepare('INSERT INTO messages VALUES(?,?,?,?,?,?,?,?,?,?)');
 doc.messages.forEach((m,i) => {
  const role = m.role === 'Prompt' ? 'user' : m.role === 'Response' ? 'assistant' : m.role;
  const id = 'derived:' + crypto.createHash('sha256').update(sourceHash+':'+i).digest('hex').slice(0,24);
  insert.run(sourceHash,i,id,'derived_from_source_hash_and_index',role,m.role,m.time??null,m.model??null,m.say??'',JSON.stringify(m));
 });
}
const actionDefs = [
 ['PR53-CLOSE','Đóng PR #53, không merge','SOL / GitHub Operations','closed; merged=false; readback PR xác nhận','đóng PR #53'],
 ['WINDOWS-CONNECT','Xác minh kết nối Windows','SOL / Device Operations','Device ID, trạng thái online, đọc/ghi và readback','Windows'],
 ['ANDROID-CONNECT','Xác minh kết nối Android','SOL / Device Operations','Device ID hiện hành, nhận diện thiết bị và read/write readback','Android'],
 ['ALL-AGENT-RECOVERY','Truy hồi kho ALL AGENT','SOL / Agent Recovery','Danh mục nguồn, đường dẫn, phiên bản, quan hệ và provenance','ALL AGENT'],
 ['MASTER-TEACHER-RECOVERY','Truy hồi nhóm 0000_THE_MASTER_TEACHER','SOL / Knowledge Recovery','Nguồn gốc, nội dung, dấu sửa và lịch sử được đối chiếu','0000_THE_MASTER_TEACHER'],
 ['MATRIX-152-RECOVERY','Khôi phục 16 Ma trận gốc và 152 ITEM','SOL / Matrix Reconciliation','Đối chiếu đủ 16 ma trận/152 ITEM với nguồn và quan hệ gốc','152 ITEM']
];
const lastPromptIndex = doc.messages.map((m,i)=>({m,i})).filter(x=>x.m.role==='Prompt' && /Đóng PR #53|152 ITEM|ALL AGENT/.test(x.m.say||'')).at(-1)?.i ?? doc.messages.length-1;
const fallbackExcerpt = doc.messages[lastPromptIndex]?.say ?? '';
const upsert = db.prepare('INSERT OR IGNORE INTO pending_actions VALUES(?,?,?,?,?,?,?,?,?)');
for (const [id,title,owner,criteria,needle] of actionDefs) {
 const idx = doc.messages.findIndex(m=>(m.say||'').includes(needle));
 upsert.run(id,title,owner,'PENDING',criteria,sourceHash,idx>=0?idx:lastPromptIndex,idx>=0?doc.messages[idx].say:fallbackExcerpt,new Date().toISOString());
}
const auditEvents = [
 ['SOURCE_INGESTED',{source,source_hash:sourceHash,bytes:raw.length,messages:doc.messages.length}],
 ['ROLE_NORMALIZATION',{mapping:{Prompt:'user',Response:'assistant'},source_role_preserved:true}],
 ['TASK_EXTRACTION',{actions:actionDefs.map(x=>x[0]),all_status:'PENDING'}],
 ['EXECUTION_GAP_AUDIT',{source_contains_repeated_question_marks:true,source_contains_admission_no_subagent_started:true,source_does_not_prove_PR_closed:true,source_does_not_prove_152_items_recovered:true}]
];
const stream = fs.createWriteStream(auditPath,{flags:'a',encoding:'utf8'});
for (const [type,evidence] of auditEvents) {
 const eventId=crypto.createHash('sha256').update(sourceHash+':'+type).digest('hex');
 const recordedAt=new Date().toISOString();
 db.prepare('INSERT OR IGNORE INTO audit_events VALUES(?,?,?,?,?,?)').run(eventId,type,sourceHash,lastPromptIndex,JSON.stringify(evidence),recordedAt);
 stream.write(JSON.stringify({event_id:eventId,event_type:type,source_hash:sourceHash,source_index:lastPromptIndex,evidence,recorded_at:recordedAt})+'\\n');
}
stream.end();
const tasks=db.prepare('SELECT action_id,title,owner,status,acceptance_criteria,source_index FROM pending_actions ORDER BY action_id').all();
fs.writeFileSync(taskPath,JSON.stringify({source,source_hash:sourceHash,generated_at:new Date().toISOString(),tasks},null,2),'utf8');
const count=q=>db.prepare(q).get(sourceHash).n;
const replay=db.prepare('SELECT source_index,role,source_role FROM messages WHERE source_hash=? ORDER BY source_index').all(sourceHash);
if(replay.length!==doc.messages.length||replay.some((r,i)=>r.source_index!==i)) throw new Error('REPLAY_ORDER_INTEGRITY_FAILED');
console.log(JSON.stringify({
 source_hash:sourceHash,source_bytes:raw.length,source_messages:doc.messages.length,
 imported_messages:count('SELECT count(*) AS n FROM messages WHERE source_hash=?'),
 user_messages:count("SELECT count(*) AS n FROM messages WHERE source_hash=? AND role='user'"),
 assistant_messages:count("SELECT count(*) AS n FROM messages WHERE source_hash=? AND role='assistant'"),
 pending_actions:count("SELECT count(*) AS n FROM pending_actions WHERE source_hash=? AND status='PENDING'"),
 audit_events:count('SELECT count(*) AS n FROM audit_events WHERE source_hash=?'),
 replay_order_integrity:'PASS',database:dbPath,task_queue:taskPath,audit_log:auditPath
},null,2));
db.close();
