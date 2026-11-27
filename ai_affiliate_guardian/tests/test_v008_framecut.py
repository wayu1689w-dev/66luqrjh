"""Tests — v008 FrameCut Studio"""

import os
import tempfile
import unittest

from ai_affiliate_guardian.framecut.studio import (
    Script, Storyboard, SubtitleTrack, Timeline, AudioGuard,
    ProductGroup, create_zip_export, reset,
)


class TestScript(unittest.TestCase):
    def setUp(self):
        reset()

    def test_create_script(self):
        s = Script("สินค้าทดสอบ", "review")
        s.add_scene("hook", "เปิดด้วยคำถาม", 3.0)
        s.add_scene("demo", "แสดงสินค้า", 10.0)
        s.add_scene("cta", "ปิดด้วย CTA", 5.0)
        self.assertEqual(len(s.scenes), 3)
        self.assertAlmostEqual(s.total_duration(), 18.0)

    def test_script_to_dict(self):
        s = Script("ทดสอบ")
        s.add_scene("intro", "สวัสดี", 5.0)
        d = s.to_dict()
        self.assertIn("scenes", d)
        self.assertEqual(d["product_name"], "ทดสอบ")


class TestStoryboard(unittest.TestCase):
    def setUp(self):
        reset()

    def test_create_storyboard(self):
        s = Script("สินค้า")
        scene = s.add_scene("hook", "เปิด", 3.0)
        sb = Storyboard(s)
        self.assertEqual(len(sb.frames), 1)

    def test_set_image(self):
        s = Script("สินค้า")
        scene = s.add_scene("hook", "เปิด", 3.0)
        sb = Storyboard(s)
        result = sb.set_image(scene["id"], "/tmp/test.png")
        self.assertTrue(result)


class TestSubtitleTrack(unittest.TestCase):
    def test_srt_output(self):
        sub = SubtitleTrack()
        sub.add_entry(0.0, 3.0, "สวัสดีครับ")
        sub.add_entry(3.0, 6.5, "วันนี้มารีวิว")
        srt = sub.to_srt()
        self.assertIn("สวัสดีครับ", srt)
        self.assertIn("-->", srt)
        self.assertEqual(sub.total_entries(), 2)


class TestTimeline(unittest.TestCase):
    def setUp(self):
        reset()

    def test_add_clips(self):
        tl = Timeline()
        tl.add_clip("video", "clip1.mp4", 0.0, 10.0, "intro")
        tl.add_clip("audio", "music.mp3", 0.0, 30.0, "bg music")
        tl.add_clip("subtitle", "sub.srt", 0.0, 10.0)
        self.assertAlmostEqual(tl.total_duration(), 30.0)

    def test_invalid_track(self):
        tl = Timeline()
        with self.assertRaises(ValueError):
            tl.add_clip("invalid", "x.mp4", 0.0, 5.0)


class TestAudioGuard(unittest.TestCase):
    def test_normal_level(self):
        ok, _ = AudioGuard.check_level(-10.0)
        self.assertTrue(ok)

    def test_too_loud(self):
        ok, msg = AudioGuard.check_level(-1.0)
        self.assertFalse(ok)
        self.assertIn("ดังเกิน", msg)

    def test_too_quiet(self):
        ok, msg = AudioGuard.check_level(-50.0)
        self.assertFalse(ok)
        self.assertIn("เบาเกิน", msg)


class TestProductGroup(unittest.TestCase):
    def test_add_remove(self):
        pg = ProductGroup("อาหาร")
        pg.add_product("P001")
        pg.add_product("P002")
        self.assertEqual(len(pg.products), 2)
        pg.remove_product("P001")
        self.assertEqual(len(pg.products), 1)

    def test_no_duplicate(self):
        pg = ProductGroup("เครื่องดื่ม")
        pg.add_product("P001")
        pg.add_product("P001")
        self.assertEqual(len(pg.products), 1)


class TestZipExport(unittest.TestCase):
    def test_create_zip(self):
        with tempfile.TemporaryDirectory() as td:
            f1 = os.path.join(td, "a.txt")
            with open(f1, "w") as f:
                f.write("test")
            out = os.path.join(td, "export.zip")
            result = create_zip_export([f1], out)
            self.assertTrue(os.path.exists(result))


if __name__ == "__main__":
    unittest.main()
