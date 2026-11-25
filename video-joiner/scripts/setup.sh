#!/usr/bin/env bash
# ตรวจและติดตั้ง ffmpeg + Python บน macOS (Homebrew) / Linux (apt)
set -u
need=()
command -v ffmpeg >/dev/null 2>&1 || need+=(ffmpeg)
command -v python3 >/dev/null 2>&1 || need+=(python3)

if [ ${#need[@]} -gt 0 ]; then
  echo "กำลังติดตั้ง: ${need[*]}"
  if [ "$(uname)" = "Darwin" ]; then
    command -v brew >/dev/null 2>&1 || { echo "ไม่พบ Homebrew: ติดตั้งจาก https://brew.sh ก่อน"; exit 2; }
    pk=(); for n in "${need[@]}"; do [ "$n" = python3 ] && pk+=(python) || pk+=("$n"); done
    brew install "${pk[@]}" || { echo "ติดตั้งไม่สำเร็จ"; exit 1; }
  elif command -v apt-get >/dev/null 2>&1; then
    SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
    $SUDO apt-get update -qq && $SUDO apt-get install -y "${need[@]}" || { echo "ติดตั้งไม่สำเร็จ"; exit 1; }
  else
    echo "ไม่รู้จักตัวติดตั้งของระบบนี้: ติดตั้ง ${need[*]} เอง"; exit 2
  fi
fi

ok=1
if command -v ffmpeg >/dev/null 2>&1; then echo "ffmpeg พร้อม: $(ffmpeg -version | head -1)"; else echo "ยังไม่พบ ffmpeg"; ok=0; fi
if command -v python3 >/dev/null 2>&1; then echo "Python พร้อม: $(python3 --version) (คำสั่ง: python3)"; else echo "ยังไม่พบ Python"; ok=0; fi
[ $ok = 1 ] && { echo "พร้อมใช้งาน"; exit 0; } || exit 3
