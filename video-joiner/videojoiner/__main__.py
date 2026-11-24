import argparse
import sys
from .joiner import join_videos, JoinError


def main():
    ap = argparse.ArgumentParser(prog="videojoiner", description="ต่อวิดีโอหลายคลิปให้เป็นไฟล์เดียว (เสียงไม่หาย)")
    ap.add_argument("clips", nargs="+", help="ไฟล์วิดีโอตามลำดับ")
    ap.add_argument("-o", "--output", default="joined.mp4")
    ap.add_argument("--size", default="1280x720", help="กว้างxสูง")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--mute", action="store_true", help="ตัดเสียงเดิมทั้งหมด")
    ap.add_argument("--crossfade", type=float, default=0.0, help="วินาที ที่เฟดซ้อนระหว่างคลิป")
    ap.add_argument("--music", help="ไฟล์เพลงพื้นหลัง (วนซ้ำ/ตัดให้พอดี)")
    ap.add_argument("--music-volume", type=float, default=0.25)
    a = ap.parse_args()
    w, h = map(int, a.size.lower().split("x"))

    def show(p):
        print(f"\r{p:6.1%}", end="", file=sys.stderr, flush=True)

    try:
        out = join_videos(a.clips, a.output, progress=show, width=w, height=h, fps=a.fps,
                          mute=a.mute, crossfade=a.crossfade, music=a.music,
                          music_volume=a.music_volume)
    except JoinError as e:
        raise SystemExit(f"\nerror: {e}")
    print(f"\nสำเร็จ -> {out}")


main()
