"""Tests — v008 Automation Health Monitor"""

import unittest

from ai_affiliate_guardian.automation.health_monitor import (
    HealthMonitor, HealthStatus,
)


class TestHealthMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = HealthMonitor()

    def test_register_component(self):
        c = self.monitor.register("guardian")
        self.assertEqual(c.name, "guardian")
        self.assertEqual(c.status, HealthStatus.UNKNOWN)

    def test_report_ok(self):
        c = self.monitor.register("db")
        c.report_ok()
        self.assertEqual(c.status, HealthStatus.HEALTHY)
        self.assertEqual(c.consecutive_failures, 0)

    def test_degraded_after_one_failure(self):
        c = self.monitor.register("api")
        c.report_error("timeout")
        self.assertEqual(c.status, HealthStatus.DEGRADED)

    def test_down_after_three_failures(self):
        c = self.monitor.register("api")
        c.report_error()
        c.report_error()
        c.report_error()
        self.assertEqual(c.status, HealthStatus.DOWN)

    def test_recovery_after_ok(self):
        c = self.monitor.register("api")
        c.report_error()
        c.report_error()
        c.report_error()
        c.report_ok()
        self.assertEqual(c.status, HealthStatus.HEALTHY)

    def test_overall_healthy(self):
        c1 = self.monitor.register("a")
        c2 = self.monitor.register("b")
        c1.report_ok()
        c2.report_ok()
        self.assertEqual(self.monitor.overall_status(), HealthStatus.HEALTHY)

    def test_overall_down(self):
        c = self.monitor.register("a")
        c.report_error()
        c.report_error()
        c.report_error()
        self.assertEqual(self.monitor.overall_status(), HealthStatus.DOWN)

    def test_alerts(self):
        self.monitor.add_alert("db", "slow query", "warning")
        self.monitor.add_alert("api", "timeout", "critical")
        self.assertEqual(len(self.monitor.get_alerts()), 2)
        self.assertEqual(len(self.monitor.get_alerts("critical")), 1)

    def test_generate_report(self):
        self.monitor.register("x").report_ok()
        report = self.monitor.generate_report()
        self.assertEqual(report["overall"], "healthy")
        self.assertIn("components", report)

    def test_clear_alerts(self):
        self.monitor.add_alert("x", "test")
        self.monitor.clear_alerts()
        self.assertEqual(len(self.monitor.get_alerts()), 0)


if __name__ == "__main__":
    unittest.main()
