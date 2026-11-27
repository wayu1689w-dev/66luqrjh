"""Tests — v008 Community Board"""

import unittest

from ai_affiliate_guardian.community.board import (
    Board, SpamFilter, Moderator, reset,
)


class TestCommunityBoard(unittest.TestCase):
    def setUp(self):
        reset()
        self.board = Board()
        self.board.register_member("u1", "เสือ")
        self.board.register_member("u2", "แมว")
        self.cat = self.board.add_category("ทั่วไป", "พูดคุยทั่วไป")

    def test_create_thread(self):
        t = self.board.create_thread("สวัสดี", "ทดสอบ", "u1", self.cat.id)
        self.assertEqual(t.title, "สวัสดี")
        self.assertEqual(t.author_id, "u1")

    def test_non_member_cannot_post(self):
        with self.assertRaises(ValueError):
            self.board.create_thread("x", "y", "stranger", self.cat.id)

    def test_add_comment(self):
        t = self.board.create_thread("ทดสอบ", "เนื้อหา", "u1", self.cat.id)
        c = t.add_comment("u2", "ดีจัง!")
        self.assertEqual(c["text"], "ดีจัง!")
        self.assertEqual(len(t.comments), 1)

    def test_toggle_like(self):
        t = self.board.create_thread("ถูกใจ", "ทดสอบ", "u1", self.cat.id)
        self.assertTrue(t.toggle_like("u2"))
        self.assertEqual(len(t.likes), 1)
        self.assertFalse(t.toggle_like("u2"))
        self.assertEqual(len(t.likes), 0)

    def test_search_threads(self):
        self.board.create_thread("อาหาร SUEA", "รีวิวอาหาร", "u1", self.cat.id)
        self.board.create_thread("ท่องเที่ยว", "เที่ยวเชียงใหม่", "u2", self.cat.id)
        results = self.board.search_threads("อาหาร")
        self.assertEqual(len(results), 1)

    def test_report_thread(self):
        t = self.board.create_thread("ทดสอบ", "เนื้อหา", "u1", self.cat.id)
        r = t.report("u2", "เนื้อหาไม่เหมาะสม")
        self.assertEqual(r["status"], "pending")

    def test_notifications(self):
        self.board.notify("u1", "มีคอมเมนต์ใหม่", "THR-001")
        notifs = self.board.get_notifications("u1")
        self.assertEqual(len(notifs), 1)

    def test_category_filter(self):
        cat2 = self.board.add_category("เทคโนโลยี")
        self.board.create_thread("AI", "ปัญญาประดิษฐ์", "u1", cat2.id)
        self.board.create_thread("อาหาร", "รีวิว", "u1", self.cat.id)
        results = self.board.get_threads_by_category(cat2.id)
        self.assertEqual(len(results), 1)


class TestSpamFilter(unittest.TestCase):
    def test_clean_text(self):
        ok, _ = SpamFilter.check("ขอบคุณครับ")
        self.assertTrue(ok)

    def test_spam_detected(self):
        ok, msg = SpamFilter.check("สมัครสล็อตวันนี้")
        self.assertFalse(ok)
        self.assertIn("สล็อต", msg)

    def test_casino_blocked(self):
        ok, _ = SpamFilter.check("win big at casino now")
        self.assertFalse(ok)


class TestModerator(unittest.TestCase):
    def setUp(self):
        reset()
        self.board = Board()
        self.board.register_member("u1", "เสือ")
        cat = self.board.add_category("ทั่วไป")
        self.thread = self.board.create_thread("test", "body", "u1", cat.id)

    def test_pin_thread(self):
        Moderator.pin_thread(self.thread)
        self.assertTrue(self.thread.is_pinned)

    def test_lock_thread(self):
        Moderator.lock_thread(self.thread)
        self.assertTrue(self.thread.is_locked)

    def test_resolve_report(self):
        r = self.thread.report("u2", "spam")
        Moderator.resolve_report(r, "removed")
        self.assertEqual(r["status"], "removed")


if __name__ == "__main__":
    unittest.main()
