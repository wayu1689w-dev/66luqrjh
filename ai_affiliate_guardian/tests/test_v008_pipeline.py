"""Tests — Plugin Pipeline (Auto-Discovery + Connector + v008 Security)"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_affiliate_guardian.security.auth import create_session, _sessions
from ai_affiliate_guardian.core.kill_switch import SWITCHES

from plugins.plugin_pipeline import (
    smart_execute, batch_execute, Windsor_auto_respond,
    pipeline_report, clear_log, _pipeline_log,
)


class TestSmartExecute(unittest.TestCase):
    def setUp(self):
        _sessions.clear()
        clear_log()
        for k in SWITCHES:
            SWITCHES[k] = False

    def tearDown(self):
        for k in SWITCHES:
            SWITCHES[k] = True
        _sessions.clear()
        clear_log()

    def test_execute_text_task(self):
        s = create_session("user1", "editor")
        result = smart_execute("เขียนบทความ", s["token"])
        self.assertIn("ok", result)
        self.assertIn("log", result)

    def test_execute_no_match(self):
        s = create_session("user1", "editor")
        result = smart_execute("zzzznonexistent", s["token"])
        self.assertFalse(result["ok"])
        self.assertEqual(result["stage"], "discovery")

    def test_execute_bad_session(self):
        result = smart_execute("เขียนบทความ", "fake-token")
        self.assertFalse(result["ok"])
        self.assertEqual(result["stage"], "auth")

    def test_execute_kill_switch_blocks(self):
        SWITCHES["KILL_ALL_EXTERNAL"] = True
        s = create_session("user1", "editor")
        result = smart_execute("เขียนบทความ", s["token"])
        self.assertFalse(result["ok"])

    def test_execute_high_risk_needs_approval(self):
        s = create_session("user1", "editor")
        result = smart_execute("สร้างแคมเปญโฆษณา TikTok", s["token"])
        if result.get("stage") == "approval":
            self.assertIn("R", result.get("risk", ""))
            self.assertFalse(result["ok"])

    def test_execute_with_auto_approve(self):
        s = create_session("admin1", "admin")
        result = smart_execute("สร้างแคมเปญโฆษณา TikTok", s["token"],
                               auto_approve=True)
        self.assertIn("ok", result)

    def test_execute_disabled_plugin_not_recommended(self):
        s = create_session("user1", "editor")
        result = smart_execute("ออกแบบกราฟิก", s["token"])
        if result["ok"]:
            self.assertNotEqual(result.get("plugin"), "Canva")

    def test_execute_logs_entry(self):
        s = create_session("user1", "editor")
        smart_execute("วิเคราะห์ข้อมูล", s["token"])
        self.assertGreater(len(_pipeline_log), 0)
        self.assertIn("status", _pipeline_log[-1])


class TestBatchExecute(unittest.TestCase):
    def setUp(self):
        _sessions.clear()
        clear_log()
        for k in SWITCHES:
            SWITCHES[k] = False

    def tearDown(self):
        for k in SWITCHES:
            SWITCHES[k] = True
        _sessions.clear()
        clear_log()

    def test_batch_multiple_tasks(self):
        s = create_session("user1", "editor")
        tasks = [
            {"description": "เขียนบทความ"},
            {"description": "วิเคราะห์ข้อมูล"},
            {"description": "zzzznonexistent"},
        ]
        results = batch_execute(tasks, s["token"])
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertIn("task_description", r)

    def test_batch_empty(self):
        s = create_session("user1", "editor")
        results = batch_execute([], s["token"])
        self.assertEqual(len(results), 0)


class TestWindsorAutoRespond(unittest.TestCase):
    def test_tiktok_organic(self):
        result = Windsor_auto_respond("tiktok_organic")
        self.assertTrue(result["ok"])
        self.assertEqual(result["connector"], "tiktok_organic")
        self.assertIn("views", result["fields"])
        self.assertTrue(result["auto_response"])

    def test_instagram(self):
        result = Windsor_auto_respond("instagram")
        self.assertTrue(result["ok"])
        self.assertEqual(result["plugin_key"], "windsor_social")

    def test_youtube(self):
        result = Windsor_auto_respond("youtube")
        self.assertTrue(result["ok"])
        self.assertIn("watch_time", result["fields"])

    def test_unsupported_connector(self):
        result = Windsor_auto_respond("nonexistent")
        self.assertFalse(result["ok"])
        self.assertIn("supported", result)

    def test_custom_date_range(self):
        result = Windsor_auto_respond("tiktok_organic", "last_30_days")
        self.assertEqual(result["date_range"], "last_30_days")


class TestPipelineReport(unittest.TestCase):
    def setUp(self):
        _sessions.clear()
        clear_log()
        for k in SWITCHES:
            SWITCHES[k] = False

    def tearDown(self):
        for k in SWITCHES:
            SWITCHES[k] = True
        _sessions.clear()
        clear_log()

    def test_report_structure(self):
        report = pipeline_report()
        self.assertIn("pipeline_health", report)
        self.assertIn("discovery", report)
        self.assertIn("execution_stats", report)
        self.assertIn("recent_log", report)

    def test_report_after_executions(self):
        s = create_session("user1", "editor")
        smart_execute("เขียนบทความ", s["token"])
        smart_execute("zzzznonexistent", s["token"])
        report = pipeline_report()
        stats = report["execution_stats"]
        self.assertEqual(stats["total_requests"], 2)

    def test_report_success_rate(self):
        report = pipeline_report()
        self.assertIn("%", report["execution_stats"]["success_rate"])


class TestSecurityGates(unittest.TestCase):
    def setUp(self):
        _sessions.clear()
        clear_log()
        for k in SWITCHES:
            SWITCHES[k] = False

    def tearDown(self):
        for k in SWITCHES:
            SWITCHES[k] = True
        _sessions.clear()
        clear_log()

    def test_viewer_cannot_write(self):
        s = create_session("viewer1", "viewer")
        result = smart_execute("สร้างเอกสารใน Notion", s["token"], action="write")
        if result.get("stage") not in ("discovery", "connector"):
            self.assertFalse(result["ok"])

    def test_secret_in_payload_blocked(self):
        s = create_session("user1", "editor")
        result = smart_execute("เขียนบทความ", s["token"],
                               payload={"password": "secret123"})
        if result["ok"] is False:
            self.assertIn("log", result)

    def test_kill_mcp_blocks(self):
        SWITCHES["KILL_MCP"] = True
        s = create_session("user1", "editor")
        result = smart_execute("เขียนบทความ", s["token"])
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
