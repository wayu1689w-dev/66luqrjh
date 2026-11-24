import argparse
from .joiner import join_videos, JoinError


def main():
    ap = argparse.ArgumentParser(prog="videojoiner", description="ต่อวิดีโอหลายคลิปให้เป็นไฟล์เดียว (เสียงไม่หาย)")
    ap.add_argument("clips", nargs="+", help="ไฟล์วิดีโอตามลำดับ")
    ap.add_argument("-o", "--output", default="joined.mp4")
    ap.add_argument("--size", default="1280x720", help="กว้างxสูง")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--mute", action="store_true", help="ตัดเสียงทั้งหมด")
    a = ap.parse_args()
    w, h = map(int, a.size.lower().split("x"))
    try:
        out = join_videos(a.clips, a.output, width=w, height=h, fps=a.fps, mute=a.mute)
    except JoinError as e:
        raise SystemExit(f"error: {e}")
    print(f"สำเร็จ -> {out}")


main()
