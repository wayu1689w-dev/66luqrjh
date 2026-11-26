"""Tests for Plugin Catalog — 1000+ plugins, 12 categories, all DISABLED"""
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
    GOOGLE_AI_STUDIO,
    META_AI,
    CLAUDE_EXTENDED,
    CANVA_EXTENDED,
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
    def test_total_at_least_1000(self):
        self.assertGreaterEqual(get_total_count(), 1000)

    def test_twelve_categories(self):
        self.assertEqual(len(CATEGORIES), 12)

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

    def test_google_ai_studio_at_least_150(self):
        self.assertGreaterEqual(len(GOOGLE_AI_STUDIO), 150)

    def test_meta_ai_at_least_150(self):
        self.assertGreaterEqual(len(META_AI), 150)

    def test_claude_extended_at_least_150(self):
        self.assertGreaterEqual(len(CLAUDE_EXTENDED), 150)

    def test_canva_extended_at_least_50(self):
        self.assertGreaterEqual(len(CANVA_EXTENDED), 50)


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
               if any(t in p["tools"] for t in ["gmv_campaign", "ad_create", "budget_optimize"])]
        for p in ads:
            self.assertTrue(p["approval_required"],
                            f"{p['name']} ads/budget must need approval")

    def test_total_approval_count(self):
        approved = get_approval_required()
        self.assertGreater(len(approved), 30, "Too few plugins need approval")


class TestExtendedProviderCoverage(unittest.TestCase):
    def test_google_ai_studio_provider(self):
        results = get_by_provider("google_ai_studio")
        self.assertGreaterEqual(len(results), 150)

    def test_meta_ai_provider(self):
        results = get_by_provider("meta_ai")
        self.assertGreaterEqual(len(results), 150)

    def test_anthropic_provider(self):
        results = get_by_provider("anthropic")
        self.assertGreaterEqual(len(results), 150)

    def test_canva_provider(self):
        results = get_by_provider("canva")
        self.assertGreaterEqual(len(results), 50)

    def test_extended_all_disabled(self):
        from plugin_os.plugin_catalog_extended import EXTENDED_PLUGINS
        for p in EXTENDED_PLUGINS:
            self.assertFalse(p["connected"])
            self.assertFalse(p["authorized"])
            self.assertEqual(p["state"], "DISCOVERED")

    def test_extended_r5_requires_approval(self):
        from plugin_os.plugin_catalog_extended import EXTENDED_PLUGINS
        r5 = [p for p in EXTENDED_PLUGINS if p["risk"] == "R5"]
        self.assertGreater(len(r5), 0)
        for p in r5:
            self.assertTrue(p["approval_required"],
                            f"R5 extended plugin {p['name']} must require approval")

    def test_extended_unique_ids(self):
        from plugin_os.plugin_catalog_extended import EXTENDED_PLUGINS
        ids = [p["id"] for p in EXTENDED_PLUGINS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_id_collision_with_base(self):
        from plugin_os.plugin_catalog_extended import EXTENDED_PLUGINS
        base_ids = set()
        for cat_key in ["ai_dev", "content", "ecommerce", "documents",
                        "data", "control", "tiktok", "security"]:
            for p in CATEGORIES[cat_key]:
                base_ids.add(p["id"])
        ext_ids = {p["id"] for p in EXTENDED_PLUGINS}
        collision = base_ids & ext_ids
        self.assertEqual(len(collision), 0, f"ID collision: {collision}")

    def test_search_gemini(self):
        results = search_plugins("gemini")
        self.assertGreater(len(results), 10)

    def test_search_llama(self):
        results = search_plugins("llama")
        self.assertGreater(len(results), 5)

    def test_search_canva(self):
        results = search_plugins("canva")
        self.assertGreater(len(results), 20)

    def test_meta_ads_r5(self):
        from plugin_os.plugin_catalog_extended import META_AI
        ads = [p for p in META_AI if "ad_gen" in p["tools"] or "ad_variation" in p["tools"]]
        for p in ads:
            self.assertIn(p["risk"], ("R4", "R5"))


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
                    "data", "control", "tiktok", "security",
                    "ai_studio", "meta_ai", "claude_ext", "canva_ext"}
        self.assertEqual(set(CATEGORIES.keys()), expected)


if __name__ == "__main__":
    unittest.main()
