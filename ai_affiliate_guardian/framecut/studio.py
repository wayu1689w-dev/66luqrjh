"""FrameCut Studio — Spec v008 Area 4
AI Script, Storyboard, Auto Subtitle, Multi-track Timeline,
Audio Guard, Product Grouping, MP4 Rendering, PNG Cover, ZIP Export

video-joiner (อยู่แล้ว) ทำหน้าที่ rendering ผ่าน ffmpeg
โมดูลนี้เพิ่มชั้น script/storyboard/subtitle/timeline ครอบ joiner"""

import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

_counter = 0


def _next_id(prefix: str = "FC") -> str:
    global _counter
    _counter += 1
    return f"{prefix}-{_counter:06d}"


class Script:
    def __init__(self, product_name: str, style: str = "review"):
        self.id = _next_id("SCR")
        self.product_name = product_name
        self.style = style
        self.scenes: list[dict] = []
        self.created_at = datetime.now(timezone.utc).isoformat()

    def add_scene(self, scene_type: str, text: str,
                  duration_sec: float = 5.0, notes: str = "") -> dict:
        scene = {
            "id": _next_id("SCN"),
            "type": scene_type,
            "text": text,
            "duration_sec": duration_sec,
            "notes": notes,
        }
        self.scenes.append(scene)
        return scene

    def total_duration(self) -> float:
        return sum(s["duration_sec"] for s in self.scenes)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_name": self.product_name,
            "style": self.style,
            "scenes": self.scenes,
            "total_duration": self.total_duration(),
            "created_at": self.created_at,
        }


class Storyboard:
    def __init__(self, script: Script):
        self.id = _next_id("STB")
        self.script_id = script.id
        self.frames: list[dict] = []
        for scene in script.scenes:
            self.frames.append({
                "scene_id": scene["id"],
                "visual_description": f"[{scene['type']}] {scene['text'][:50]}",
                "audio_note": "",
                "image_path": "",
            })

    def set_image(self, scene_id: str, image_path: str):
        for frame in self.frames:
            if frame["scene_id"] == scene_id:
                frame["image_path"] = image_path
                return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "script_id": self.script_id,
            "frame_count": len(self.frames),
            "frames": self.frames,
        }


class SubtitleTrack:
    def __init__(self):
        self.id = _next_id("SUB")
        self.entries: list[dict] = []

    def add_entry(self, start_sec: float, end_sec: float, text: str):
        self.entries.append({
            "start": start_sec,
            "end": end_sec,
            "text": text,
        })

    def to_srt(self) -> str:
        lines = []
        for i, e in enumerate(self.entries, 1):
            s = _fmt_time(e["start"])
            end = _fmt_time(e["end"])
            lines.append(f"{i}\n{s} --> {end}\n{e['text']}\n")
        return "\n".join(lines)

    def total_entries(self) -> int:
        return len(self.entries)


def _fmt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


class Timeline:
    def __init__(self):
        self.id = _next_id("TML")
        self.tracks: dict[str, list[dict]] = {
            "video": [],
            "audio": [],
            "subtitle": [],
            "music": [],
        }

    def add_clip(self, track: str, file_path: str, start_sec: float,
                 duration_sec: float, label: str = ""):
        if track not in self.tracks:
            raise ValueError(f"Track ไม่ถูกต้อง: {track}")
        self.tracks[track].append({
            "id": _next_id("CLP"),
            "file_path": file_path,
            "start": start_sec,
            "duration": duration_sec,
            "label": label,
        })

    def total_duration(self) -> float:
        all_ends = []
        for clips in self.tracks.values():
            for c in clips:
                all_ends.append(c["start"] + c["duration"])
        return max(all_ends) if all_ends else 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tracks": {k: len(v) for k, v in self.tracks.items()},
            "total_duration": self.total_duration(),
        }


class AudioGuard:
    MAX_DB = -3.0
    MIN_DB = -40.0

    @classmethod
    def check_level(cls, db_level: float) -> tuple[bool, str]:
        if db_level > cls.MAX_DB:
            return False, f"เสียงดังเกิน ({db_level} dB > {cls.MAX_DB} dB)"
        if db_level < cls.MIN_DB:
            return False, f"เสียงเบาเกิน ({db_level} dB < {cls.MIN_DB} dB)"
        return True, "ระดับเสียงปกติ"


class ProductGroup:
    def __init__(self, group_name: str):
        self.id = _next_id("PGR")
        self.name = group_name
        self.products: list[str] = []

    def add_product(self, product_id: str):
        if product_id not in self.products:
            self.products.append(product_id)

    def remove_product(self, product_id: str):
        self.products = [p for p in self.products if p != product_id]


def create_zip_export(files: list[str], output_path: str) -> str:
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            if os.path.exists(f):
                zf.write(f, os.path.basename(f))
    return output_path


def reset():
    global _counter
    _counter = 0
