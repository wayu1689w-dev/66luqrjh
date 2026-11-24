"""Join video clips into one file, keeping every clip's audio.

Features: normalised size/fps/audio, silent-track fill for clips without
sound, optional crossfade between clips, optional background music mixed
under the original audio, and progress reporting.

Needs ffmpeg >= 5.1 (uses amix normalize=0).
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

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


def total_duration(clips: list[Clip], crossfade: float = 0.0) -> float:
    return sum(c.duration for c in clips) - crossfade * (len(clips) - 1)


def build_command(clips: list[Clip], output: str, width: int = 1280,
                  height: int = 720, fps: int = 30, mute: bool = False,
                  crossfade: float = 0.0, music: Optional[str] = None,
                  music_volume: float = 0.25) -> list[str]:
    """Build the ffmpeg command. Pure function, so it is easy to test."""
    if not clips:
        raise JoinError("ต้องมีอย่างน้อย 1 คลิป")
    if crossfade < 0:
        raise JoinError("crossfade ต้องไม่ติดลบ")
    if len(clips) == 1:
        crossfade = 0.0
    if crossfade and min(c.duration for c in clips) < crossfade * 2:
        raise JoinError("มีคลิปสั้นกว่า 2 เท่าของเวลา crossfade")

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for c in clips:
        cmd += ["-i", c.path]
    if music:
        cmd += ["-stream_loop", "-1", "-i", music]  # loop short tracks
    n = len(clips)

    f = []
    for i, c in enumerate(clips):
        f.append(
            f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},"
            f"format=yuv420p,settb=AVTB[v{i}]")
        if c.has_audio and not mute:
            f.append(f"[{i}:a]aresample={SAMPLE_RATE},"
                     f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]")
        else:  # silence of the exact clip length keeps everything in sync
            f.append(f"anullsrc=r={SAMPLE_RATE}:cl=stereo,"
                     f"atrim=duration={c.duration:.3f},asetpts=N/SR/TB[a{i}]")

    if crossfade:
        vprev, aprev, acc = "v0", "a0", clips[0].duration
        for k in range(1, n):
            offset = acc - crossfade
            vout = "v" if k == n - 1 else f"vx{k}"
            aout = "amain" if k == n - 1 else f"ax{k}"
            f.append(f"[{vprev}][v{k}]xfade=transition=fade:duration={crossfade}:"
                     f"offset={offset:.3f}[{vout}]")
            f.append(f"[{aprev}][a{k}]acrossfade=d={crossfade}[{aout}]")
            vprev, aprev, acc = vout, aout, acc + clips[k].duration - crossfade
        if n == 1:
            raise AssertionError  # unreachable: crossfade zeroed above
    else:
        f.append("".join(f"[v{i}][a{i}]" for i in range(n)) +
                 f"concat=n={n}:v=1:a=1[v][amain]")

    if music:
        total = total_duration(clips, crossfade)
        f.append(f"[{n}:a]aresample={SAMPLE_RATE},"
                 f"aformat=sample_fmts=fltp:channel_layouts=stereo,"
                 f"volume={music_volume},atrim=duration={total:.3f},"
                 f"afade=t=out:st={max(total - 2, 0):.3f}:d=2[bg]")
        f.append("[amain][bg]amix=inputs=2:duration=first:normalize=0[a]")
    else:
        f.append("[amain]anull[a]")

    cmd += ["-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            "-progress", "pipe:1", "-nostats", output]
    return cmd


def join_videos(paths: list[str], output: str,
                progress: Optional[Callable[[float], None]] = None,
                **opts) -> Path:
    """Join clips. `progress` gets a 0..1 fraction while encoding."""
    clips = [probe(p) for p in paths]
    cmd = build_command(clips, output, **opts)
    total = total_duration(clips, opts.get("crossfade", 0.0) if len(clips) > 1 else 0.0)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in proc.stdout:
        if line.startswith("out_time_us=") and progress and total > 0:
            try:
                progress(min(int(line.split("=")[1]) / 1e6 / total, 1.0))
            except ValueError:  # ffmpeg prints N/A at the start
                pass
    err = proc.stderr.read()
    proc.stdout.close()
    proc.stderr.close()
    if proc.wait() != 0:
        raise JoinError(f"ffmpeg ล้มเหลว: {err.strip()}")
    if progress:
        progress(1.0)
    if not probe(output).has_audio:
        raise JoinError("ไฟล์ผลลัพธ์ไม่มีเสียง")
    return Path(output)
