"""SKELETON: Gemini API helpers for the video joiner (standard library only).

  transcribe_to_srt(video)  -> subtitles (.srt) from the clip's speech
  synthesize_speech(text)   -> voice-over WAV, usable as `music=` with music_loop=False

Needs GEMINI_API_KEY (from Google AI Studio). Model names change often, so they
are read from env and MUST be checked against the current docs:
  GEMINI_STT_MODEL  GEMINI_TTS_MODEL  GEMINI_VOICE
The payload shapes below follow the public generateContent REST format, but they
were NOT run against the real API here (no key) — only against mocked responses.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
import urllib.request
import wave
from pathlib import Path

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
STT_MODEL = os.getenv("GEMINI_STT_MODEL", "gemini-2.5-flash")          # TODO verify
TTS_MODEL = os.getenv("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")  # TODO verify
VOICE = os.getenv("GEMINI_VOICE", "Kore")
PCM_RATE = 24000  # TTS returns raw 16-bit mono PCM @ 24kHz


class GeminiError(RuntimeError):
    pass


def _call(model: str, payload: dict) -> dict:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise GeminiError("ไม่พบ GEMINI_API_KEY (ตั้งค่าเป็น environment variable)")
    req = urllib.request.Request(
        API.format(model=model), data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except Exception as e:  # network / HTTP errors, never include the key
        raise GeminiError(f"เรียก Gemini ล้มเหลว: {type(e).__name__}") from e


# ---------- subtitles ----------
def build_transcribe_payload(audio: bytes, mime: str = "audio/mp3", lang: str = "th") -> dict:
    prompt = (f"Transcribe the speech (language: {lang}). Return a JSON array of "
              'segments: [{"start": seconds, "end": seconds, "text": "..."}]. '
              "Only speech, no commentary.")
    return {"contents": [{"parts": [
        {"text": prompt},
        {"inline_data": {"mime_type": mime, "data": base64.b64encode(audio).decode()}}]}],
        "generationConfig": {"responseMimeType": "application/json"}}


def _ts(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def segments_to_srt(segments: list[dict]) -> str:
    out = []
    for i, s in enumerate(segments, 1):
        out.append(f"{i}\n{_ts(float(s['start']))} --> {_ts(float(s['end']))}\n{s['text'].strip()}\n")
    return "\n".join(out)


def transcribe_to_srt(video: str, srt_out: str, lang: str = "th") -> Path:
    with tempfile.TemporaryDirectory() as d:  # small mono mp3 keeps us under inline limits
        mp3 = Path(d, "a.mp3")
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vn",
                            "-ac", "1", "-ar", "16000", "-b:a", "48k", str(mp3)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise GeminiError(f"ดึงเสียงไม่ได้: {r.stderr.strip()}")
        resp = _call(STT_MODEL, build_transcribe_payload(mp3.read_bytes(), lang=lang))
    try:
        text = resp["candidates"][0]["content"]["parts"][0]["text"]
        segments = json.loads(text)
    except (KeyError, IndexError, ValueError) as e:
        raise GeminiError("รูปแบบคำตอบจาก Gemini ไม่ตรงที่คาด") from e
    Path(srt_out).write_text(segments_to_srt(segments), encoding="utf-8")
    return Path(srt_out)


# ---------- voice-over ----------
def build_tts_payload(text: str, voice: str = VOICE) -> dict:
    return {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {
                                     "prebuiltVoiceConfig": {"voiceName": voice}}}}}


def synthesize_speech(text: str, wav_out: str, voice: str = VOICE) -> Path:
    resp = _call(TTS_MODEL, build_tts_payload(text, voice))
    try:
        part = resp["candidates"][0]["content"]["parts"][0]
        pcm = base64.b64decode((part.get("inlineData") or part["inline_data"])["data"])
    except (KeyError, IndexError) as e:
        raise GeminiError("ไม่พบข้อมูลเสียงในคำตอบจาก Gemini") from e
    with wave.open(wav_out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(PCM_RATE)
        w.writeframes(pcm)
    return Path(wav_out)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(prog="videojoiner.gemini")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("subs", help="ถอดเสียงวิดีโอเป็น .srt")
    t.add_argument("video"); t.add_argument("-o", "--output", default="subs.srt")
    t.add_argument("--lang", default="th")
    s = sub.add_parser("speak", help="สร้างเสียงพากย์ .wav จากข้อความ/ไฟล์ .txt")
    s.add_argument("text"); s.add_argument("-o", "--output", default="voice.wav")
    a = ap.parse_args()
    try:
        if a.cmd == "subs":
            print(transcribe_to_srt(a.video, a.output, a.lang))
        else:
            txt = Path(a.text).read_text(encoding="utf-8") if Path(a.text).is_file() else a.text
            print(synthesize_speech(txt, a.output))
    except GeminiError as e:
        raise SystemExit(f"error: {e}")
