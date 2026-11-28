"""Tests — KPI Engine + ACK Handler + Task Queue + Backup"""

import unittest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ.setdefault("WINDSOR_API_KEY", "")
os.environ.setdefault("METRICOOL_API_KEY", "")
os.environ.setdefault("TIKTOK_ACCESS_TOKEN", "")

from suea_ai.kpi_engine import (
    get_kpi_status, get_policy, enforce_policy, compute_kpi_score,
    validate_evidence, initial_status, AGENTS, POLICY,
)
from suea_ai.ack_handler import init_ack_table, record_ack, get_ack_log
from suea_ai.task_queue import init_task_table, enqueue, update_task, get_queue, queue_stats
from suea_ai.backup_worker import backup_now, list_backups
from suea_ai.app import app, init_db

from fastapi.testclient import TestClient

init_db()
init_ack_table()
init_task_table()


class TestKPIEngine(unittest.TestCase):
    def test_all_agents_listed(self):
        self.assertEqual(len(AGENTS), 9)
        self.assertIn("Claude", AGENTS)
        self.assertIn("GrokBot", AGENTS)

    def test_initial_status(self):
        s = initial_status("Claude")
        self.assertEqual(s["status"], "UNVERIFIED")
        self.assertFalse(s["ack"])
        self.assertIsNone(s["kpi_score"])

    def test_unknown_agent_raises(self):
        with self.assertRaises(ValueError):
            initial_status("Unknown_Bot")

    def test_get_kpi_status(self):
        statuses = get_kpi_status()
        self.assertEqual(len(statuses), 9)
        for s in statuses:
            self.assertEqual(s["status"], "UNVERIFIED")

    def test_policy_fields(self):
        p = get_policy()
        self.assertTrue(p["owner_control"])
        self.assertTrue(p["read_only"])
        self.assertTrue(p["free_only"])
        self.assertFalse(p["auto_spending"])
        self.assertEqual(p["report_destination"], "OWNER_ONLY")

    def test_enforce_blocks_spend(self):
        result = enforce_policy("spend")
        self.assertFalse(result["allowed"])

    def test_enforce_blocks_publish(self):
        result = enforce_policy("publish")
        self.assertFalse(result["allowed"])

    def test_enforce_allows_read(self):
        result = enforce_policy("read")
        self.assertTrue(result["allowed"])

    def test_compute_kpi_score_empty(self):
        s = initial_status("Claude")
        score = compute_kpi_score(s)
        self.assertEqual(score, 20.0)

    def test_compute_kpi_score_full(self):
        s = {
            "ack": True,
            "evidence": [{"type": "url", "value": "https://example.com"}],
            "completed_tasks": 5,
            "errors": [],
        }
        score = compute_kpi_score(s)
        self.assertEqual(score, 100.0)

    def test_validate_evidence_empty(self):
        result = validate_evidence([])
        self.assertFalse(result["valid"])

    def test_validate_evidence_valid(self):
        result = validate_evidence([{"type": "url", "value": "test"}])
        self.assertTrue(result["valid"])


class TestACKHandler(unittest.TestCase):
    def test_record_ack_with_evidence(self):
        result = record_ack("Claude", "task_001", "screenshot.png")
        self.assertEqual(result["status"], "ACK")

    def test_record_ack_without_evidence(self):
        result = record_ack("Claude", "task_002", "")
        self.assertEqual(result["status"], "NO_EVIDENCE")

    def test_get_ack_log(self):
        log = get_ack_log(10)
        self.assertIsInstance(log, list)


class TestTaskQueue(unittest.TestCase):
    def test_enqueue(self):
        result = enqueue("analytics", "ดูสถิติ TikTok", "Windsor.ai")
        self.assertEqual(result["status"], "QUEUED")
        self.assertIn("id", result)

    def test_update_task(self):
        t = enqueue("report", "สรุปรายวัน", "Claude")
        result = update_task(t["id"], "DONE", "completed")
        self.assertEqual(result["status"], "DONE")

    def test_get_queue(self):
        q = get_queue()
        self.assertIsInstance(q, list)

    def test_queue_stats(self):
        stats = queue_stats()
        self.assertIn("total", stats)
        self.assertIn("queued", stats)
        self.assertIn("done", stats)


class TestBackup(unittest.TestCase):
    def test_backup_now(self):
        result = backup_now()
        self.assertTrue(result["ok"])
        self.assertIn("size_kb", result)

    def test_list_backups(self):
        backup_now()
        backups = list_backups()
        self.assertGreater(len(backups), 0)


class TestKPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_kpi_report(self):
        r = self.client.get("/api/kpi")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["mode"], "LOCAL_ONLY")
        self.assertTrue(data["read_only"])
        self.assertEqual(len(data["agents"]), 9)

    def test_kpi_policy(self):
        r = self.client.get("/api/kpi/policy")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["owner_control"])

    def test_kpi_enforce_blocked(self):
        r = self.client.post("/api/kpi/enforce", json={"action": "spend"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["allowed"])

    def test_config_endpoint(self):
        r = self.client.get("/api/config")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["FREE_ONLY"])
        self.assertTrue(data["READ_ONLY"])
        self.assertFalse(data["AUTO_AD_SPEND"])

    def test_ack_submit(self):
        r = self.client.post("/api/ack", json={
            "agent": "Claude", "task_id": "t1", "evidence": "done"
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ACK")

    def test_ack_log(self):
        r = self.client.get("/api/ack/log")
        self.assertEqual(r.status_code, 200)

    def test_task_create(self):
        r = self.client.post("/api/tasks", json={
            "task_type": "analytics", "description": "test task"
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "QUEUED")

    def test_task_list(self):
        r = self.client.get("/api/tasks")
        self.assertEqual(r.status_code, 200)

    def test_task_stats(self):
        r = self.client.get("/api/tasks/stats")
        self.assertEqual(r.status_code, 200)
        self.assertIn("total", r.json())

    def test_backup_endpoint(self):
        r = self.client.post("/api/backup")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])

    def test_backup_list(self):
        r = self.client.get("/api/backup/list")
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
