"""Tests — TikTok Shop App Key Security + Credential Guard + Auth Flow
ไม่มี API key จริงในโค้ด ทดสอบเฉพาะ logic ป้องกัน"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ═══════════════════════════════════════════════════════════
# 1. Credential Guard — ห้ามฝัง Key ในโค้ด (20 tests)
# ═══════════════════════════════════════════════════════════
class TestCredentialGuard(unittest.TestCase):
    """ตรวจว่าไม่มี key/secret/token ฝังใน source code"""

    DANGEROUS_PATTERNS = [
        "TIKTOK_SHOP_APP_KEY=",
        "TIKTOK_SHOP_APP_SECRET=",
        "TIKTOK_ACCESS_TOKEN=",
        "OPENAI_API_KEY=sk-",
        "ANTHROPIC_API_KEY=sk-ant-",
        "GEMINI_API_KEY=AI",
        "Bearer sk-",
        "Bearer sk-ant-",
        "api_key=\"",
        "app_secret=\"",
    ]

    def _scan_file(self, filepath):
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r", errors="ignore") as f:
            content = f.read()
        found = []
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in content:
                found.append(pattern)
        return found

    def _scan_directory(self, dirpath):
        violations = {}
        for root, _, files in os.walk(dirpath):
            if "__pycache__" in root or ".git" in root:
                continue
            for fname in files:
                if fname.endswith((".py", ".yaml", ".yml", ".json", ".env")):
                    path = os.path.join(root, fname)
                    found = self._scan_file(path)
                    if found:
                        violations[path] = found
        return violations

    def test_no_secrets_in_plugin_os(self):
        d = os.path.join(os.path.dirname(__file__), "..", "plugin_os")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_tiktok_gateway(self):
        d = os.path.join(os.path.dirname(__file__), "..", "tiktok_gateway")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_core(self):
        d = os.path.join(os.path.dirname(__file__), "..", "core")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_config(self):
        d = os.path.join(os.path.dirname(__file__), "..", "config")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_channels(self):
        d = os.path.join(os.path.dirname(__file__), "..", "channels")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_products(self):
        d = os.path.join(os.path.dirname(__file__), "..", "products")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_content(self):
        d = os.path.join(os.path.dirname(__file__), "..", "content")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_media(self):
        d = os.path.join(os.path.dirname(__file__), "..", "media")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_quality(self):
        d = os.path.join(os.path.dirname(__file__), "..", "quality")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_approval(self):
        d = os.path.join(os.path.dirname(__file__), "..", "approval")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_governance(self):
        d = os.path.join(os.path.dirname(__file__), "..", "governance")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_workflows(self):
        d = os.path.join(os.path.dirname(__file__), "..", "workflows")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_publishing(self):
        d = os.path.join(os.path.dirname(__file__), "..", "publishing")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_performance(self):
        d = os.path.join(os.path.dirname(__file__), "..", "performance")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_analytics(self):
        d = os.path.join(os.path.dirname(__file__), "..", "analytics")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_experiments(self):
        d = os.path.join(os.path.dirname(__file__), "..", "experiments")
        self.assertEqual(self._scan_directory(d), {})

    def test_no_secrets_in_dashboard(self):
        d = os.path.join(os.path.dirname(__file__), "..", "dashboard")
        self.assertEqual(self._scan_directory(d), {})

    def test_auth_manager_env_only(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import validate_no_secrets_in_code
        result = validate_no_secrets_in_code()
        self.assertEqual(result["method"], "environment variables only")

    def test_no_hardcoded_key_format(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import validate_no_secrets_in_code
        result = validate_no_secrets_in_code()
        self.assertTrue(result["audit"])

    def test_credential_source_env(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import validate_no_secrets_in_code
        result = validate_no_secrets_in_code()
        self.assertIn("environment", result["method"])


# ═══════════════════════════════════════════════════════════
# 2. TikTok Shop Auth Flow — 8 ขั้นตอน (25 tests)
# ═══════════════════════════════════════════════════════════
class TestTikTokShopAuthFlow(unittest.TestCase):
    """ทดสอบ auth flow ทั้ง 8 ขั้น"""

    def test_auth_states_order(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        expected = [
            "DOCUMENTED", "APP_REGISTERED", "AUTHORIZED",
            "TOKEN_VALIDATED", "SCOPES_VERIFIED", "READ_TESTED",
            "WRITE_TESTED", "PRODUCTION_READY",
        ]
        self.assertEqual(AUTH_STATES, expected)

    def test_documented_is_first_step(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[0], "DOCUMENTED")

    def test_app_registered_is_second(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[1], "APP_REGISTERED")

    def test_authorized_is_third(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[2], "AUTHORIZED")

    def test_token_validated_is_fourth(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[3], "TOKEN_VALIDATED")

    def test_scopes_verified_is_fifth(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[4], "SCOPES_VERIFIED")

    def test_read_tested_is_sixth(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[5], "READ_TESTED")

    def test_write_tested_is_seventh(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[6], "WRITE_TESTED")

    def test_production_ready_is_last(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[7], "PRODUCTION_READY")

    def test_status_at_documented(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "DOCUMENTED")
        self.assertEqual(s["current"], "DOCUMENTED")
        self.assertEqual(len(s["remaining"]), 7)

    def test_status_at_app_registered(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "APP_REGISTERED")
        self.assertIn("DOCUMENTED", s["completed"])
        self.assertEqual(len(s["remaining"]), 6)

    def test_status_at_authorized(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "AUTHORIZED")
        self.assertIn("APP_REGISTERED", s["completed"])
        self.assertEqual(len(s["remaining"]), 5)

    def test_status_at_token_validated(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "TOKEN_VALIDATED")
        self.assertEqual(len(s["remaining"]), 4)

    def test_status_at_scopes_verified(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "SCOPES_VERIFIED")
        self.assertEqual(len(s["remaining"]), 3)

    def test_status_at_read_tested(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "READ_TESTED")
        self.assertEqual(len(s["remaining"]), 2)

    def test_status_at_write_tested(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "WRITE_TESTED")
        self.assertEqual(len(s["remaining"]), 1)

    def test_status_at_production_ready(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "PRODUCTION_READY")
        self.assertEqual(len(s["remaining"]), 0)

    def test_cannot_skip_steps(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "DOCUMENTED")
        self.assertNotIn("TOKEN_VALIDATED", s["completed"])

    def test_completed_accumulates(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "SCOPES_VERIFIED")
        self.assertEqual(len(s["completed"]), 5)

    def test_progress_percentage_start(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "DOCUMENTED")
        pct = len(s["completed"]) / 8 * 100
        self.assertAlmostEqual(pct, 12.5)

    def test_progress_percentage_mid(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "TOKEN_VALIDATED")
        pct = len(s["completed"]) / 8 * 100
        self.assertAlmostEqual(pct, 50.0)

    def test_progress_percentage_end(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-SHOP", "PRODUCTION_READY")
        pct = len(s["completed"]) / 8 * 100
        self.assertAlmostEqual(pct, 100.0)

    def test_plugin_id_preserved(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        s = get_auth_status("PLG-00000099", "DOCUMENTED")
        self.assertEqual(s["plugin_id"], "PLG-00000099")

    def test_all_states_reachable(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES, get_auth_status
        for state in AUTH_STATES:
            s = get_auth_status("PLG-TEST", state)
            self.assertEqual(s["current"], state)

    def test_8_total_steps(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(len(AUTH_STATES), 8)


# ═══════════════════════════════════════════════════════════
# 3. TikTok Shop API Scope Guard (20 tests)
# ═══════════════════════════════════════════════════════════
class TestShopAPIScopeGuard(unittest.TestCase):
    """ตรวจ scope ของ Shop API ทั้ง 10 ตัว"""

    def test_product_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("product", get_status()["apis"])

    def test_product_api_not_authorized(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertFalse(get_status()["apis"]["product"]["authorized"])

    def test_product_api_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertFalse(get_status()["apis"]["product"]["connected"])

    def test_order_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("order", get_status()["apis"])

    def test_order_api_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertFalse(get_status()["apis"]["order"]["connected"])

    def test_finance_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("finance", get_status()["apis"])

    def test_finance_api_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertFalse(get_status()["apis"]["finance"]["connected"])

    def test_fulfillment_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("fulfillment", get_status()["apis"])

    def test_logistics_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("logistics", get_status()["apis"])

    def test_promotion_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("promotion", get_status()["apis"])

    def test_seller_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("seller", get_status()["apis"])

    def test_return_refund_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("return_refund", get_status()["apis"])

    def test_authorization_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("authorization", get_status()["apis"])

    def test_events_webhooks_api_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertIn("events_webhooks", get_status()["apis"])

    def test_all_10_apis_present(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertEqual(len(get_status()["apis"]), 10)

    def test_no_api_is_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        for name, api in get_status()["apis"].items():
            self.assertFalse(api["connected"], f"{name} should not be connected")

    def test_no_api_is_authorized(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        for name, api in get_status()["apis"].items():
            self.assertFalse(api["authorized"], f"{name} should not be authorized")

    def test_auth_state_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertEqual(get_status()["auth_state"], "DOCUMENTED")

    def test_auth_flow_8_steps(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import AUTH_FLOW
        self.assertEqual(len(AUTH_FLOW), 8)

    def test_auth_flow_starts_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import AUTH_FLOW
        self.assertEqual(AUTH_FLOW[0], "DOCUMENTED")


# ═══════════════════════════════════════════════════════════
# 4. Shop Engine Detail Tests (16 tests)
# ═══════════════════════════════════════════════════════════
class TestShopEngineDetails(unittest.TestCase):

    def test_product_engine_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.product_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_product_engine_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.product_engine import get_status
        self.assertFalse(get_status()["connected"])

    def test_order_engine_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.order_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_order_engine_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.order_engine import get_status
        self.assertFalse(get_status()["connected"])

    def test_fulfillment_engine_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.fulfillment_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_fulfillment_engine_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.fulfillment_engine import get_status
        self.assertFalse(get_status()["connected"])

    def test_return_refund_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.return_refund_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_return_refund_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.return_refund_engine import get_status
        self.assertFalse(get_status()["connected"])

    def test_logistics_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.logistics_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_logistics_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.logistics_engine import get_status
        self.assertFalse(get_status()["connected"])

    def test_promotion_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.promotion_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_promotion_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.promotion_engine import get_status
        self.assertFalse(get_status()["connected"])

    def test_finance_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.finance_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_finance_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.finance_engine import get_status
        self.assertFalse(get_status()["connected"])

    def test_seller_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.seller_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_seller_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.seller_engine import get_status
        self.assertFalse(get_status()["connected"])


# ═══════════════════════════════════════════════════════════
# 5. Ads Safety Chain (15 tests)
# ═══════════════════════════════════════════════════════════
class TestAdsSafetyChain(unittest.TestCase):
    """AI → Evidence → Policy → Approval → Tool → Validate → Audit
    NEVER: AI → budget change"""

    def test_budget_blocked_no_evidence(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("budget_change", has_evidence=False)
        self.assertFalse(ok)

    def test_budget_blocked_no_policy(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("budget_change", has_evidence=True, has_policy=False)
        self.assertFalse(ok)

    def test_budget_blocked_no_approval(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("budget_change", has_evidence=True, has_policy=True, has_approval=False)
        self.assertFalse(ok)

    def test_budget_allowed_full_chain(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("budget_change", has_evidence=True, has_policy=True, has_approval=True)
        self.assertTrue(ok)

    def test_campaign_create_blocked_no_evidence(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("campaign_create", has_evidence=False)
        self.assertFalse(ok)

    def test_campaign_create_allowed_full(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("campaign_create", has_evidence=True, has_policy=True, has_approval=True)
        self.assertTrue(ok)

    def test_audience_change_blocked(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("audience_change", has_evidence=False)
        self.assertFalse(ok)

    def test_audience_change_allowed(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("audience_change", has_evidence=True, has_policy=True, has_approval=True)
        self.assertTrue(ok)

    def test_ads_read_allowed_no_approval(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import check_permission
        ok, _ = check_permission("read")
        self.assertTrue(ok)

    def test_ads_write_blocked(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import check_permission
        ok, _ = check_permission("ads", has_approval=False)
        self.assertFalse(ok)

    def test_business_mcp_budget_safety(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["safety"]["budget_change"], "REQUIRES_EVIDENCE_POLICY_APPROVAL")

    def test_business_mcp_campaign_safety(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["safety"]["campaign_create"], "REQUIRES_HUMAN_APPROVAL")

    def test_business_mcp_audience_safety(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["safety"]["audience_change"], "REQUIRES_HUMAN_APPROVAL")

    def test_business_mcp_ads_write_safety(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["safety"]["ads_write"], "REQUIRES_HUMAN_APPROVAL")

    def test_master_policy_auto_ads_write_off(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertFalse(get_policy()["AUTO_ADS_WRITE"])


# ═══════════════════════════════════════════════════════════
# 6. Kill Switch Verification (10 tests)
# ═══════════════════════════════════════════════════════════
class TestKillSwitch(unittest.TestCase):
    """ตรวจว่า kill switch ปิดทุก connection"""

    def test_kill_switch_exists(self):
        path = os.path.join(os.path.dirname(__file__), "..", "config", "kill_switch.yaml")
        self.assertTrue(os.path.exists(path))

    def test_master_policy_external_disabled(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertEqual(get_policy()["EXTERNAL_CONNECTIONS"], "DISABLED")

    def test_master_policy_plugin_disabled(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertEqual(get_policy()["PLUGIN_CONNECTIONS"], "DISABLED")

    def test_master_policy_mcp_disabled(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertEqual(get_policy()["MCP_CONNECTIONS"], "DISABLED")

    def test_master_policy_oauth_disabled(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertEqual(get_policy()["OAUTH_CONNECTIONS"], "DISABLED")

    def test_publish_blocked(self):
        from ai_affiliate_guardian.plugin_os.master_policy import is_allowed
        ok, _ = is_allowed("publish")
        self.assertFalse(ok)

    def test_send_blocked(self):
        from ai_affiliate_guardian.plugin_os.master_policy import is_allowed
        ok, _ = is_allowed("send")
        self.assertFalse(ok)

    def test_ads_write_blocked(self):
        from ai_affiliate_guardian.plugin_os.master_policy import is_allowed
        ok, _ = is_allowed("ads")
        self.assertFalse(ok)

    def test_finance_blocked(self):
        from ai_affiliate_guardian.plugin_os.master_policy import is_allowed
        ok, _ = is_allowed("finance")
        self.assertFalse(ok)

    def test_delete_blocked(self):
        from ai_affiliate_guardian.plugin_os.master_policy import is_allowed
        ok, _ = is_allowed("delete")
        self.assertFalse(ok)


# ═══════════════════════════════════════════════════════════
# 7. Gateway Isolation (12 tests)
# ═══════════════════════════════════════════════════════════
class TestGatewayIsolation(unittest.TestCase):
    """แต่ละ gateway แยกกัน ไม่เชื่อมข้ามโดยอัตโนมัติ"""

    def test_shop_gateway_independent(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertEqual(get_status()["gateway"], "tiktok_shop")

    def test_affiliate_gateway_independent(self):
        from ai_affiliate_guardian.tiktok_gateway.affiliate import get_status
        self.assertEqual(get_status()["gateway"], "tiktok_affiliate")

    def test_webhook_gateway_independent(self):
        from ai_affiliate_guardian.tiktok_gateway.webhook import get_status
        self.assertEqual(get_status()["gateway"], "tiktok_webhook")

    def test_social_mcp_gateway_independent(self):
        from ai_affiliate_guardian.tiktok_gateway.social_mcp import get_status
        self.assertEqual(get_status()["gateway"], "tiktok_social_mcp")

    def test_business_gateway_independent(self):
        from ai_affiliate_guardian.tiktok_gateway.business import get_status
        self.assertEqual(get_status()["gateway"], "tiktok_business_api")

    def test_business_mcp_gateway_independent(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["gateway"], "tiktok_business_mcp")

    def test_6_gateways_total(self):
        from ai_affiliate_guardian.tiktok_gateway import GATEWAYS
        self.assertEqual(len(GATEWAYS), 6)

    def test_shop_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertFalse(get_status()["apis"]["product"]["connected"])

    def test_affiliate_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.affiliate import get_status
        self.assertFalse(get_status()["connected"])

    def test_webhook_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.webhook import get_status
        self.assertFalse(get_status()["connected"])

    def test_social_mcp_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.social_mcp import get_status
        self.assertFalse(get_status()["connection"])

    def test_business_mcp_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertFalse(get_status()["connected"])


# ═══════════════════════════════════════════════════════════
# 8. Risk Assessment for TikTok Operations (15 tests)
# ═══════════════════════════════════════════════════════════
class TestTikTokRiskAssessment(unittest.TestCase):

    def test_shop_read_r1(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.READ)["level"], "R1")

    def test_shop_search_r1(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.SEARCH)["level"], "R1")

    def test_shop_analyze_r0(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.ANALYZE)["level"], "R0")

    def test_shop_draft_r2(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.DRAFT)["level"], "R2")

    def test_shop_create_product_r3(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.CREATE)["level"], "R3")

    def test_shop_update_order_r3(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.UPDATE)["level"], "R3")

    def test_shop_publish_r4(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.PUBLISH)["level"], "R4")

    def test_shop_commerce_r5(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.COMMERCE)["level"], "R5")

    def test_shop_finance_r5(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.FINANCE)["level"], "R5")

    def test_ads_r5(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.ADS)["level"], "R5")

    def test_admin_r5(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.ADMIN)["level"], "R5")

    def test_delete_r3(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        r = assess_risk(ToolClass.DELETE)
        self.assertIn(r["level"], ["R3", "R4", "R5"])

    def test_r0_auto_allow(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import RISK_POLICIES
        self.assertIn("auto-allow", RISK_POLICIES["R0"])

    def test_r5_strongest_approval(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import RISK_POLICIES
        self.assertIn("strongest", RISK_POLICIES["R5"])

    def test_r5_finance_ads(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import RISK_POLICIES
        self.assertIn("finance", RISK_POLICIES["R5"])


# ═══════════════════════════════════════════════════════════
# 9. Progressive Disclosure (8 tests)
# ═══════════════════════════════════════════════════════════
class TestProgressiveDisclosure(unittest.TestCase):

    def test_strategy_progressive(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["strategy"], "progressive")

    def test_core_40(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["core_tools"], 40)

    def test_full_400(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["full_tools"], 400)

    def test_core_less_than_full(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        s = get_status()
        self.assertLess(s["core_tools"], s["full_tools"])

    def test_ratio_10_percent(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        s = get_status()
        self.assertEqual(s["core_tools"] / s["full_tools"], 0.1)

    def test_not_authorized(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertFalse(get_status()["authorized"])

    def test_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertFalse(get_status()["connected"])

    def test_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertTrue(get_status()["documented"])


# ═══════════════════════════════════════════════════════════
# 10. Discovery → Quarantine → Approve (10 tests)
# ═══════════════════════════════════════════════════════════
class TestDiscoveryQuarantineApprove(unittest.TestCase):

    def test_discover_shop_tool_quarantined(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        r = discover_tool("get_products", "read", "tiktok", "shop")
        self.assertEqual(r["state"], "quarantined")

    def test_discover_finance_tool_r5(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        r = discover_tool("get_balance", "finance", "tiktok", "shop")
        self.assertEqual(r["risk_level"], "R5")

    def test_discover_ads_tool_r5(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        r = discover_tool("create_campaign", "ads", "tiktok", "business_mcp")
        self.assertEqual(r["risk_level"], "R5")

    def test_discover_search_tool_r1(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        r = discover_tool("search_products", "search", "tiktok", "shop")
        self.assertEqual(r["risk_level"], "R1")

    def test_approve_read_tool(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool, approve_tool
        t = discover_tool("get_orders", "read", "tiktok", "shop")
        a = approve_tool(t)
        self.assertEqual(a["state"], "enabled")

    def test_approve_preserves_name(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool, approve_tool
        t = discover_tool("get_orders", "read", "tiktok", "shop")
        a = approve_tool(t)
        self.assertEqual(a["tool_name"], "get_orders")

    def test_discover_no_auto_access_finance(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        r = discover_tool("withdraw", "finance", "tiktok", "shop")
        self.assertIn("ห้าม", r["note"])

    def test_discover_no_auto_access_ads(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        r = discover_tool("set_budget", "ads", "tiktok", "business_mcp")
        self.assertIn("ห้าม", r["note"])

    def test_discover_has_provider(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        r = discover_tool("get_products", "read", "tiktok", "shop")
        self.assertEqual(r["provider"], "tiktok")

    def test_discover_has_gateway(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        r = discover_tool("get_products", "read", "tiktok", "shop")
        self.assertEqual(r["gateway"], "shop")


if __name__ == "__main__":
    unittest.main()
