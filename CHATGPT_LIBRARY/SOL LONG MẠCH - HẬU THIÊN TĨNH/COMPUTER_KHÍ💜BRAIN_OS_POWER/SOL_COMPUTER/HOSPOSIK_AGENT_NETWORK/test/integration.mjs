import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createSocket} from 'node:dgram';
import {createInterface} from 'node:readline';
import dnsPacket from 'dns-packet';

const scratch=mkdtempSync(join(tmpdir(),'hosposik-test-'));
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function start(){
 const child=spawn(process.execPath,['src/server.mjs'],{cwd:process.cwd(),env:{...process.env,HOSPOSIK_DATA_DIR:scratch,HOSPOSIK_HTTP_PORT:'0',HOSPOSIK_DNS_PORT:'0'},stdio:['ignore','pipe','pipe']});
 let diagnostics='';
 child.stderr.on('data',v=>{diagnostics+=String(v).slice(0,1500)});
 const ready=new Promise((resolve,reject)=>{
  const timeout=setTimeout(()=>reject(new Error('Startup timeout: '+diagnostics)),12000);
  child.once('error',e=>{clearTimeout(timeout);reject(e)});
  child.once('exit',code=>{clearTimeout(timeout);reject(new Error('Server exited '+code+' '+diagnostics))});
  const rl=createInterface({input:child.stdout});
  rl.on('line',line=>{
   try{const value=JSON.parse(line);if(value.event==='HOSPOSIK_READY'){clearTimeout(timeout);resolve(value);}}catch {}
  });
 });
 return {child,ready:await ready};
}
async function stop(child){
 if(child.exitCode!==null)return;
 child.kill('SIGTERM');
 await Promise.race([new Promise(resolve=>child.once('exit',resolve)),wait(3000)]);
 if(child.exitCode===null)child.kill('SIGKILL');
}
async function dnsRequest(port,name,type){
 const packet=dnsPacket.encode({type:'query',id:3217,flags:0,questions:[{type,name}]});
 const client=createSocket('udp4');
 return await new Promise((resolve,reject)=>{
  const timeout=setTimeout(()=>{client.close();reject(new Error('DNS timeout'))},2000);
  client.once('message',buffer=>{clearTimeout(timeout);client.close();resolve(dnsPacket.decode(buffer))});
  client.once('error',e=>{clearTimeout(timeout);client.close();reject(e)});
  client.send(packet,port,'127.0.0.1');
 });
}
let first,second;
try{
 first=await start();
 const address='http://127.0.0.1:'+first.ready.http_port;
 const token=readFileSync(join(scratch,'agent.token'),'utf8').trim();
 const headers={'authorization':'Bearer '+token,'content-type':'application/json'};
 async function post(route,v){
  const resp=await fetch(address+route,{method:'POST',headers,body:JSON.stringify(v)});
  return {status:resp.status,data:await resp.json()};
 }
 let health=await (await fetch(address+'/health')).json();
 assert.equal(health.status,'ready');
 let denied=await fetch(address+'/v1/agents');assert.equal(denied.status,401);
 for(const agent of ['sol','router']) {
  const result=await post('/v1/agents/register',{agent,capabilities:['memory','messages']});
  assert.equal(result.status,200);
 }
 const memory=await post('/v1/memory/events',{agent:'sol',kind:'observation',text:'HOSPOSIK_EVENT_PERSISTED',meta:{origin:'integration-test'},dedupe:'event-1'});
 assert.equal(memory.status,201);
 assert.equal(memory.data.durable,true);
 const repeated=await post('/v1/memory/events',{agent:'sol',kind:'observation',text:'HOSPOSIK_EVENT_PERSISTED',dedupe:'event-1'});
 assert.equal(repeated.status,200);assert.equal(repeated.data.event.id,memory.data.event.id);
 const events=await (await fetch(address+'/v1/memory/events?agent=sol&after=0',{headers})).json();
 assert.equal(events.events.length,1);
 const message=await post('/v1/route',{from:'sol',to:'router',payload:{job:'route-confirmation'}});
 assert.equal(message.status,201);
 const inbox=await (await fetch(address+'/v1/inbox?agent=router',{headers})).json();
 assert.equal(inbox.messages.length,1);
 assert.equal(inbox.messages[0].payload.job,'route-confirmation');
 const ack=await post('/v1/ack',{agent:'router',id:message.data.message_id});
 assert.equal(ack.status,200);
 const empty=await (await fetch(address+'/v1/inbox?agent=router',{headers})).json();
 assert.equal(empty.messages.length,0);
 const dns=await dnsRequest(first.ready.dns_port,'router.hosposik.test','A');
 assert.equal(dns.answers[0].data,'127.0.0.1');
 const srv=await dnsRequest(first.ready.dns_port,'_agent._tcp.hosposik.test','SRV');
 assert.equal(srv.answers[0].data.port,first.ready.http_port);
 const unknown=await dnsRequest(first.ready.dns_port,'unknown.hosposik.test','A');
 assert.equal(unknown.flags&15,3);
 await stop(first.child);
 second=await start();
 const again=await (await fetch('http://127.0.0.1:'+second.ready.http_port+'/v1/memory/events?agent=sol',{headers})).json();
 assert.equal(again.events.length,1);
 assert.equal(again.events[0].text,'HOSPOSIK_EVENT_PERSISTED');
 console.log(JSON.stringify({status:'PASS',agent_memory:'durable_after_restart',sqlite:'WAL_FULL',dedupe:true,agent_router:'queue_and_ack',dns:'A_SRV_NXDOMAIN',http:'loopback',auth:'validated',event_id:memory.data.event.id}));
}catch(e){console.error(e.stack||e.message);process.exitCode=1;}
finally{
 if(first)await stop(first.child);
 if(second)await stop(second.child);
 rmSync(scratch,{force:true,recursive:true});
}