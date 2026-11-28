"""Tests — SUEA AI Dashboard"""

import unittest
import sys
import os
import json
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ.setdefault("WINDSOR_API_KEY", "")
os.environ.setdefault("METRICOOL_API_KEY", "")
os.environ.setdefault("TIKTOK_ACCESS_TOKEN", "")

from fastapi.testclient import TestClient
from suea_ai.app import app, init_db, DB_PATH, security_check, check_connector_status, CONNECTORS

# Ensure DB is initialised before any test
init_db()


class TestHealth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_ok(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "0.8.0")

    def test_root_returns_html(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/html", r.headers.get("content-type", ""))


class TestSecurity(unittest.TestCase):
    def test_blocked_action(self):
        result = security_check("PUBLISH")
        self.assertFalse(result["allowed"])

    def test_allowed_action(self):
        result = security_check("READ")
        self.assertTrue(result["allowed"])

    def test_ads_write_blocked(self):
        result = security_check("ADS_WRITE")
        self.assertFalse(result["allowed"])

    def test_security_policy_endpoint(self):
        client = TestClient(app)
        r = client.get("/api/security/policy")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["mode"], "FREE_MODE_ONLY")
        self.assertFalse(data["billing_enabled"])
        self.assertFalse(data["public_access"])


class TestConnectors(unittest.TestCase):
    def test_connector_no_credential(self):
        old = os.environ.get("WINDSOR_API_KEY", "")
        os.environ["WINDSOR_API_KEY"] = ""
        result = check_connector_status("windsor_tiktok_organic")
        self.assertEqual(result["status"], "no_credential")
        os.environ["WINDSOR_API_KEY"] = old

    def test_connector_with_credential(self):
        os.environ["WINDSOR_API_KEY"] = "test_key_123"
        result = check_connector_status("windsor_tiktok_organic")
        self.assertEqual(result["status"], "ready")
        os.environ["WINDSOR_API_KEY"] = ""

    def test_unknown_connector(self):
        result = check_connector_status("nonexistent")
        self.assertEqual(result["status"], "unknown")

    def test_connectors_endpoint(self):
        client = TestClient(app)
        r = client.get("/api/connectors")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data), len(CONNECTORS))

    def test_all_connectors_registered(self):
        expected = {"windsor_tiktok_organic", "windsor_instagram",
                    "windsor_facebook", "windsor_youtube",
                    "metricool", "tiktok_ads"}
        self.assertEqual(set(CONNECTORS.keys()), expected)


class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_dashboard_summary(self):
        r = self.client.get("/api/dashboard")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("products", data)
        self.assertIn("videos", data)
        self.assertIn("connectors_total", data)
        self.assertEqual(data["version"], "v008")


class TestProducts(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_list_products(self):
        r = self.client.get("/api/products")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), list)

    def test_product_not_found(self):
        r = self.client.get("/api/products/99999")
        self.assertEqual(r.status_code, 404)


class TestVideos(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_list_videos(self):
        r = self.client.get("/api/videos")
        self.assertEqual(r.status_code, 200)

    def test_video_performance(self):
        r = self.client.get("/api/videos/performance")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("total_videos", data)
        self.assertIn("total_views", data)


class TestAds(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_list_ads(self):
        r = self.client.get("/api/ads")
        self.assertEqual(r.status_code, 200)

    def test_ads_profit(self):
        r = self.client.get("/api/ads/profit")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("total_spend", data)
        self.assertIn("roas", data)


if __name__ == "__main__":
    unittest.main()
