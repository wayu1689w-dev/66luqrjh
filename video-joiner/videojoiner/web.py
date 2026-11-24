"""Tiny local web UI: python -m videojoiner.web  ->  http://localhost:8000
Upload several clips, get one joined mp4 back. Standard library only."""
import tempfile
from email import message_from_bytes
from email.policy import HTTP
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .joiner import join_videos, JoinError

PAGE = """<!doctype html><meta charset=utf-8><title>Video Joiner</title>
<style>body{font-family:system-ui;max-width:560px;margin:48px auto;color:#14213D}
button{background:#2563EB;color:#fff;border:0;padding:10px 18px;border-radius:8px;font-size:16px}
input{margin:12px 0;display:block}</style>
<h1>ต่อวิดีโอ</h1>
<form method=post enctype=multipart/form-data>
<p>เลือกหลายไฟล์ตามลำดับที่ต้องการ</p>
<input type=file name=clips accept="video/*" multiple required>
<label><input type=checkbox name=mute> ตัดเสียงทั้งหมด</label>
<button>ต่อวิดีโอ</button></form>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(200, PAGE.encode())

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        msg = message_from_bytes(
            b"Content-Type: " + self.headers["Content-Type"].encode() + b"\r\n\r\n" + body,
            policy=HTTP)
        files, mute = [], False
        for part in msg.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if name == "mute":
                mute = True
            elif name == "clips" and part.get_filename():
                files.append((part.get_filename(), part.get_payload(decode=True)))
        if not files:
            return self._send(400, "กรุณาเลือกไฟล์".encode(), "text/plain; charset=utf-8")
        with tempfile.TemporaryDirectory() as d:
            paths = []
            for n, (fname, data) in enumerate(files):
                p = Path(d) / f"{n:03d}{Path(fname).suffix}"
                p.write_bytes(data)
                paths.append(str(p))
            try:
                out = join_videos(paths, str(Path(d) / "joined.mp4"), mute=mute)
            except JoinError as e:
                return self._send(400, str(e).encode(), "text/plain; charset=utf-8")
            self._send(200, out.read_bytes(), "video/mp4")


if __name__ == "__main__":
    print("http://localhost:8000")
    HTTPServer(("", 8000), Handler).serve_forever()
