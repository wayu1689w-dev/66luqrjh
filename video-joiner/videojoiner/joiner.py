"""Join several video clips into one file and keep the audio in sync.

Why audio usually disappears when joining clips:
  * some clips have no audio stream at all,
  * clips use different sample rates / channel layouts,
  * the plain "concat demuxer" copies streams and breaks on any mismatch.

Fix: normalise every clip (size, fps, sample rate, stereo) and give silent
clips a generated silent track of the same length, then use ffmpeg's concat
*filter*, which always re-encodes video and audio together.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

SAMPLE_RATE = 48000


class JoinError(RuntimeError):
    pass


@dataclass
class Clip:
    path: str
    duration: float
    has_audio: bool
    width: int
    height: int


def probe(path: str) -> Clip:
    p = Path(path)
    if not p.is_file():
        raise JoinError(f"ไม่พบไฟล์: {path}")
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", str(p)],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise JoinError(f"อ่านไฟล์ไม่ได้ ({path}): {out.stderr.strip()}")
    info = json.loads(out.stdout)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    if video is None:
        raise JoinError(f"ไม่มีภาพวิดีโอในไฟล์: {path}")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    return Clip(str(p), float(info["format"]["duration"]), has_audio,
                int(video["width"]), int(video["height"]))


def build_command(clips: list[Clip], output: str, width: int = 1280,
                  height: int = 720, fps: int = 30, mute: bool = False) -> list[str]:
    """Build the ffmpeg command. Pure function, so it is easy to test."""
    if not clips:
        raise JoinError("ต้องมีอย่างน้อย 1 คลิป")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for c in clips:
        cmd += ["-i", c.path]

    parts, labels = [], []
    silent_inputs = 0
    for i, c in enumerate(clips):
        parts.append(
            f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},"
            f"format=yuv420p[v{i}]")
        if c.has_audio and not mute:
            parts.append(
                f"[{i}:a]aresample={SAMPLE_RATE},"
                f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]")
        else:  # no audio (or muted): generate silence of the exact clip length
            parts.append(
                f"anullsrc=r={SAMPLE_RATE}:cl=stereo,atrim=duration={c.duration:.3f},"
                f"asetpts=N/SR/TB[a{i}]")
            silent_inputs += 1
        labels.append(f"[v{i}][a{i}]")

    parts.append("".join(labels) + f"concat=n={len(clips)}:v=1:a=1[v][a]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", output]
    return cmd


def join_videos(paths: list[str], output: str, **opts) -> Path:
    clips = [probe(p) for p in paths]
    cmd = build_command(clips, output, **opts)
    run = subprocess.run(cmd, capture_output=True, text=True)
    if run.returncode != 0:
        raise JoinError(f"ffmpeg ล้มเหลว: {run.stderr.strip()}")
    result = probe(output)
    if not result.has_audio:
        raise JoinError("ไฟล์ผลลัพธ์ไม่มีเสียง")
    return Path(output)
