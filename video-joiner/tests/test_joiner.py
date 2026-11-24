import subprocess, tempfile, unittest
from pathlib import Path
from videojoiner import join_videos, probe
from videojoiner.joiner import JoinError


def make(path, size, audio, d=1):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"testsrc=s={size}:d={d}:r=25"]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:d={d}:sample_rate=44100"]
    subprocess.run(cmd + ["-pix_fmt", "yuv420p", str(path)], check=True)


def mean_volume(path):
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    line = next(l for l in r.stderr.splitlines() if "mean_volume" in l)
    return float(line.split("mean_volume:")[1].split()[0])


class JoinTest(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.d = Path(self._t.name)
        self.a, self.b = self.d / "a.mp4", self.d / "b.mp4"
        make(self.a, "640x360", True, 2)    # has sound
        make(self.b, "320x240", False, 2)   # silent, different size
        self.out = str(self.d / "o.mp4")

    def tearDown(self):
        self._t.cleanup()

    def test_mixed_clips_keep_audio(self):
        join_videos([str(self.a), str(self.b)], self.out)
        r = probe(self.out)
        self.assertTrue(r.has_audio)
        self.assertAlmostEqual(r.duration, 4.0, delta=0.2)
        self.assertEqual((r.width, r.height), (1280, 720))
        self.assertGreater(mean_volume(self.out), -60)   # sound really there

    def test_crossfade_shortens_and_keeps_audio(self):
        join_videos([str(self.a), str(self.b)], self.out, crossfade=0.5)
        r = probe(self.out)
        self.assertTrue(r.has_audio)
        self.assertAlmostEqual(r.duration, 3.5, delta=0.2)

    def test_crossfade_too_long_rejected(self):
        with self.assertRaises(JoinError):
            join_videos([str(self.a), str(self.b)], self.out, crossfade=1.5)

    def test_music_over_silent_clips(self):
        music = self.d / "m.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        "sine=frequency=220:d=1", str(music)], check=True)  # shorter -> loops
        join_videos([str(self.b), str(self.b)], self.out, music=str(music))
        self.assertGreater(mean_volume(self.out), -60)   # music audible over silence
        self.assertAlmostEqual(probe(self.out).duration, 4.0, delta=0.2)

    def test_progress_reaches_one(self):
        seen = []
        join_videos([str(self.a), str(self.b)], self.out, progress=seen.append)
        self.assertEqual(seen[-1], 1.0)
        self.assertEqual(seen, sorted(seen))


if __name__ == "__main__":
    unittest.main()
