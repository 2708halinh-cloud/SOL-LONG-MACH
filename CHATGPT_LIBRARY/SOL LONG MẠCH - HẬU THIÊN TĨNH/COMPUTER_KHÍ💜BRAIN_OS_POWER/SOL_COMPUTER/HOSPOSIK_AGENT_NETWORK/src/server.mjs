import {DatabaseSync} from 'node:sqlite';
import {createServer} from 'node:http';
import {createSocket} from 'node:dgram';
import {readFileSync, writeFileSync, mkdirSync, existsSync, chmodSync} from 'node:fs';
import {join, resolve} from 'node:path';
import {randomBytes, timingSafeEqual} from 'node:crypto';
import dnsPacket from 'dns-packet';

const host = '127.0.0.1';
const httpPort = Number(process.env.HOSPOSIK_HTTP_PORT ?? '8788');
const dnsPort = Number(process.env.HOSPOSIK_DNS_PORT ?? '15353');
const base = resolve(process.env.HOSPOSIK_DATA_DIR ?? './data');
mkdirSync(base, {recursive:true, mode:0o700});
const tokenPath = resolve(process.env.HOSPOSIK_TOKEN_FILE ?? join(base,'agent.token'));
if (!existsSync(tokenPath)) writeFileSync(tokenPath,randomBytes(32).toString('hex')+'\n',{mode:0o600,flag:'wx'});
try {chmodSync(tokenPath,0o600);}catch {}
const token = readFileSync(tokenPath,'utf8').trim();
if (token.length<32) throw Error('A token with at least 32 characters is required');
const db = new DatabaseSync(join(base,'memory.sqlite'));
db.exec('PRAGMA journal_mode = WAL; PRAGMA synchronous = FULL; PRAGMA busy_timeout = 5000;');
db.exec(
 'CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT NOT NULL, kind TEXT NOT NULL, text TEXT NOT NULL, meta TEXT NOT NULL, created_at TEXT NOT NULL, dedupe TEXT, UNIQUE(agent,dedupe));'+
 'CREATE TABLE IF NOT EXISTS agents (agent TEXT PRIMARY KEY, capabilities TEXT NOT NULL, last_seen TEXT NOT NULL);'+
 'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, destination TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL, ack_at TEXT);'
);
const listAgents = db.prepare('SELECT agent,capabilities,last_seen FROM agents ORDER BY agent LIMIT 200');
const addAgent = db.prepare('INSERT INTO agents(agent,capabilities,last_seen) VALUES (?,?,?) ON CONFLICT(agent) DO UPDATE SET capabilities=excluded.capabilities,last_seen=excluded.last_seen');
const findAgent = db.prepare('SELECT agent FROM agents WHERE agent=?');
const addMemory = db.prepare('INSERT OR IGNORE INTO memory(agent,kind,text,meta,created_at,dedupe) VALUES (?,?,?,?,?,?)');
const findMemoryDedupe = db.prepare('SELECT * FROM memory WHERE agent=? AND dedupe=?');
const findMemory = db.prepare('SELECT * FROM memory WHERE id=?');
const recentMemory = db.prepare('SELECT * FROM memory WHERE id>? AND agent=? ORDER BY id LIMIT 100');
const addMessage = db.prepare('INSERT INTO messages(source,destination,payload,created_at) VALUES (?,?,?,?)');
const findMessages = db.prepare('SELECT * FROM messages WHERE destination=? AND id>? AND ack_at IS NULL ORDER BY id LIMIT 100');
const ackMessage = db.prepare('UPDATE messages SET ack_at=? WHERE id=? AND destination=? AND ack_at IS NULL');
const maxMemory = db.prepare('SELECT COALESCE(MAX(id),0) AS last_id FROM memory');
const eventStreams = new Set();
const JSON_HEADERS={'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff'};
function send(res,status,object){if(res.writableEnded)return;res.writeHead(status,JSON_HEADERS);res.end(JSON.stringify(object));}
function authorize(req){
 const sent=req.headers.authorization?.replace(/^Bearer /i,'')??'';
 const a=Buffer.from(sent),b=Buffer.from(token);
 return a.length===b.length && timingSafeEqual(a,b);
}
function validAgent(value){return typeof value==='string' && /^[a-z][a-z0-9_-]{1,62}$/.test(value);}
function trimEvent(e){return {id:e.id,agent:e.agent,kind:e.kind,text:e.text,meta:JSON.parse(e.meta),created_at:e.created_at};}
async function bodyJson(req){
 const chunks=[];let length=0;
 for await (const part of req) {length+=part.length;if(length>128*1024)throw Error('body_exceeds_128KiB');chunks.push(part);}
 const object=JSON.parse(Buffer.concat(chunks).toString('utf8'));
 if(!object||typeof object!=='object'||Array.isArray(object))throw Error('object_required');
 return object;
}
function streamEvent(event){
 for(const stream of eventStreams) {
  if(stream.agent===event.agent && event.id>stream.after){
   try{stream.res.write('id: '+event.id+'\nevent: memory\ndata: '+JSON.stringify(event)+'\n\n');stream.after=event.id;}catch {}
  }
 }
}
const http=createServer(async(req,res)=>{
 try {
  const url=new URL(req.url,'http://127.0.0.1');
  if(req.method==='GET'&&url.pathname==='/health'){
   return send(res,200,{service:'HOSPOSIK_AGENT_NETWORK',status:'ready',dns_zone:'hosposik.test',memory:'sqlite_wal_full',last_memory_id:maxMemory.get().last_id,local_only:true});
  }
  if(!authorize(req))return send(res,401,{error:'unauthorized'});
  if(req.method==='POST'&&url.pathname==='/v1/agents/register'){
   const v=await bodyJson(req);
   if(!validAgent(v.agent))return send(res,400,{error:'invalid_agent'});
   const cap=Array.isArray(v.capabilities)?v.capabilities:[];
   if(cap.length>24||cap.some(x=>typeof x!=='string'||x.length>64))return send(res,400,{error:'invalid_capabilities'});
   const now=new Date().toISOString();
   addAgent.run(v.agent,JSON.stringify(cap),now);
   return send(res,200,{registered:v.agent,last_seen:now});
  }
  if(req.method==='GET'&&url.pathname==='/v1/agents'){
   const now=Date.now();
   return send(res,200,{agents:listAgents.all().map(v=>({agent:v.agent,capabilities:JSON.parse(v.capabilities),last_seen:v.last_seen,online:now-Date.parse(v.last_seen)<90000}))});
  }
  if(req.method==='POST'&&url.pathname==='/v1/memory/events'){
   const v=await bodyJson(req);
   if(!validAgent(v.agent)||typeof v.kind!=='string'||v.kind.length>64||!v.kind||
      typeof v.text!=='string'||Buffer.byteLength(v.text)>16384||
      (v.dedupe!==undefined&&(typeof v.dedupe!=='string'||v.dedupe.length>96)))
     return send(res,400,{error:'invalid_event'});
   if(!findAgent.get(v.agent))return send(res,404,{error:'agent_not_registered'});
   const meta=(v.meta&&typeof v.meta==='object'&&!Array.isArray(v.meta))?v.meta:{};
   const metaStr=JSON.stringify(meta);if(Buffer.byteLength(metaStr)>8192)return send(res,400,{error:'meta_too_large'});
   const now=new Date().toISOString();
   const result=addMemory.run(v.agent,v.kind,v.text,metaStr,now,v.dedupe??null);
   const event=(result.changes?findMemory.get(Number(result.lastInsertRowid)):findMemoryDedupe.get(v.agent,v.dedupe));
   if(result.changes)streamEvent(trimEvent(event));
   return send(res,result.changes?201:200,{durable:true,deduplicated:result.changes===0,event:trimEvent(event)});
  }
  if(req.method==='GET'&&url.pathname==='/v1/memory/events'){
   const agent=url.searchParams.get('agent');if(!validAgent(agent))return send(res,400,{error:'invalid_agent'});
   const after=Math.max(0,Number(url.searchParams.get('after')||0));if(!Number.isSafeInteger(after))return send(res,400,{error:'invalid_cursor'});
   return send(res,200,{events:recentMemory.all(after,agent).map(trimEvent)});
  }
  if(req.method==='GET'&&url.pathname==='/v1/memory/stream'){
   const agent=url.searchParams.get('agent');if(!validAgent(agent))return send(res,400,{error:'invalid_agent'});
   const after=Math.max(0,Number(url.searchParams.get('after')||req.headers['last-event-id']||0));
   if(!Number.isSafeInteger(after))return send(res,400,{error:'invalid_cursor'});
   res.writeHead(200,{'content-type':'text/event-stream','cache-control':'no-cache, no-transform','connection':'keep-alive','x-accel-buffering':'no'});
   const listener={agent,after,res};eventStreams.add(listener);
   for(const e of recentMemory.all(after,agent)){const ev=trimEvent(e);res.write('id: '+ev.id+'\nevent: memory\ndata: '+JSON.stringify(ev)+'\n\n');listener.after=ev.id;}
   const pulse=setInterval(()=>{if(!res.writableEnded)res.write(': heartbeat\n\n');},20000);
   req.on('close',()=>{clearInterval(pulse);eventStreams.delete(listener);});
   return;
  }
  if(req.method==='POST'&&url.pathname==='/v1/route'){
   const v=await bodyJson(req);
   if(!validAgent(v.from)||!validAgent(v.to)||!findAgent.get(v.from)||!findAgent.get(v.to))
     return send(res,400,{error:'unregistered_agent'});
   const payload=JSON.stringify(v.payload??null);
   if(Buffer.byteLength(payload)>65536)return send(res,400,{error:'payload_too_large'});
   const now=new Date().toISOString(),out=addMessage.run(v.from,v.to,payload,now);
   return send(res,201,{queued:true,message_id:Number(out.lastInsertRowid),from:v.from,to:v.to,created_at:now});
  }
  if(req.method==='GET'&&url.pathname==='/v1/inbox'){
   const agent=url.searchParams.get('agent');if(!validAgent(agent))return send(res,400,{error:'invalid_agent'});
   const after=Math.max(0,Number(url.searchParams.get('after')||0));if(!Number.isSafeInteger(after))return send(res,400,{error:'invalid_cursor'});
   return send(res,200,{messages:findMessages.all(agent,after).map(e=>({id:e.id,from:e.source,to:e.destination,payload:JSON.parse(e.payload),created_at:e.created_at}))});
  }
  if(req.method==='POST'&&url.pathname==='/v1/ack'){
   const v=await bodyJson(req);
   if(!validAgent(v.agent)||!Number.isSafeInteger(v.id)||v.id<1)return send(res,400,{error:'invalid_ack'});
   const result=ackMessage.run(new Date().toISOString(),v.id,v.agent);
   return send(res,result.changes?200:404,{acknowledged:result.changes>0});
  }
  return send(res,404,{error:'not_found'});
 }catch(e){return send(res,400,{error:e.message||'bad_request'});}
});
const known=new Set(['router.hosposik.test','memory.hosposik.test','agent.hosposik.test','hosposik.test']);
const udp=createSocket('udp4');
udp.on('message',(message,rinfo)=>{
 try{
  const query=dnsPacket.decode(message);
  const answers=[];let knownQuestion=false;
  for(const q of query.questions??[]){
   const qname=String(q.name).replace(/\.$/,'').toLowerCase(),typ=q.type;
   if(known.has(qname)){
    knownQuestion=true;
    if(typ==='A'||typ==='ANY')answers.push({name:q.name,type:'A',class:'IN',ttl:30,data:host});
    if(typ==='TXT')answers.push({name:q.name,type:'TXT',class:'IN',ttl:30,data:['SOL HOSPOSIK local agent router; HTTP 8788']});
   }
   if((qname==='_agent._tcp.hosposik.test'||qname==='_memory._tcp.hosposik.test')&&(typ==='SRV'||typ==='ANY')){
    knownQuestion=true;answers.push({name:q.name,type:'SRV',class:'IN',ttl:30,data:{priority:0,weight:0,port:http.address()?.port||httpPort,target:'router.hosposik.test'}});
   }
  }
  const response=dnsPacket.encode({type:'response',id:query.id,flags:dnsPacket.AUTHORITATIVE_ANSWER|(knownQuestion?0:3),questions:query.questions??[],answers});
  udp.send(response,rinfo.port,rinfo.address);
 }catch {}
});
udp.on('error',(err)=>{console.error('DNS_ERROR',err.code);});
http.listen(httpPort,host,()=>{
 udp.bind(dnsPort,host,()=>{
  console.log(JSON.stringify({event:'HOSPOSIK_READY',host,http_port:http.address().port,dns_port:udp.address().port,dns_zone:'hosposik.test',database:'sqlite_wal_full',token_file:tokenPath}));
 });
});
let closing=false;
async function shutdown(){
 if(closing)return;closing=true;
 for(const listener of eventStreams){try{listener.res.end();}catch{}}
 await new Promise(resolve=>http.close(()=>resolve()));
 await new Promise(resolve=>udp.close(()=>resolve()));
 db.close();
}
process.on('SIGTERM',()=>void shutdown());
process.on('SIGINT',()=>void shutdown());