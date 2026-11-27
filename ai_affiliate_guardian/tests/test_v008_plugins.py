"""Tests — v008 Plugin Connector"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_affiliate_guardian.security.auth import create_session, _sessions
from ai_affiliate_guardian.core.kill_switch import SWITCHES

from plugins.plugin_connector import (
    get_plugin_info, list_all_plugins, list_by_category,
    execute_plugin, plugin_health_report, plugin_count, categories,
    search_plugins, list_connected, list_disabled,
)


class TestPluginInfo(unittest.TestCase):
    def test_get_known_plugin(self):
        info = get_plugin_info("claude")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "Claude")

    def test_unknown_plugin(self):
        self.assertIsNone(get_plugin_info("nonexistent"))

    def test_list_all(self):
        plugins = list_all_plugins()
        self.assertGreater(len(plugins), 20)

    def test_list_by_category(self):
        ai = list_by_category("ai_text")
        self.assertGreater(len(ai), 0)

    def test_plugin_count(self):
        self.assertGreater(plugin_count(), 20)

    def test_categories(self):
        cats = categories()
        self.assertIn("ai_text", cats)
        self.assertIn("analytics", cats)
        self.assertIn("storage", cats)

    def test_canva_disabled(self):
        info = get_plugin_info("canva")
        self.assertTrue(info.get("disabled"))

    def test_vidiq_disabled(self):
        info = get_plugin_info("vidiq")
        self.assertTrue(info.get("disabled"))

    def test_plugin_count_with_new(self):
        self.assertGreater(plugin_count(), 30)

    def test_search_by_name(self):
        results = search_plugins("claude")
        names = [r["name"] for r in results]
        self.assertIn("Claude", names)
        self.assertIn("Claude Academy", names)

    def test_search_by_category(self):
        results = search_plugins("learning")
        self.assertGreater(len(results), 0)

    def test_list_connected(self):
        connected = list_connected()
        keys = [p["key"] for p in connected]
        self.assertIn("claude", keys)
        self.assertNotIn("canva", keys)
        self.assertNotIn("vidiq", keys)

    def test_list_disabled(self):
        disabled = list_disabled()
        keys = [p["key"] for p in disabled]
        self.assertIn("canva", keys)
        self.assertIn("vidiq", keys)

    def test_new_categories(self):
        cats = categories()
        self.assertIn("learning", cats)
        self.assertIn("memory", cats)
        self.assertIn("meeting", cats)


class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        _sessions.clear()
        for k in SWITCHES:
            SWITCHES[k] = False

    def tearDown(self):
        for k in SWITCHES:
            SWITCHES[k] = True
        _sessions.clear()

    def test_execute_valid(self):
        s = create_session("user1", "editor")
        result = execute_plugin("claude", s["token"], "read")
        self.assertTrue(result["ok"])
        self.assertEqual(result["plugin"], "Claude")
        self.assertEqual(result["user"], "user1")

    def test_execute_bad_session(self):
        result = execute_plugin("claude", "fake-token")
        self.assertFalse(result["ok"])
        self.assertIn("Session", result["error"])

    def test_execute_no_permission(self):
        s = create_session("viewer1", "viewer")
        result = execute_plugin("notion", s["token"], "write")
        self.assertFalse(result["ok"])
        self.assertIn("ไม่มีสิทธิ์", result["error"])

    def test_execute_kill_switch(self):
        SWITCHES["KILL_ALL_EXTERNAL"] = True
        s = create_session("admin1", "admin")
        result = execute_plugin("claude", s["token"])
        self.assertFalse(result["ok"])
        self.assertIn("Kill Switch", result["error"])

    def test_execute_disabled_plugin(self):
        s = create_session("admin1", "admin")
        result = execute_plugin("canva", s["token"])
        self.assertFalse(result["ok"])
        self.assertIn("Canva", result["error"])

    def test_execute_unknown_plugin(self):
        s = create_session("user1", "editor")
        result = execute_plugin("nonexistent", s["token"])
        self.assertFalse(result["ok"])

    def test_secret_in_payload(self):
        SWITCHES["KILL_MCP"] = False
        s = create_session("user1", "editor")
        result = execute_plugin(
            "claude", s["token"], "read",
            payload={"password": "secret123"}
        )
        self.assertFalse(result["ok"])
        self.assertIn("Secret", result["error"])

    def test_health_report(self):
        s = create_session("user1", "editor")
        execute_plugin("claude", s["token"])
        report = plugin_health_report()
        self.assertIn("overall", report)


if __name__ == "__main__":
    unittest.main()
