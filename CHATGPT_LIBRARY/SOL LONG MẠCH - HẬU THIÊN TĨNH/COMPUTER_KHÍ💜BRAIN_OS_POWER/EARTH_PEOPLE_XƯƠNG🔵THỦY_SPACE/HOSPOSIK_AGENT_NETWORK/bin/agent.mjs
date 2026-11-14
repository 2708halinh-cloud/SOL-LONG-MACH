#!/usr/bin/env node
import {readFileSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';

const dir=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const address=process.env.HOSPOSIK_URL||'http://127.0.0.1:8788';
const u=new URL(address);
if(u.protocol!=='http:'||u.hostname!=='127.0.0.1')throw Error('Client only supports the local loopback HOSPOSIK runtime');
const [command,...args]=process.argv.slice(2);
const headers={'content-type':'application/json'};
if(command!=='health'){
 const path=process.env.HOSPOSIK_TOKEN_FILE||join(dir,'data','agent.token');
 headers.authorization='Bearer '+readFileSync(path,'utf8').trim();
}
async function request(path,body){
 const result=await fetch(address+path,{
  method:body===undefined?'GET':'POST',
  headers,
  ...(body===undefined?{}:{body:JSON.stringify(body)}),
  signal:AbortSignal.timeout(10000)
 });
 const reply=await result.json();
 if(!result.ok)throw Error(result.status+': '+(reply.error||'request failed'));
 return reply;
}
function checkAgent(id){
 if(typeof id!=='string'||!/^[a-z][a-z0-9_-]{1,62}$/.test(id))throw Error('Invalid agent name');
 return id;
}
async function register(agent){
 return request('/v1/agents/register',{agent:checkAgent(agent),capabilities:['memory','messages','routing']});
}
async function main(){
 switch(command){
  case 'health':
   return request('/health');
  case 'register':
   return register(args[0]);
  case 'agents':
   return request('/v1/agents');
  case 'remember': {
   const [agent,kind,...words]=args;
   if(!kind||words.length===0)throw Error('Usage: remember <agent> <kind> <text ...>');
   await register(agent);
   const data=await request('/v1/memory/events',{agent,kind,text:words.join(' ')});
   return {durable:data.durable,id:data.event.id,agent,kind:data.event.kind,created_at:data.event.created_at};
  }
  case 'history': {
   const [agent,after='0']=args;
   checkAgent(agent);
   return request('/v1/memory/events?agent='+encodeURIComponent(agent)+'&after='+Number(after));
  }
  case 'send': {
   const [from,to,...json]=args;
   checkAgent(to);await register(from);
   if(!json.length)throw Error('Usage: send <from> <to> <JSON payload>');
   return request('/v1/route',{from,to,payload:JSON.parse(json.join(' '))});
  }
  case 'inbox': {
   const agent=checkAgent(args[0]);
   return request('/v1/inbox?agent='+encodeURIComponent(agent));
  }
  case 'ack': {
   const [agent,id]=args;
   checkAgent(agent);
   return request('/v1/ack',{agent,id:Number(id)});
  }
  default: throw Error('Usage: node bin/agent.mjs {health|register|agents|remember|history|send|inbox|ack} ...');
 }
}
main().then(value=>console.log(JSON.stringify(value,null,2))).catch(err=>{console.error(err.message);process.exitCode=1;});