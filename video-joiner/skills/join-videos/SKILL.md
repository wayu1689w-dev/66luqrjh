---
name: join-videos
description: Join several video clips into one mp4 while keeping audio (silent clips get silence, mixed sample rates fixed). Supports crossfade, background music, voice-over, and Gemini-generated subtitles/TTS. Use when the user wants to stitch/merge/concatenate videos, or asks for subtitles or a voice-over for a video.
---

Run from the plugin root: `cd "${CLAUDE_PLUGIN_ROOT}"` (needs `ffmpeg` >= 5.1 and Python 3.9+).

## Join clips
`python3 -m videojoiner a.mp4 b.mp4 -o joined.mp4`

Options: `--crossfade 0.5` (clips must be >= 2x as long), `--music bg.mp3 --music-volume 0.25`,
`--voiceover voice.wav` (plays once; cannot combine with `--music`), `--size 1080x1920`, `--fps 30`, `--mute`.
Paths are relative to the plugin root, so pass absolute paths for the user's files.
The tool fails loudly if the result has no audio track; report that error, do not hide it.

## Gemini helpers (optional)
Need `GEMINI_API_KEY` from Google AI Studio in the environment. Never ask the user to paste the key
in chat and never print it.

- Subtitles: `python3 -m videojoiner.gemini subs joined.mp4 -o subs.srt --lang th`
- Voice-over: `python3 -m videojoiner.gemini speak script.txt -o voice.wav`

Model names are env-configurable (`GEMINI_STT_MODEL`, `GEMINI_TTS_MODEL`, `GEMINI_VOICE`) and the defaults
are unverified guesses. These calls have only been tested against mocked responses, so say so if one fails
and check the current Gemini docs for model names.

## Browser UI
`python3 -m videojoiner.web` serves http://localhost:8000 (drag-reorder, crossfade, music, progress).
Local use only: no auth.
