"""Tests for Plugin Catalog — 500+ plugins, 8 categories, all DISABLED"""
import unittest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plugin_os.plugin_catalog import (
    ALL_PLUGINS,
    CATEGORIES,
    AI_DEVELOPMENT,
    CONTENT_WRITING,
    ECOMMERCE,
    DOCUMENTS,
    DATA_ANALYTICS,
    CONTROL_CENTER,
    TIKTOK_PLUGINS,
    SECURITY,
    get_total_count,
    get_category_counts,
    get_by_provider,
    get_by_risk,
    get_approval_required,
    get_connected,
    get_not_connected,
    search_plugins,
)


class TestCatalogSize(unittest.TestCase):
    def test_total_at_least_500(self):
        self.assertGreaterEqual(get_total_count(), 500)

    def test_eight_categories(self):
        self.assertEqual(len(CATEGORIES), 8)

    def test_ai_dev_at_least_100(self):
        self.assertGreaterEqual(len(AI_DEVELOPMENT), 100)

    def test_content_at_least_100(self):
        self.assertGreaterEqual(len(CONTENT_WRITING), 100)

    def test_ecommerce_at_least_100(self):
        self.assertGreaterEqual(len(ECOMMERCE), 100)

    def test_documents_at_least_50(self):
        self.assertGreaterEqual(len(DOCUMENTS), 50)

    def test_data_at_least_50(self):
        self.assertGreaterEqual(len(DATA_ANALYTICS), 50)

    def test_control_at_least_50(self):
        self.assertGreaterEqual(len(CONTROL_CENTER), 50)

    def test_tiktok_at_least_50(self):
        self.assertGreaterEqual(len(TIKTOK_PLUGINS), 50)

    def test_security_at_least_50(self):
        self.assertGreaterEqual(len(SECURITY), 50)


class TestAllDisabled(unittest.TestCase):
    def test_no_plugin_connected(self):
        connected = get_connected()
        self.assertEqual(len(connected), 0, "ALL connections must be DISABLED")

    def test_all_not_connected(self):
        self.assertEqual(len(get_not_connected()), get_total_count())

    def test_no_plugin_authorized(self):
        for p in ALL_PLUGINS:
            self.assertFalse(p["authorized"], f"{p['name']} must not be authorized")

    def test_all_state_discovered(self):
        for p in ALL_PLUGINS:
            self.assertEqual(p["state"], "DISCOVERED", f"{p['name']} state wrong")


class TestPluginStructure(unittest.TestCase):
    def test_all_have_required_fields(self):
        required = {"id", "name", "provider", "category", "tools", "risk",
                     "approval_required", "state", "connected", "authorized"}
        for p in ALL_PLUGINS:
            self.assertTrue(required.issubset(p.keys()), f"{p['name']} missing fields")

    def test_unique_ids(self):
        ids = [p["id"] for p in ALL_PLUGINS]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate plugin IDs found")

    def test_id_format(self):
        for p in ALL_PLUGINS:
            self.assertTrue(p["id"].startswith("PLG-"), f"{p['id']} bad format")

    def test_risk_levels_valid(self):
        valid = {"R0", "R1", "R2", "R3", "R4", "R5"}
        for p in ALL_PLUGINS:
            self.assertIn(p["risk"], valid, f"{p['name']} has invalid risk {p['risk']}")


class TestRiskDistribution(unittest.TestCase):
    def test_r5_requires_approval(self):
        r5 = get_by_risk("R5")
        self.assertGreater(len(r5), 0)
        for p in r5:
            self.assertTrue(p["approval_required"],
                            f"R5 plugin {p['name']} must require approval")

    def test_r0_no_approval(self):
        r0 = get_by_risk("R0")
        for p in r0:
            self.assertFalse(p["approval_required"],
                             f"R0 plugin {p['name']} should not require approval")

    def test_finance_ads_r5(self):
        finance_ads = [p for p in ALL_PLUGINS
                       if any(t in p["tools"] for t in
                              ["ad_create", "gmv_campaign"])]
        for p in finance_ads:
            self.assertIn(p["risk"], ("R4", "R5"),
                          f"{p['name']} finance/ads must be R4+")


