"""Tests — Plugin Auto-Discovery & Auto-Response System"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from plugins.plugin_auto_discovery import (
    total_count, count_by_status, search, search_by_task,
    list_by_status, list_by_category, auto_match, auto_respond,
    health_summary, CATEGORIES, TASK_PLUGIN_MAP,
)


class TestRegistry(unittest.TestCase):
    def test_total_over_100(self):
        self.assertGreaterEqual(total_count(), 100)

    def test_categories_exist(self):
        self.assertGreater(len(CATEGORIES), 15)

    def test_task_types(self):
        self.assertGreater(len(TASK_PLUGIN_MAP), 15)

    def test_count_by_status(self):
        counts = count_by_status()
        self.assertIn("connected", counts)
        self.assertGreater(counts["connected"], 10)

    def test_no_duplicate_keys(self):
        from plugins.plugin_auto_discovery import EXTENDED_REGISTRY
        keys = list(EXTENDED_REGISTRY.keys())
        self.assertEqual(len(keys), len(set(keys)))


class TestSearch(unittest.TestCase):
    def test_search_by_name(self):
        results = search("claude")
        names = [r["name"] for r in results]
        self.assertIn("Claude", names)

    def test_search_by_category(self):
        results = search("security")
        self.assertGreater(len(results), 0)

    def test_search_no_match(self):
        results = search("zzzznonexistent")
        self.assertEqual(len(results), 0)

    def test_search_thai(self):
        results = search("เสือ")
        self.assertGreater(len(results), 0)

    def test_search_by_task_text(self):
        results = search_by_task("text")
        self.assertGreater(len(results), 3)
        names = [r["name"] for r in results]
        self.assertIn("Claude", names)

    def test_search_by_task_video(self):
        results = search_by_task("video")
        self.assertGreater(len(results), 0)

    def test_search_by_task_security(self):
        results = search_by_task("security")
        self.assertGreater(len(results), 0)
        names = [r["name"] for r in results]
        self.assertIn("เสือเจาะข้อมูล", names)

    def test_search_by_task_unknown(self):
        results = search_by_task("unknown_task_type")
        self.assertEqual(len(results), 0)


class TestListBy(unittest.TestCase):
    def test_list_connected(self):
        connected = list_by_status("connected")
        self.assertGreater(len(connected), 10)

    def test_list_disabled(self):
        disabled = list_by_status("disabled")
        keys = [d["key"] for d in disabled]
        self.assertIn("canva", keys)
        self.assertIn("vidiq", keys)

    def test_list_active_internal(self):
        active = list_by_status("active")
        self.assertGreater(len(active), 0)

    def test_list_by_category_ads(self):
        ads = list_by_category("ads")
        self.assertGreater(len(ads), 0)


class TestAutoMatch(unittest.TestCase):
    def test_match_thai_video(self):
        matches = auto_match("ตัดต่อวิดีโอสั้น")
        self.assertGreater(len(matches), 0)
        tasks = [m["matched_task"] for m in matches]
        self.assertIn("video", tasks)

    def test_match_english_analytics(self):
        matches = auto_match("get analytics report from TikTok")
        self.assertGreater(len(matches), 0)

    def test_match_security(self):
        matches = auto_match("ตรวจความปลอดภัยระบบ")
        self.assertGreater(len(matches), 0)
        names = [m["name"] for m in matches]
        self.assertIn("เสือเจาะข้อมูล", names)

    def test_match_multi_task(self):
        matches = auto_match("เขียนโพสต์โซเชียลพร้อมรูปภาพ")
        tasks = set(m["matched_task"] for m in matches)
        self.assertTrue(len(tasks) >= 2)

    def test_no_match(self):
        matches = auto_match("zzzzz")
        self.assertEqual(len(matches), 0)


class TestAutoRespond(unittest.TestCase):
    def test_respond_with_recommendation(self):
        response = auto_respond("เขียนบทความสั้น")
        self.assertIn("recommended", response)
        self.assertIsNotNone(response["recommended"])
        self.assertEqual(response["recommended"]["status"], "connected")

    def test_respond_has_timestamp(self):
        response = auto_respond("วิเคราะห์ข้อมูล")
        self.assertIn("timestamp", response)

    def test_respond_separates_needs_setup(self):
        response = auto_respond("ส่งอีเมลแคมเปญ")
        needs = response["needs_setup"]
        for p in needs:
            self.assertNotIn(p["status"], ("connected", "active", "disabled"))

    def test_respond_separates_disabled(self):
        response = auto_respond("ออกแบบกราฟิก")
        disabled_keys = [d["key"] for d in response["disabled"]]
        self.assertIn("canva", disabled_keys)

    def test_respond_security_prefers_internal(self):
        response = auto_respond("scan for security threats")
        rec = response["recommended"]
        self.assertIsNotNone(rec)
        self.assertEqual(rec["name"], "เสือเจาะข้อมูล")


class TestHealthSummary(unittest.TestCase):
    def test_summary_structure(self):
        summary = health_summary()
        self.assertGreaterEqual(summary["total_plugins"], 100)
        self.assertGreater(summary["categories"], 15)
        self.assertGreater(summary["connected"], 10)
        self.assertGreater(summary["task_types"], 15)

    def test_summary_has_all_fields(self):
        summary = health_summary()
        for field in ["total_plugins", "categories", "status", "connected",
                      "active_internal", "needs_reconnect", "disabled"]:
            self.assertIn(field, summary)


if __name__ == "__main__":
    unittest.main()
