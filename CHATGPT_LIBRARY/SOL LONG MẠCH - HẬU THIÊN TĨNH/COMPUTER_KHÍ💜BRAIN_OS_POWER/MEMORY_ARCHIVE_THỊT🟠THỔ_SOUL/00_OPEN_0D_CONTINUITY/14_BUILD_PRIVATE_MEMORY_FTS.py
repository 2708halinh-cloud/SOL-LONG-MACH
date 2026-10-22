#!/usr/bin/env python3
"""Offline FTS index for a locally extracted ChatGPT data export.

Usage: python 14_BUILD_PRIVATE_MEMORY_FTS.py RAW_EXPORT_ROOT OUTPUT.sqlite3
Never publish output or raw messages to a public repository.
"""
import argparse, json, pathlib, sqlite3, sys
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source',type=pathlib.Path)
p.add_argument('output',type=pathlib.Path)
a=p.parse_args()
if a.output.exists():p.error('OUTPUT_EXISTS_REFUSE_OVERWRITE')
parts=sorted(a.source.glob('conversations-*.json'))
if not parts:p.error('NO_CONVERSATION_PARTS')
a.output.parent.mkdir(parents=True,exist_ok=True)
db=sqlite3.connect(a.output)
db.executescript('''
CREATE TABLE conversations (conversation_id TEXT PRIMARY KEY,title TEXT,create_time REAL,update_time REAL,part TEXT,nodes INTEGER);
CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT,conversation_id TEXT,node_id TEXT,parent_id TEXT,role TEXT,create_time REAL,part TEXT,body TEXT);
CREATE INDEX msg_conv ON messages(conversation_id);
CREATE INDEX msg_time ON messages(create_time);
CREATE VIRTUAL TABLE messages_search USING fts5(body,content='messages',content_rowid='id',tokenize='unicode61 remove_diacritics 2');
CREATE TRIGGER msg_ai AFTER INSERT ON messages BEGIN
 INSERT INTO messages_search(rowid,body) VALUES(new.id,new.body);
END;
''')
conversation_count=message_count=0
for part in parts:
    docs=json.loads(part.read_text(encoding='utf-8'))
    for c in docs:
        cid=c.get('conversation_id') or c.get('id')
        if not cid:continue
        mapping=c.get('mapping') or {}
        db.execute('INSERT OR IGNORE INTO conversations VALUES(?,?,?,?,?,?)',
                   (cid,c.get('title'),c.get('create_time'),c.get('update_time'),part.name,len(mapping)))
        conversation_count+=1
        for node_id,node in mapping.items():
            msg=node.get('message') if isinstance(node,dict) else None
            if not isinstance(msg,dict):continue
            role=(msg.get('author') or {}).get('role')
            if role not in ('user','assistant'):continue
            md=msg.get('metadata') or {}
            if md.get('channel') in ('analysis','reasoning') or md.get('message_type') in ('analysis','reasoning'):continue
            cont=msg.get('content') or {}
            if cont.get('content_type') in ('thoughts','reasoning'):continue
            parts_text=cont.get('parts') or []
            body='\n'.join(v for v in parts_text if isinstance(v,str))
            if not body and isinstance(cont.get('content'),str):body=cont['content']
            if not body:continue
            db.execute('INSERT INTO messages(conversation_id,node_id,parent_id,role,create_time,part,body) VALUES (?,?,?,?,?,?,?)',
                      (cid,node_id,node.get('parent'),role,msg.get('create_time'),part.name,body))
            message_count+=1
    db.commit()
db.execute('ANALYZE');db.commit();db.close()
print(json.dumps({'conversations':conversation_count,'indexed_messages':message_count,'parts':len(parts),'output':str(a.output)},ensure_ascii=False))
