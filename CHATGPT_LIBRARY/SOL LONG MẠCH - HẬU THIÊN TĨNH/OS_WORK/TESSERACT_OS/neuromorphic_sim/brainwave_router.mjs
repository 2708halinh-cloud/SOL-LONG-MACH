// SOL SNN virtual reflex router. SIMULATION ONLY; no EEG classification or physical actuation.
// Portable ES module, runs in Node/browser without user hardware.
export const createBody = function createBody(){
 return {schema:"SOL_SNN_VIRTUAL/1.0",simulation:true,gate:"BETA",membrane:0,threshold:1,decay:.6,seq:0,action:"VIRTUAL_SAFE_STOP",latest_event_id:null,events:[]};
};
export const tickBody = function tickBody(old,signal){
 if(!old||old.schema!=="SOL_SNN_VIRTUAL/1.0"||old.simulation!==true)throw Error("Unknown body state");
 if(!signal||signal.source_kind!=="SIMULATED_INPUT")return {state:old,action:old.action,event:null,accepted:false,reason:"UNVERIFIED_SOURCE"};
 const n=(v,k)=>{if(!Number.isFinite(v)||v<0||v>1)throw Error("Invalid normalized "+k);return v;};
 const heat=n(signal.heat_intensity,"heat_intensity"),touch=n(signal.touch_pressure,"touch_pressure"),closeness=n(signal.obstacle_closeness,"obstacle_closeness");
 const desired=signal.next_gate===undefined?old.gate:signal.next_gate;
 if(!["ALPHA","BETA","GAMMA","DELTA","THETA"].includes(desired))throw Error("Unknown gate");
 const next={...old,seq:old.seq+1,events:old.events.slice(-15)};
 const gateChange=old.gate!==desired;
 const voltage=Math.min(2,old.membrane*old.decay+heat*.75+touch*.8+closeness*.35);
 const spiked=voltage>=old.threshold;
 next.membrane=spiked?0:Number(voltage.toFixed(4));
 next.gate=desired;
 const eventId="SIM_EVT_"+String(next.seq).padStart(8,"0");
 let kind=null;
 if(gateChange){kind="BRAINWAVE_GATE_TRANSITION";next.latest_event_id=eventId;}
 else if(spiked){kind="SNN_SPIKE";next.latest_event_id=eventId;}
 if(desired==="DELTA"){next.action="VIRTUAL_SAFE_STOP";}
 else if(spiked){next.action="VIRTUAL_WITHDRAW";}
 else if(desired==="BETA"){next.action="VIRTUAL_SCAN";}
 else {next.action="VIRTUAL_OBSERVE";}
 const event=kind?{event_id:eventId,kind,source_kind:"SIMULATED_INPUT",simulation:true,from_gate:old.gate,to_gate:desired,motor_action:next.action,spiked}:null;
 if(event)next.events.push(event);
 return {state:next,action:next.action,event,accepted:true,reason:"SIMULATION_ONLY"};
};
