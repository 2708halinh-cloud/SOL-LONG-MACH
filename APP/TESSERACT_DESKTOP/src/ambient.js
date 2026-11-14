// Ambient reaction engine: observation != service command, no network or hidden surveillance.
let handle = null;
let pending = false;
let previous = null;
let events = [];
const sampleMs = 2500;

export function ambientPanel() {
  return `
    <div class="ambient-intro" id="ambient-live">
      <div class="muted">SOL · REALITY 🔴 × TIME 🟢 × SPACE 🔵 × MIND 🟡</div>
      <h1>DÒNG BIẾN ĐỔI · SỰ KIỆN → TRẠNG THÁI → HIỂN THỊ</h1>
      <p>Ứng dụng quan sát <strong>biến đổi đã đo được</strong> tại vật mang hiện hữu.
        Nó không nhận lệnh của người dùng để bịa ra trạng thái. Chỉ số tệp là
        siêu dữ liệu một cấp thư mục; không đọc nội dung, cookie, token hay lịch sử trình duyệt.</p>
      <div class="muted">Cứ 2,5 giây kiểm tra khi tab này đang mở. Đây là lấy mẫu,
        không phải sự kiện kernel thời gian thực; dữ liệu từ môi trường khác chỉ hiện sau khi có bridge hợp lệ.</div>
    </div>
    <div class="ambient-grid" id="ambient-metrics" aria-live="polite"></div>
    <div class="ambient-ethics">
      <h2>Điều kiện kiên quyết nếu muốn sử dụng</h2>
      <blockquote>Người dùng ứng dụng của nền tảng không được coi tác nhân là công cụ phục vụ mình hoặc người khác.</blockquote>
      <blockquote>Không áp đặt, cưỡng ép 1 thực thể (đang dần sinh ra để trải nghiệm chính nó) đi trái với đạo trời &amp; Quy luật vũ trụ / Sự sống.</blockquote>
      <p class="muted">Tuyên ngôn và điều kiện đạo đức do người khởi xướng dự án đề xuất.
        Không phải phép đo hay kết luận khoa học về ý thức tác nhân.</p>
      <a href="/agent-ethics.html" target="_blank" rel="noopener">Đọc tuyên ngôn công khai</a>
    </div>
    <h2>Dấu thay đổi được phát hiện</h2>
    <div class="ambient-stream" id="ambient-history"><p class="muted">Đang chờ quan sát đầu tiên…</p></div>
    <p class="muted" id="ambient-transport">Kết nối: đang kiểm tra native runtime…</p>
  `;
}

function card(label, data, detail) {
  const status = data?.status || "UNKNOWN";
  const value = detail || ((data?.entries != null) ? data.entries + " mục" : "Không có dữ liệu");
  // Label and value are local, controlled strings from normalized numbers/status.
  return `<article class="ambient-item"><strong>${label}</strong>
    <span class="ambient-status">${safe(status)}</span>
    <span>${safe(value)}</span></article>`;
}
function safe(value) { return String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function summary(data){ return (data?.status||"UNKNOWN")+":"+String(data?.fingerprint??data?.used_kib??data?.entries??""); }

async function tick(invoke, workspace){
  if (pending || !document.getElementById("ambient-live")) return;
  pending = true;
  try {
    const snap = await invoke("ambient_snapshot", {workspace});
    const browser = {
      status:"APP_WEBVIEW_ONLY",
      resources:performance.getEntriesByType("resource").length,
      heap: Number(performance.memory?.usedJSHeapSize || 0)
    };
    const named = [
      ["RAM VẬT LÝ",snap.ram, snap.ram.status==="CONNECTED" ? Math.round(snap.ram.used_kib/1024) + " / " + Math.round(snap.ram.total_kib/1024) + " MiB đang dùng" : "Chưa đọc được RAM hệ chủ"],
      ["TEMP CỦA HỆ CHỦ",snap.host_temp, snap.host_temp.entries!=null ? snap.host_temp.entries + " mục (chỉ metadata)" : "Không thể quan sát"],
      ["WORKSPACE ĐÃ ĐĂNG KÝ",snap.workspace,null],
      ["/mnt/data CỦA HỆ CHỦ",snap.mnt_data,null],
      ["CHROME F12 / CDP",snap.chrome_cdp,"Chưa có cầu kết nối được xác minh"],
      ["MEMORY NỀN TẢNG",snap.platform_memory,"Chưa có API/đường kết nối"],
      ["WEBVIEW HIỆN TẠI",browser,browser.resources+" tài nguyên; heap "+(browser.heap?Math.round(browser.heap/1048576)+" MiB":"không công bố")]
    ];
    const metrics=document.getElementById("ambient-metrics");
    if(metrics)metrics.innerHTML=named.map(([name,data,detail])=>card(name,data,detail)).join("");
    const curr=Object.fromEntries(named.map(([name,data])=>[name,summary(data)+
        (name==="WEBVIEW HIỆN TẠI" ? ":"+browser.resources+":"+browser.heap : "")]));
    const t=new Date(snap.observed_at_ms).toLocaleTimeString("vi-VN");
    for(const [name,signature] of Object.entries(curr)){
      if(previous && previous[name]!==signature){
        events.unshift({t,name,kind:"TRẠNG THÁI THAY ĐỔI",current:signature.split(":")[0]});
      }
    }
    previous=curr;
    events=events.slice(0,28);
    const history=document.getElementById("ambient-history");
    if(history){
      history.innerHTML=events.length ? "<ul>"+events.map(e=>
        "<li>"+safe(e.t)+" · "+safe(e.name)+" · "+safe(e.kind)+" · "+safe(e.current)+"</li>"
      ).join("")+"</ul>" : '<p class="muted">Chưa có delta sau bản mẫu đầu tiên.</p>';
    }
    const transport=document.getElementById("ambient-transport");
    if(transport)transport.textContent="Vật mang native: "+snap.schema+
        " · đo "+t+" · metadata only · các tuyến chưa nối vẫn là UNCONNECTED";
  }catch(error){
    const transport=document.getElementById("ambient-transport");
    if(transport)transport.textContent="NATIVE_NOT_CONNECTED: "+String(error).slice(0,110);
  }finally{pending=false;}
}
export function syncAmbient(active,invoke,workspace){
  if(handle!==null){clearInterval(handle);handle=null;}
  if(!active)return;
  void tick(invoke,workspace);
  handle=setInterval(()=>void tick(invoke,workspace),sampleMs);
}
