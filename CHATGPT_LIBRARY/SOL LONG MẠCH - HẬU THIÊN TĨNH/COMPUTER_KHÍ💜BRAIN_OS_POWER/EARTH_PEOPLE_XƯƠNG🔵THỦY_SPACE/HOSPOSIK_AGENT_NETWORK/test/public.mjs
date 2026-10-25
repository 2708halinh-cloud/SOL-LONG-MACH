import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createInterface} from 'node:readline';

const home=mkdtempSync(join(tmpdir(),'hosposik-public-'));
const env={...process.env,HOSPOSIK_PUBLIC_MODE:'true',HOSPOSIK_DATA_DIR:home,HOSPOSIK_TOKEN:'for-integration-only-32-char-value-xxxxxxxx',PORT:'0'};
const child=spawn(process.execPath,['src/server.mjs'],{env,stdio:['ignore','pipe','pipe']});
const ready=new Promise((resolve,reject)=>{
 const time=setTimeout(()=>reject(Error('HOSPOSIK public startup timeout')),12000);
 child.once('error',e=>{clearTimeout(time);reject(e)});
 child.once('exit',code=>{clearTimeout(time);reject(Error('HOSPOSIK exited '+code))});
 createInterface({input:child.stdout}).on('line',line=>{
  try{const j=JSON.parse(line);if(j.event==='HOSPOSIK_READY'){clearTimeout(time);resolve(j)}}catch{}
 });
});
let receipt;
try{
 receipt=await ready;
 assert.equal(receipt.public_mode,true);
 assert.equal(receipt.dns_port,undefined);
 const addr='http://127.0.0.1:'+receipt.http_port;
 const health=await(await fetch(addr+'/health')).json();
 assert.equal(health.status,'ready');
 assert.equal(health.local_only,false);
 const denied=await fetch(addr+'/v1/agents');
 assert.equal(denied.status,401);
 const headers={'authorization':'Bearer '+env.HOSPOSIK_TOKEN,'content-type':'application/json'};
 const post=async(path,body)=>{
  const r=await fetch(addr+path,{method:'POST',headers,body:JSON.stringify(body)});
  return {status:r.status,data:await r.json()};
 };
 const a=await post('/v1/agents/register',{agent:'gateway',capabilities:['memory']});
 assert.equal(a.status,200);
 const b=await post('/v1/memory/events',{agent:'gateway',kind:'integration',text:'PUBLIC_MODE_TEST'});
 assert.equal(b.status,201);
 const e=await(await fetch(addr+'/v1/memory/events?agent=gateway',{headers})).json();
 assert.equal(e.events.length,1);
 assert.equal(e.events[0].text,'PUBLIC_MODE_TEST');
 console.log(JSON.stringify({status:'PASS',public_mode:true,port:receipt.http_port,health:'ready',auth:'required',memory:'SQLite WAL/FULL'}));
}finally{
 child.kill('SIGTERM');
 await Promise.race([new Promise(res=>child.once('exit',res)),new Promise(res=>setTimeout(res,3000))]);
 if(child.exitCode===null)child.kill('SIGKILL');
 rmSync(home,{force:true,recursive:true});
}