class TestProviderCoverage(unittest.TestCase):
    def test_claude_plugins(self):
        claude = get_by_provider("claude")
        self.assertGreaterEqual(len(claude), 5)

    def test_openai_plugins(self):
        openai = get_by_provider("openai")
        self.assertGreaterEqual(len(openai), 10)

    def test_gemini_plugins(self):
        gemini = get_by_provider("gemini")
        self.assertGreaterEqual(len(gemini), 5)

    def test_meta_plugins(self):
        meta = get_by_provider("meta")
        self.assertGreaterEqual(len(meta), 5)

    def test_google_plugins(self):
        google = get_by_provider("google")
        self.assertGreaterEqual(len(google), 10)

    def test_tiktok_plugins(self):
        tiktok = get_by_provider("tiktok")
        self.assertGreaterEqual(len(tiktok), 10)

    def test_microsoft_plugins(self):
        ms = get_by_provider("microsoft")
        self.assertGreaterEqual(len(ms), 5)

    def test_notion_plugins(self):
        notion = get_by_provider("notion")
        self.assertGreaterEqual(len(notion), 2)


class TestApprovalRequired(unittest.TestCase):
    def test_publishing_plugins_need_approval(self):
        publish = [p for p in ALL_PLUGINS if "auto_publish" in p["tools"]
                   or "publish" in p["tools"]]
        for p in publish:
            if p["risk"] in ("R4", "R5"):
                self.assertTrue(p["approval_required"],
                                f"{p['name']} publish R4+ must need approval")

    def test_email_send_needs_approval(self):
        email = [p for p in ALL_PLUGINS if "email_send" in p["tools"]]
        for p in email:
            self.assertTrue(p["approval_required"],
                            f"{p['name']} email send must need approval")

    def test_ads_budget_needs_approval(self):
        ads = [p for p in ALL_PLUGINS
               if any(t in p["tools"] for t in ["gmv_campaign", "ad_create", "budget"])]
        for p in ads:
            self.assertTrue(p["approval_required"],
                            f"{p['name']} ads/budget must need approval")

    def test_total_approval_count(self):
        approved = get_approval_required()
        self.assertGreater(len(approved), 30, "Too few plugins need approval")


class TestSearch(unittest.TestCase):
    def test_search_tiktok(self):
        results = search_plugins("tiktok")
        self.assertGreater(len(results), 20)

    def test_search_shopify(self):
        results = search_plugins("shopify")
        self.assertGreater(len(results), 0)

    def test_search_claude(self):
        results = search_plugins("claude")
        self.assertGreater(len(results), 3)

    def test_search_notion(self):
        results = search_plugins("notion")
        self.assertGreater(len(results), 0)

    def test_search_empty(self):
        results = search_plugins("xyznonexistent999")
        self.assertEqual(len(results), 0)


class TestNoSecrets(unittest.TestCase):
    def test_no_api_keys_in_plugins(self):
        import json
        dump = json.dumps(ALL_PLUGINS)
        for pattern in ["sk-proj-", "AIzaSy", "token=abc", "password=", "secret_key="]:
            self.assertNotIn(pattern, dump, f"Found secret pattern: {pattern}")


class TestCategoryMapping(unittest.TestCase):
    def test_all_plugins_in_categories(self):
        cat_total = sum(len(v) for v in CATEGORIES.values())
        self.assertEqual(cat_total, get_total_count())

    def test_category_keys_valid(self):
        expected = {"ai_dev", "content", "ecommerce", "documents",
                    "data", "control", "tiktok", "security"}
        self.assertEqual(set(CATEGORIES.keys()), expected)


if __name__ == "__main__":
    unittest.main()
