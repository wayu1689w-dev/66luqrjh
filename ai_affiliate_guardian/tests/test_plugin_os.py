"""Tests — Plugin OS + TikTok Gateway + Risk + Permission + Evidence 100+ tests"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ═══════════════════════════════════════════════════════════
# 1. Plugin State Machine (10 tests)
# ═══════════════════════════════════════════════════════════
class TestPluginStateMachine(unittest.TestCase):
    def test_discovered_to_verified(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, can_transition
        self.assertTrue(can_transition(PluginState.DISCOVERED, PluginState.DOCUMENTATION_VERIFIED))

    def test_discovered_cannot_skip_to_ready(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, can_transition
        self.assertFalse(can_transition(PluginState.DISCOVERED, PluginState.READY))

    def test_registered_to_auth_required(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, can_transition
        self.assertTrue(can_transition(PluginState.REGISTERED, PluginState.AUTH_REQUIRED))

    def test_authorized_to_connecting(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, can_transition
        self.assertTrue(can_transition(PluginState.AUTHORIZED, PluginState.CONNECTING))

    def test_connected_to_health_check(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, can_transition
        self.assertTrue(can_transition(PluginState.CONNECTED, PluginState.HEALTH_CHECK))

    def test_ready_to_production(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, can_transition
        self.assertTrue(can_transition(PluginState.READY, PluginState.PRODUCTION_READY))

    def test_production_can_degrade(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, can_transition
        self.assertTrue(can_transition(PluginState.PRODUCTION_READY, PluginState.DEGRADED))

    def test_failed_can_retry(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, can_transition
        self.assertTrue(can_transition(PluginState.FAILED, PluginState.CONNECTING))

    def test_quarantined_can_only_disable(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, can_transition
        self.assertTrue(can_transition(PluginState.QUARANTINED, PluginState.DISABLED))
        self.assertFalse(can_transition(PluginState.QUARANTINED, PluginState.READY))

    def test_transition_raises_on_invalid(self):
        from ai_affiliate_guardian.plugin_os.plugin_state_machine import PluginState, transition
        with self.assertRaises(ValueError):
            transition(PluginState.DISCOVERED, PluginState.PRODUCTION_READY)


# ═══════════════════════════════════════════════════════════
# 2. Tool Classification (15 tests)
# ═══════════════════════════════════════════════════════════
class TestToolClassification(unittest.TestCase):
    def test_classify_search(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import classify_tool, ToolClass
        self.assertEqual(classify_tool("search"), ToolClass.SEARCH)

    def test_classify_read(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import classify_tool, ToolClass
        self.assertEqual(classify_tool("read"), ToolClass.READ)

    def test_classify_publish(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import classify_tool, ToolClass
        self.assertEqual(classify_tool("publish"), ToolClass.PUBLISH)

    def test_classify_finance(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import classify_tool, ToolClass
        self.assertEqual(classify_tool("finance"), ToolClass.FINANCE)

    def test_classify_ads(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import classify_tool, ToolClass
        self.assertEqual(classify_tool("ads"), ToolClass.ADS)

    def test_classify_admin(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import classify_tool, ToolClass
        self.assertEqual(classify_tool("admin"), ToolClass.ADMIN)

    def test_classify_delete(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import classify_tool, ToolClass
        self.assertEqual(classify_tool("delete"), ToolClass.DELETE)

    def test_classify_commerce(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import classify_tool, ToolClass
        self.assertEqual(classify_tool("commerce"), ToolClass.COMMERCE)

    def test_classify_unknown_defaults_read(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import classify_tool, ToolClass
        self.assertEqual(classify_tool("xyz_unknown"), ToolClass.READ)

    def test_search_no_approval(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass, requires_approval
        ok, _ = requires_approval(ToolClass.SEARCH)
        self.assertFalse(ok)

    def test_read_no_approval(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass, requires_approval
        ok, _ = requires_approval(ToolClass.READ)
        self.assertFalse(ok)

    def test_publish_needs_approval(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass, requires_approval
        ok, _ = requires_approval(ToolClass.PUBLISH)
        self.assertTrue(ok)

    def test_finance_needs_approval(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass, requires_approval
        ok, _ = requires_approval(ToolClass.FINANCE)
        self.assertTrue(ok)

    def test_ads_needs_approval(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass, requires_approval
        ok, _ = requires_approval(ToolClass.ADS)
        self.assertTrue(ok)

    def test_send_needs_approval(self):
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass, requires_approval
        ok, _ = requires_approval(ToolClass.SEND)
        self.assertTrue(ok)


# ═══════════════════════════════════════════════════════════
# 3. Risk Levels (12 tests)
# ═══════════════════════════════════════════════════════════
class TestRiskLevels(unittest.TestCase):
    def test_search_r1(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.SEARCH)["level"], "R1")

    def test_read_r1(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.READ)["level"], "R1")

    def test_analyze_r0(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.ANALYZE)["level"], "R0")

    def test_draft_r2(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.DRAFT)["level"], "R2")

    def test_create_r3(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.CREATE)["level"], "R3")

    def test_publish_r4(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.PUBLISH)["level"], "R4")

    def test_send_r4(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import assess_risk
        from ai_affiliate_guardian.plugin_os.tool_classification import ToolClass
        self.assertEqual(assess_risk(ToolClass.SEND)["level"], "R4")

    def test_finance_r5(self):
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

    def test_r0_is_safe(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import is_safe
        self.assertTrue(is_safe("R0"))

    def test_r5_not_safe(self):
        from ai_affiliate_guardian.plugin_os.risk_levels import is_safe
        self.assertFalse(is_safe("R5"))


# ═══════════════════════════════════════════════════════════
# 4. Permission Guard (10 tests)
# ═══════════════════════════════════════════════════════════
class TestPermissionGuard(unittest.TestCase):
    def test_search_allowed(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import check_permission
        ok, _ = check_permission("search")
        self.assertTrue(ok)

    def test_read_allowed(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import check_permission
        ok, _ = check_permission("read")
        self.assertTrue(ok)

    def test_publish_blocked_without_approval(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import check_permission
        ok, _ = check_permission("publish", has_approval=False)
        self.assertFalse(ok)

    def test_publish_allowed_with_approval(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import check_permission
        ok, _ = check_permission("publish", has_approval=True)
        self.assertTrue(ok)

    def test_finance_blocked_without_approval(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import check_permission
        ok, _ = check_permission("finance", has_approval=False)
        self.assertFalse(ok)

    def test_ads_blocked_without_approval(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import check_permission
        ok, _ = check_permission("ads", has_approval=False)
        self.assertFalse(ok)

    def test_ads_safety_no_evidence(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("budget_change", has_evidence=False)
        self.assertFalse(ok)

    def test_ads_safety_no_policy(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("budget_change", has_evidence=True, has_policy=False)
        self.assertFalse(ok)

    def test_ads_safety_no_human_approval(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("budget_change", has_evidence=True, has_policy=True, has_approval=False)
        self.assertFalse(ok)

    def test_ads_safety_full_approval(self):
        from ai_affiliate_guardian.plugin_os.permission_guard import guard_ads_safety
        ok, _ = guard_ads_safety("budget_change", has_evidence=True, has_policy=True, has_approval=True)
        self.assertTrue(ok)


# ═══════════════════════════════════════════════════════════
# 5. Master Policy (10 tests)
# ═══════════════════════════════════════════════════════════
class TestMasterPolicy(unittest.TestCase):
    def test_external_disabled(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertEqual(get_policy()["EXTERNAL_CONNECTIONS"], "DISABLED")

    def test_plugin_disabled(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertEqual(get_policy()["PLUGIN_CONNECTIONS"], "DISABLED")

    def test_mcp_disabled(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertEqual(get_policy()["MCP_CONNECTIONS"], "DISABLED")

    def test_oauth_disabled(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertEqual(get_policy()["OAUTH_CONNECTIONS"], "DISABLED")

    def test_auto_discover_on(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertTrue(get_policy()["AUTO_DISCOVER"])

    def test_auto_connect_off(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertFalse(get_policy()["AUTO_CONNECT"])

    def test_auto_publish_off(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertFalse(get_policy()["AUTO_PUBLISH"])

    def test_auto_ads_write_off(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertFalse(get_policy()["AUTO_ADS_WRITE"])

    def test_human_approval_on(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertTrue(get_policy()["HUMAN_APPROVAL"])

    def test_audit_required(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_policy
        self.assertTrue(get_policy()["AUDIT_REQUIRED"])


# ═══════════════════════════════════════════════════════════
# 6. Deep Search (8 tests)
# ═══════════════════════════════════════════════════════════
class TestDeepSearch(unittest.TestCase):
    def test_public_always_accessible(self):
        from ai_affiliate_guardian.plugin_os.deep_search import search
        result = search("test", permissions=[])
        self.assertIn("public", result["searched_layers"])

    def test_official_always_accessible(self):
        from ai_affiliate_guardian.plugin_os.deep_search import search
        result = search("test", permissions=[])
        self.assertIn("official", result["searched_layers"])

    def test_stops_at_permission_boundary(self):
        from ai_affiliate_guardian.plugin_os.deep_search import search
        result = search("test", permissions=[])
        self.assertEqual(len(result["searched_layers"]), 2)

    def test_api_access_with_permission(self):
        from ai_affiliate_guardian.plugin_os.deep_search import search
        result = search("test", permissions=["authorized_apis"])
        self.assertIn("authorized_apis", result["searched_layers"])

    def test_mcp_access_with_permission(self):
        from ai_affiliate_guardian.plugin_os.deep_search import search
        result = search("test", permissions=["authorized_apis", "authorized_mcp"])
        self.assertIn("authorized_mcp", result["searched_layers"])

    def test_full_access_with_all_permissions(self):
        from ai_affiliate_guardian.plugin_os.deep_search import search
        result = search("test", permissions=["authorized_apis", "authorized_mcp", "authorized_account_data"])
        self.assertEqual(len(result["searched_layers"]), 5)

    def test_forbidden_bypass(self):
        from ai_affiliate_guardian.plugin_os.deep_search import validate_search_action
        ok, _ = validate_search_action("permission_bypass")
        self.assertFalse(ok)

    def test_forbidden_scraping(self):
        from ai_affiliate_guardian.plugin_os.deep_search import validate_search_action
        ok, _ = validate_search_action("private_data_scraping")
        self.assertFalse(ok)


# ═══════════════════════════════════════════════════════════
# 7. TikTok Gateway Status (12 tests)
# ═══════════════════════════════════════════════════════════
class TestTikTokGateway(unittest.TestCase):
    def test_shop_gateway_documented(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertEqual(get_status()["auth_state"], "DOCUMENTED")

    def test_shop_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        for api in get_status()["apis"].values():
            self.assertFalse(api["connected"])

    def test_shop_10_apis(self):
        from ai_affiliate_guardian.tiktok_gateway.shop import get_status
        self.assertEqual(len(get_status()["apis"]), 10)

    def test_affiliate_gateway(self):
        from ai_affiliate_guardian.tiktok_gateway.affiliate import get_status
        self.assertTrue(get_status()["documented"])
        self.assertFalse(get_status()["connected"])

    def test_webhook_gateway(self):
        from ai_affiliate_guardian.tiktok_gateway.webhook import get_status
        self.assertTrue(get_status()["documented"])
        self.assertFalse(get_status()["connected"])

    def test_social_mcp_gateway(self):
        from ai_affiliate_guardian.tiktok_gateway.social_mcp import get_status
        self.assertTrue(get_status()["documentation"])
        self.assertFalse(get_status()["connection"])

    def test_business_gateway(self):
        from ai_affiliate_guardian.tiktok_gateway.business import get_status
        self.assertTrue(get_status()["documented"])
        self.assertFalse(get_status()["connected"])

    def test_business_mcp_progressive(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["strategy"], "progressive")

    def test_business_mcp_core_40(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["core_tools"], 40)

    def test_business_mcp_full_400(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertEqual(get_status()["full_tools"], 400)

    def test_business_mcp_ads_safety(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        safety = get_status()["safety"]
        self.assertEqual(safety["budget_change"], "REQUIRES_EVIDENCE_POLICY_APPROVAL")

    def test_business_mcp_not_connected(self):
        from ai_affiliate_guardian.tiktok_gateway.business_mcp import get_status
        self.assertFalse(get_status()["connected"])


# ═══════════════════════════════════════════════════════════
# 8. Auth Manager (6 tests)
# ═══════════════════════════════════════════════════════════
class TestAuthManager(unittest.TestCase):
    def test_auth_states_count(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(len(AUTH_STATES), 8)

    def test_documented_first(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[0], "DOCUMENTED")

    def test_production_ready_last(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import AUTH_STATES
        self.assertEqual(AUTH_STATES[-1], "PRODUCTION_READY")

    def test_status_documented(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        status = get_auth_status("PLG-00000001", "DOCUMENTED")
        self.assertEqual(len(status["remaining"]), 7)

    def test_status_authorized(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import get_auth_status
        status = get_auth_status("PLG-00000001", "AUTHORIZED")
        self.assertIn("DOCUMENTED", status["completed"])

    def test_no_secrets_in_code(self):
        from ai_affiliate_guardian.plugin_os.auth_manager import validate_no_secrets_in_code
        result = validate_no_secrets_in_code()
        self.assertEqual(result["method"], "environment variables only")


# ═══════════════════════════════════════════════════════════
# 9. Discovery Engine (5 tests)
# ═══════════════════════════════════════════════════════════
class TestDiscoveryEngine(unittest.TestCase):
    def test_discover_starts_quarantined(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        result = discover_tool("test_tool", "read", "tiktok", "shop")
        self.assertEqual(result["state"], "quarantined")

    def test_discover_has_risk(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        result = discover_tool("test_tool", "finance", "tiktok", "shop")
        self.assertEqual(result["risk_level"], "R5")

    def test_discover_safe_tool(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        result = discover_tool("search_tool", "search", "tiktok", "shop")
        self.assertEqual(result["risk_level"], "R1")

    def test_approve_changes_state(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool, approve_tool
        tool = discover_tool("test", "read", "tiktok", "shop")
        approved = approve_tool(tool)
        self.assertEqual(approved["state"], "enabled")

    def test_discover_no_auto_access(self):
        from ai_affiliate_guardian.plugin_os.discovery_engine import discover_tool
        result = discover_tool("dangerous", "ads", "tiktok", "business_mcp")
        self.assertIn("ห้าม", result["note"])


# ═══════════════════════════════════════════════════════════
# 10. Auto Answer Pipeline (3 tests)
# ═══════════════════════════════════════════════════════════
class TestAutoAnswer(unittest.TestCase):
    def test_pipeline_12_steps(self):
        from ai_affiliate_guardian.plugin_os.auto_answer import AUTO_ANSWER_PIPELINE
        self.assertEqual(len(AUTO_ANSWER_PIPELINE), 12)

    def test_starts_with_question(self):
        from ai_affiliate_guardian.plugin_os.auto_answer import AUTO_ANSWER_PIPELINE
        self.assertEqual(AUTO_ANSWER_PIPELINE[0], "question")

    def test_ends_with_audit(self):
        from ai_affiliate_guardian.plugin_os.auto_answer import AUTO_ANSWER_PIPELINE
        self.assertEqual(AUTO_ANSWER_PIPELINE[-1], "audit")


# ═══════════════════════════════════════════════════════════
# 11. Shop Engines (8 tests)
# ═══════════════════════════════════════════════════════════
class TestShopEngines(unittest.TestCase):
    def test_product_engine(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.product_engine import get_status
        self.assertTrue(get_status()["documented"])
        self.assertFalse(get_status()["connected"])

    def test_order_engine(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.order_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_fulfillment_engine(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.fulfillment_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_return_engine(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.return_refund_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_logistics_engine(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.logistics_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_promotion_engine(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.promotion_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_finance_engine(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.finance_engine import get_status
        self.assertTrue(get_status()["documented"])

    def test_seller_engine(self):
        from ai_affiliate_guardian.tiktok_gateway.shop.seller_engine import get_status
        self.assertTrue(get_status()["documented"])


# ═══════════════════════════════════════════════════════════
# 12. Connection Manager (4 tests)
# ═══════════════════════════════════════════════════════════
class TestConnectionManager(unittest.TestCase):
    def test_request_pending(self):
        from ai_affiliate_guardian.plugin_os.connection_manager import request_connection
        result = request_connection("PLG-1", "shop")
        self.assertEqual(result["state"], "pending_approval")

    def test_verify_success(self):
        from ai_affiliate_guardian.plugin_os.connection_manager import verify_connection
        result = verify_connection("PLG-1", {"status": "ok"})
        self.assertTrue(result["healthy"])

    def test_verify_failure(self):
        from ai_affiliate_guardian.plugin_os.connection_manager import verify_connection
        result = verify_connection("PLG-1", {"status": "error", "error": "timeout"})
        self.assertFalse(result["healthy"])

    def test_connection_needs_approval(self):
        from ai_affiliate_guardian.plugin_os.connection_manager import request_connection
        result = request_connection("PLG-1", "business_mcp")
        self.assertIn("อนุมัติ", result["note"])


# ═══════════════════════════════════════════════════════════
# 13. Checklist Verification (5 tests)
# ═══════════════════════════════════════════════════════════
class TestChecklist(unittest.TestCase):
    def test_all_documented_true(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_checklist
        for v in get_checklist()["documented"].values():
            self.assertTrue(v)

    def test_all_not_done_false(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_checklist
        for v in get_checklist()["not_done"].values():
            self.assertFalse(v)

    def test_9_documented_items(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_checklist
        self.assertEqual(len(get_checklist()["documented"]), 9)

    def test_8_not_done_items(self):
        from ai_affiliate_guardian.plugin_os.master_policy import get_checklist
        self.assertEqual(len(get_checklist()["not_done"]), 8)

    def test_policy_is_allowed_publish(self):
        from ai_affiliate_guardian.plugin_os.master_policy import is_allowed
        ok, _ = is_allowed("publish")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
