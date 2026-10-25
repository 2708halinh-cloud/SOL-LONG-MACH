const $=id=>document.getElementById(id);
let key="",activeRoom="sol-main";
function node(tag,text,klass=""){const e=document.createElement(tag);e.textContent=text;if(klass)e.className=klass;return e}
function say(msg){$("feedback").textContent=typeof msg==="string"?msg:JSON.stringify(msg,null,2)}
async function api(path,body=null){
  if(!key)throw Error("Nhập token ở cột trái trước.");
  const res=await fetch(path,{method:body?"POST":"GET",headers:{"X-SOL-TOKEN":key,...(body?{"Content-Type":"application/json"}:{})},
    ...(body?{body:JSON.stringify(body)}:{})});
  const data=await res.json();
  if(!res.ok)throw Error(data.error||("HTTP "+res.status));
  return data;
}
async function refresh(){
  const state=await api("/api/state");
  $("connection").textContent="LOCAL · "+state.rooms.length+" phòng";
  $("rooms").replaceChildren();
  for(const r of state.rooms){
    const btn=node("button",r.title,r.id===activeRoom?"":"secondary");
    btn.classList.add("workspace-button");btn.onclick=()=>{activeRoom=r.id;refresh().catch(e=>say(e.message))};
    $("rooms").append(btn);
  }
  $("capabilities").replaceChildren();
  for(const [name,desc] of Object.entries(state.capabilities)){
    const item=node("div",name+" · "+desc.state,"agentchip");
    $("capabilities").append(item);
  }
  const data=await api("/api/events?room="+encodeURIComponent(activeRoom));
  $("log").replaceChildren();
  for(const e of data.events){
    const article=node("article","","event "+(e.role==="DUONG_PHAP_SU"?"human":"agent"));
    article.append(node("div",e.role+" · "+e.actor+" · "+e.kind+" · "+e.created_at,"meta"));
    article.append(node("div",e.content));
    if(e.source_ref)article.append(node("div","Nguồn: "+e.source_ref,"caption"));
    $("log").append(article);
  }
  $("log").scrollTop=$("log").scrollHeight;
}
function wrap(fn){return async()=>{try{await fn()}catch(e){say("KHÔNG THỰC HIỆN: "+e.message)}}}
$("connect").onclick=wrap(async()=>{
  key=$("token").value.trim();
  await refresh();
  $("token").value="";
  say("Đã kết nối workspace cục bộ. Quyền dữ liệu trong tiến trình này.");
});
$("send").onclick=wrap(async()=>{
  await api("/api/messages",{room_id:activeRoom,kind:$("kind").value,content:$("message").value,actor:"DƯƠNG PHÁP SƯ"});
  $("message").value="";await refresh();say("Tin nhắn đã được ghi vào SQLite và đọc lại.");
});
$("add-room").onclick=wrap(async()=>{
  const out=await api("/api/rooms",{title:$("new-room").value});activeRoom=out.room_id;
  $("new-room").value="";await refresh();
});
$("dispatch").onclick=wrap(async()=>{
  const result=await api("/api/dispatch",{room_id:activeRoom,agent:$("agent").value,task:$("task").value});
  say(result.output);await refresh();
});
async function fileBase64(file){
  return new Promise((resolve,reject)=>{
    if(file.size>9000000)return reject(Error("Giới hạn tệp: 9 MB."));
    const rd=new FileReader();
    rd.onload=()=>resolve(String(rd.result).split(",")[1]||"");
    rd.onerror=()=>reject(Error("Không đọc được tệp"));
    rd.readAsDataURL(file);
  });
}
$("runcap").onclick=wrap(async()=>{
  const cap=$("cap").value;
  const payload={room_id:activeRoom,capability:cap,text:$("captext").value,
    query:$("captext").value,task:$("captext").value,target:$("target").value,
    approve_external:$("approve").checked};
  if(cap==="master_teacher_ethics"){
    // The ethics gate takes an explicit event; never invent a completed action.
    try{
      payload.event=JSON.parse($("captext").value);
    }catch(e){
      throw Error("Nhập JSON sự kiện: action_type, source_ref, target, actor_role... Đừng nhập lời hứa như biên nhận.");
    }
  }
  const media=$("media").files[0];
  if(["image_details","video_stream_frames","transcription_mp3_mp4","video_objects_saved"].includes(cap)){
    if(!media)throw Error("Chọn tệp ảnh, video hoặc âm thanh.");
    const b64=await fileBase64(media);
    if(cap==="image_details"||cap==="video_stream_frames"){payload.image_b64=b64;payload.frame_observed_at=new Date().toISOString()}
    else if(cap==="video_objects_saved")payload.video_b64=b64;
    else{payload.media_b64=b64;payload.filename=media.name}
  }
  const result=await api("/api/capabilities/run",payload);
  say(result.result);await refresh();
});
