import subprocess, tempfile, unittest
from pathlib import Path
from videojoiner import join_videos, probe


def make(path, size, audio):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"testsrc=s={size}:d=1:r=25"]
    if audio:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=440:d=1:sample_rate=44100"]
    subprocess.run(cmd + ["-pix_fmt", "yuv420p", str(path)], check=True)


class JoinTest(unittest.TestCase):
    def test_mixed_clips_keep_audio(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, out = Path(d, "a.mp4"), Path(d, "b.mp4"), Path(d, "o.mp4")
            make(a, "640x360", True)    # has sound
            make(b, "320x240", False)   # silent, different size
            join_videos([str(a), str(b)], str(out))
            r = probe(str(out))
            self.assertTrue(r.has_audio)
            self.assertAlmostEqual(r.duration, 2.0, delta=0.2)
            self.assertEqual((r.width, r.height), (1280, 720))


if __name__ == "__main__":
    unittest.main()
