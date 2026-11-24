"""Local web UI: python -m videojoiner.web -> http://localhost:8000
Drag to reorder clips, crossfade, background music, live progress.
Standard library only."""
import json
import tempfile
import threading
import uuid
from email import message_from_bytes
from email.policy import HTTP
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .joiner import join_videos, JoinError

JOBS: dict = {}  # id -> {"progress", "status", "error", "file"}
ROOT = Path(tempfile.mkdtemp(prefix="videojoiner-"))

PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width">
<title>Video Joiner</title>
<style>
body{font-family:system-ui;max-width:600px;margin:40px auto;padding:0 16px;color:#14213D;background:#F7F9FF}
button{background:#2563EB;color:#fff;border:0;padding:10px 18px;border-radius:8px;font-size:16px;cursor:pointer}
button:disabled{background:#94A3B8}
#list{list-style:none;padding:0}
#list li{background:#fff;border:1px solid #E2E8F0;border-radius:8px;padding:10px 12px;margin:6px 0;
display:flex;gap:10px;align-items:center;cursor:grab}
#list li.drag{opacity:.4}
#list li span{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#list li b{cursor:pointer;color:#B91C1C}
label{display:block;margin:10px 0}
progress{width:100%;height:18px}
</style>
<h1>ต่อวิดีโอ</h1>
<input type=file id=pick accept="video/*" multiple>
<p>ลากแถวเพื่อสลับลำดับ</p>
<ul id=list></ul>
<label>Crossfade (วินาที, 0 = ตัดต่อตรง ๆ)
 <input type=number id=xf value=0 min=0 max=5 step=0.25></label>
<label>เพลงพื้นหลัง (ไม่บังคับ) <input type=file id=music accept="audio/*"></label>
<label>ความดังเพลง <input type=range id=vol min=0 max=1 step=0.05 value=0.25></label>
<label><input type=checkbox id=mute> ตัดเสียงเดิมของคลิป</label>
<button id=go>ต่อวิดีโอ</button>
<p id=msg></p><progress id=bar value=0 max=1 hidden></progress>
<video id=out controls style="width:100%" hidden></video>
<a id=dl hidden download=joined.mp4>ดาวน์โหลด</a>
<script>
const files=[];const list=document.getElementById('list');
function render(){list.innerHTML='';files.forEach((f,i)=>{
 const li=document.createElement('li');li.draggable=true;
 li.innerHTML='<span></span><b title=ลบ>✕</b>';li.firstChild.textContent=(i+1)+'. '+f.name;
 li.lastChild.onclick=()=>{files.splice(i,1);render()};
 li.ondragstart=e=>{e.dataTransfer.setData('text',i);li.classList.add('drag')};
 li.ondragend=()=>li.classList.remove('drag');
 li.ondragover=e=>e.preventDefault();
 li.ondrop=e=>{e.preventDefault();const from=+e.dataTransfer.getData('text');
  files.splice(i,0,files.splice(from,1)[0]);render()};
 list.appendChild(li)})}
pick.onchange=()=>{files.push(...pick.files);pick.value='';render()};
const $=id=>document.getElementById(id);
$('go').onclick=()=>{
 if(!files.length)return $('msg').textContent='เลือกคลิปก่อน';
 const fd=new FormData();files.forEach(f=>fd.append('clips',f));
 if($('music').files[0])fd.append('music',$('music').files[0]);
 fd.append('crossfade',$('xf').value);fd.append('music_volume',$('vol').value);
 if($('mute').checked)fd.append('mute','1');
 $('go').disabled=true;$('bar').hidden=false;$('bar').value=0;$('msg').textContent='กำลังอัปโหลด...';
 const x=new XMLHttpRequest();x.open('POST','/jobs');
 x.upload.onprogress=e=>{if(e.lengthComputable)$('bar').value=e.loaded/e.total*0.3};
 x.onload=()=>{if(x.status!=200){fail(x.responseText);return}poll(JSON.parse(x.responseText).id)};
 x.onerror=()=>fail('เชื่อมต่อไม่ได้');x.send(fd)};
function fail(t){$('msg').textContent='ผิดพลาด: '+t;$('go').disabled=false}
async function poll(id){
 const j=await (await fetch('/jobs/'+id)).json();
 if(j.status=='error')return fail(j.error);
 $('bar').value=0.3+j.progress*0.7;$('msg').textContent='กำลังต่อวิดีโอ '+Math.round(j.progress*100)+'%';
 if(j.status=='done'){$('msg').textContent='เสร็จแล้ว';$('go').disabled=false;
  $('out').src=$('dl').href='/jobs/'+id+'/result';$('out').hidden=$('dl').hidden=false;return}
 setTimeout(()=>poll(id),500)}
</script>"""


def _run(job_id, paths, out, opts):
    job = JOBS[job_id]
    try:
        join_videos(paths, str(out), progress=lambda p: job.update(progress=p), **opts)
        job.update(status="done", file=str(out), progress=1.0)
    except (JoinError, OSError) as e:
        job.update(status="error", error=str(e))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json")

    def do_GET(self):
        parts = self.path.strip("/").split("/")
        if parts == [""]:
            return self._send(200, PAGE)
        job = JOBS.get(parts[1]) if len(parts) > 1 and parts[0] == "jobs" else None
        if job is None:
            return self._json(404, {"error": "not found"})
        if len(parts) == 2:
            return self._json(200, {k: job.get(k) for k in ("status", "progress", "error")})
        if len(parts) == 3 and parts[2] == "result" and job["status"] == "done":
            return self._send(200, Path(job["file"]).read_bytes(), "video/mp4")
        self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/jobs":
            return self._json(404, {"error": "not found"})
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        msg = message_from_bytes(
            b"Content-Type: " + self.headers["Content-Type"].encode() + b"\r\n\r\n" + body,
            policy=HTTP)
        job_id = uuid.uuid4().hex[:12]
        d = ROOT / job_id
        d.mkdir()
        paths, opts, music = [], {}, None
        for part in msg.iter_parts():
            name = part.get_param("name", header="content-disposition")
            data = part.get_payload(decode=True)
            if name == "clips" and part.get_filename():
                p = d / f"{len(paths):03d}{Path(part.get_filename()).suffix}"
                p.write_bytes(data)
                paths.append(str(p))
            elif name == "music" and part.get_filename():
                music = d / f"music{Path(part.get_filename()).suffix}"
                music.write_bytes(data)
                opts["music"] = str(music)
            elif name == "mute":
                opts["mute"] = True
            elif name in ("crossfade", "music_volume"):
                try:
                    opts[name] = float(data.decode())
                except ValueError:
                    return self._send(400, "ค่าตัวเลขไม่ถูกต้อง", "text/plain; charset=utf-8")
        if not paths:
            return self._send(400, "กรุณาเลือกไฟล์", "text/plain; charset=utf-8")
        JOBS[job_id] = {"status": "running", "progress": 0.0}
        threading.Thread(target=_run, args=(job_id, paths, d / "joined.mp4", opts),
                         daemon=True).start()
        self._json(200, {"id": job_id})


if __name__ == "__main__":
    print("http://localhost:8000")
    ThreadingHTTPServer(("", 8000), Handler).serve_forever()
