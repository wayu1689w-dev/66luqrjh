"""Tests — ปลั๊กอินเสือเจาะข้อมูล"""

import os
import tempfile
import unittest

from plugins.plugin_suea_security import (
    DataLeakDetector, AccessMonitor, IntegrityChecker,
    ExfiltrationGuard, SecurityReport,
)


class TestDataLeakDetector(unittest.TestCase):
    def test_detect_api_key(self):
        text = 'config = {"api_key": "sk_live_1234567890abcdef"}'
        findings = DataLeakDetector.scan_text(text)
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0]["severity"], "HIGH")

    def test_detect_password(self):
        text = 'password = "supersecret123"'
        findings = DataLeakDetector.scan_text(text)
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0]["severity"], "CRITICAL")

    def test_detect_private_key(self):
        text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIB..."
        findings = DataLeakDetector.scan_text(text)
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0]["type"], "private_key")

    def test_clean_text(self):
        findings = DataLeakDetector.scan_text("สวัสดีครับ ระบบปกติ")
        self.assertEqual(len(findings), 0)

    def test_detect_thai_phone(self):
        text = "โทร = 0812345678"
        findings = DataLeakDetector.scan_text(text)
        self.assertGreater(len(findings), 0)

    def test_scan_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write('token = "abc123def456ghij789"')
            f.flush()
            findings = DataLeakDetector.scan_file(f.name)
        os.unlink(f.name)
        self.assertEqual(len(findings), 0)

    def test_scan_file_with_secret(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write('api_key = "sk_live_abcdefghijklmnop1234"')
            f.flush()
            findings = DataLeakDetector.scan_file(f.name)
        os.unlink(f.name)
        self.assertGreater(len(findings), 0)


class TestAccessMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = AccessMonitor()

    def test_log_access(self):
        entry = self.monitor.log_access("user1", "/api/data", "GET")
        self.assertEqual(entry["user_id"], "user1")
        self.assertTrue(entry["success"])

    def test_brute_force_detection(self):
        for _ in range(6):
            self.monitor.log_access("hacker", "/login", "POST",
                                    success=False)
        detected, msg = self.monitor.detect_brute_force("hacker")
        self.assertTrue(detected)
        self.assertIn("Brute force", msg)

    def test_no_brute_force(self):
        self.monitor.log_access("user1", "/login", "POST", success=False)
        detected, _ = self.monitor.detect_brute_force("user1")
        self.assertFalse(detected)

    def test_mass_access_detection(self):
        for i in range(25):
            self.monitor.log_access("scraper", f"/resource/{i}", "GET")
        alerts = self.monitor.detect_unusual_access("scraper")
        mass = [a for a in alerts if a["type"] == "MASS_ACCESS"]
        self.assertGreater(len(mass), 0)

    def test_sensitive_access_detection(self):
        for res in ["secret_keys", "token_store", "password_db", "backup_full"]:
            self.monitor.log_access("user1", res, "GET")
        alerts = self.monitor.detect_unusual_access("user1")
        sensitive = [a for a in alerts if a["type"] == "SENSITIVE_ACCESS"]
        self.assertGreater(len(sensitive), 0)

    def test_block_ip(self):
        self.monitor.block_ip("1.2.3.4")
        self.assertTrue(self.monitor.is_blocked("1.2.3.4"))
        self.assertFalse(self.monitor.is_blocked("5.6.7.8"))

    def test_rate_limit(self):
        for _ in range(30):
            self.monitor.check_rate_limit("user1", max_per_minute=30)
        ok, msg = self.monitor.check_rate_limit("user1", max_per_minute=30)
        self.assertFalse(ok)
        self.assertIn("เกินขีดจำกัด", msg)


class TestIntegrityChecker(unittest.TestCase):
    def test_baseline_and_check(self):
        checker = IntegrityChecker()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("original content")
            f.flush()
            checker.create_baseline([f.name])
            changes = checker.check_integrity()
            self.assertEqual(len(changes), 0)

        with open(f.name, "w") as fw:
            fw.write("TAMPERED content")
        changes = checker.check_integrity()
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["status"], "MODIFIED")
        os.unlink(f.name)

    def test_deleted_file(self):
        checker = IntegrityChecker()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("test")
            f.flush()
            checker.create_baseline([f.name])
        os.unlink(f.name)
        changes = checker.check_integrity()
        self.assertEqual(changes[0]["status"], "DELETED")


class TestExfiltrationGuard(unittest.TestCase):
    def test_blocked_destination(self):
        ok, msg = ExfiltrationGuard.check_destination("https://pastebin.com/xyz")
        self.assertFalse(ok)

    def test_allowed_destination(self):
        ok, _ = ExfiltrationGuard.check_destination("https://notion.so/page")
        self.assertTrue(ok)

    def test_oversized_export(self):
        ok, _ = ExfiltrationGuard.check_export_size(100 * 1024 * 1024)
        self.assertFalse(ok)

    def test_normal_export(self):
        ok, _ = ExfiltrationGuard.check_export_size(1 * 1024 * 1024)
        self.assertTrue(ok)

    def test_bulk_download_blocked(self):
        ok, _ = ExfiltrationGuard.check_bulk_download(200)
        self.assertFalse(ok)

    def test_normal_download(self):
        ok, _ = ExfiltrationGuard.check_bulk_download(10)
        self.assertTrue(ok)


class TestSecurityReport(unittest.TestCase):
    def test_clean_report(self):
        report = SecurityReport.generate([], [], [])
        self.assertEqual(report["overall"], "CLEAN")

    def test_critical_report(self):
        leaks = [{"severity": "CRITICAL", "type": "password"}]
        report = SecurityReport.generate(leaks, [], [])
        self.assertEqual(report["overall"], "CRITICAL")

    def test_warning_report(self):
        leaks = [{"severity": "HIGH", "type": "api_key"}]
        report = SecurityReport.generate(leaks, [], [])
        self.assertEqual(report["overall"], "WARNING")

    def test_integrity_warning(self):
        changes = [{"file": "x.py", "status": "MODIFIED"}]
        report = SecurityReport.generate([], [], changes)
        self.assertEqual(report["overall"], "WARNING")

    def test_report_summary(self):
        leaks = [{"severity": "CRITICAL"}, {"severity": "HIGH"}]
        alerts = [{"severity": "CRITICAL"}]
        report = SecurityReport.generate(leaks, alerts, [])
        self.assertEqual(report["summary"]["critical_count"], 2)
        self.assertEqual(report["summary"]["high_count"], 1)


if __name__ == "__main__":
    unittest.main()
