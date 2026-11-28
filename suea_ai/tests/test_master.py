"""Tests — SUEA_AI_MASTER: Lockdown, Plugin Registry 10K, Security, Recovery, Failover"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from suea_ai.master_config import (
    get_master_config, is_lockdown, is_action_allowed, validate_config,
)
from suea_ai.security.security_guardian import SecurityGuardian, BLOCKED_ACTIONS
from suea_ai.security.emergency_lockdown import EmergencyLockdown
from suea_ai.security.permissions import check_permission, list_roles, OWNER_ONLY_ACTIONS
from suea_ai.core.plugin_registry import PluginRegistry
from suea_ai.core.plugin_discovery import (
    discover_for_task, discover_free_only, search_catalog,
    get_all_task_types, get_catalog_stats, PLUGIN_CATALOG,
)
from suea_ai.core.connection_pool import ConnectionPool
from suea_ai.core.quota_guard import QuotaGuard
from suea_ai.core.retry_manager import RetryManager
from suea_ai.core.failover_manager import CircuitBreaker, FailoverManager
from suea_ai.automation.ack_validator import ACKValidator
from suea_ai.automation.checkpoint_manager import CheckpointManager
from suea_ai.automation.watchdog import Watchdog
from suea_ai.automation.recovery_worker import RecoveryWorker
from suea_ai.connectors.meta_ai_connector import MetaAIConnector
from suea_ai.connectors.base_connector import get_all_connector_status
from suea_ai.analyzers.product_ranking import compute_score, rank_products
from suea_ai.analyzers.video_performance import engagement_rate, analyze_videos
from suea_ai.analyzers.ads_profit import compute_roas, compute_cpc, analyze_ads


class TestMasterConfig(unittest.TestCase):
    def test_lockdown_mode(self):
        self.assertTrue(is_lockdown())

    def test_config_valid(self):
        result = validate_config()
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_blocked_actions(self):
        self.assertFalse(is_action_allowed("spend"))
        self.assertFalse(is_action_allowed("billing"))
        self.assertFalse(is_action_allowed("publish"))
        self.assertFalse(is_action_allowed("ad_create"))

    def test_allowed_actions(self):
        self.assertTrue(is_action_allowed("read"))
        self.assertTrue(is_action_allowed("report"))
        self.assertTrue(is_action_allowed("backup"))

    def test_config_fields(self):
        cfg = get_master_config()
        self.assertTrue(cfg["owner_control"])
        self.assertFalse(cfg["billing_enabled"])
        self.assertFalse(cfg["auto_spending_allowed"])
        self.assertEqual(cfg["plugin_capacity_target"], 10000)
        self.assertFalse(cfg["meta_ai_adapter_enabled"])


class TestSecurityGuardian(unittest.TestCase):
    def setUp(self):
        self.guard = SecurityGuardian()

    def test_lockdown_active(self):
        self.assertTrue(self.guard.is_lockdown)

    def test_blocked_action(self):
        result = self.guard.check_action("PUBLISH")
        self.assertFalse(result["allowed"])
        self.assertEqual(result["risk"], "R4")

    def test_allowed_action(self):
        result = self.guard.check_action("read_data")
        self.assertTrue(result["allowed"])

    def test_emergency_lockdown(self):
        result = self.guard.emergency_lockdown("test")
        self.assertEqual(result["event"], "EMERGENCY_LOCKDOWN")

    def test_release_requires_owner(self):
        result = self.guard.release_lockdown("wrong_token")
        self.assertFalse(result["released"])

    def test_permission_read_allowed(self):
        result = self.guard.check_permission("viewer", "data", "READ")
        self.assertTrue(result["allowed"])

    def test_permission_write_blocked_lockdown(self):
        result = self.guard.check_permission("admin", "data", "WRITE")
        self.assertFalse(result["allowed"])

    def test_risk_classification(self):
        self.assertEqual(self.guard.classify_risk("BILLING_ENABLE"), "R5")
        self.assertEqual(self.guard.classify_risk("PUBLISH"), "R4")
        self.assertEqual(self.guard.classify_risk("BACKUP"), "R2")
        self.assertEqual(self.guard.classify_risk("read"), "R1")

    def test_audit_log(self):
        self.guard.check_action("TEST")
        log = self.guard.get_audit_log()
        self.assertGreater(len(log), 0)


class TestEmergencyLockdown(unittest.TestCase):
    def setUp(self):
        self.lockdown = EmergencyLockdown()

    def test_active_by_default(self):
        self.assertTrue(self.lockdown.active)

    def test_deny_during_lockdown(self):
        result = self.lockdown.can_execute("deploy")
        self.assertFalse(result["allowed"])

    def test_deactivate_requires_owner(self):
        result = self.lockdown.deactivate("wrong")
        self.assertFalse(result["deactivated"])

    def test_deactivate_with_owner(self):
        result = self.lockdown.deactivate("OWNER_CONFIRMED")
        self.assertEqual(result["action"], "LOCKDOWN_DEACTIVATED")
        self.assertFalse(self.lockdown.active)

    def test_block_module(self):
        self.lockdown.block_module("external_api", "unsafe")
        self.assertTrue(self.lockdown.is_module_blocked("external_api"))

    def test_status(self):
        status = self.lockdown.get_status()
        self.assertTrue(status["active"])


class TestPermissions(unittest.TestCase):
    def test_owner_has_all(self):
        result = check_permission("owner", "approve")
        self.assertTrue(result["allowed"])

    def test_viewer_read_only(self):
        result = check_permission("viewer", "read")
        self.assertTrue(result["allowed"])
        result2 = check_permission("viewer", "write")
        self.assertFalse(result2["allowed"])

    def test_plugin_limited(self):
        result = check_permission("plugin", "execute_limited")
        self.assertTrue(result["allowed"])
        result2 = check_permission("plugin", "admin")
        self.assertFalse(result2["allowed"])

    def test_owner_only_actions(self):
        for action in OWNER_ONLY_ACTIONS:
            r = check_permission("viewer", action)
            self.assertFalse(r["allowed"])

    def test_list_roles(self):
        roles = list_roles()
        self.assertIn("owner", roles)
        self.assertIn("viewer", roles)
        self.assertIn("ai_agent", roles)


class TestPluginRegistry(unittest.TestCase):
    def test_register_and_get(self):
        reg = PluginRegistry(capacity=100)
        result = reg.register("test_1", "Test Plugin")
        self.assertTrue(result["ok"])
        entry = reg.get("test_1")
        self.assertEqual(entry["name"], "Test Plugin")

    def test_duplicate_rejected(self):
        reg = PluginRegistry(capacity=100)
        reg.register("dup_1", "First")
        result = reg.register("dup_1", "Second")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "duplicate")

    def test_capacity_limit(self):
        reg = PluginRegistry(capacity=3)
        reg.register("a", "A")
        reg.register("b", "B")
        reg.register("c", "C")
        result = reg.register("d", "D")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "capacity_exceeded")

    def test_capacity_10000(self):
        reg = PluginRegistry(capacity=10000)
        self.assertEqual(reg.capacity, 10000)

    def test_bulk_register(self):
        reg = PluginRegistry(capacity=1000)
        plugins = [{"plugin_id": f"bulk_{i}", "name": f"Bulk {i}"} for i in range(100)]
        result = reg.bulk_register(plugins)
        self.assertEqual(result["registered"], 100)
        self.assertEqual(reg.count, 100)

    def test_search(self):
        reg = PluginRegistry()
        reg.register("windsor_analytics", "Windsor Analytics", category="analytics")
        reg.register("tiktok_ads", "TikTok Ads", category="ads")
        results = reg.search("windsor")
        self.assertEqual(len(results), 1)

    def test_unregister(self):
        reg = PluginRegistry()
        reg.register("temp", "Temp")
        result = reg.unregister("temp")
        self.assertTrue(result["ok"])
        self.assertIsNone(reg.get("temp"))

    def test_stats(self):
        reg = PluginRegistry(capacity=100)
        reg.register("s1", "S1", category="analytics")
        reg.register("s2", "S2", category="ai")
        stats = reg.stats()
        self.assertEqual(stats["total"], 2)
        self.assertIn("analytics", stats["by_category"])

    def test_set_status(self):
        reg = PluginRegistry()
        reg.register("st", "Status Test")
        result = reg.set_status("st", "ACTIVE")
        self.assertTrue(result["ok"])
        self.assertEqual(reg.get("st")["status"], "ACTIVE")


class TestPluginDiscovery(unittest.TestCase):
    def test_discover_text_generation(self):
        results = discover_for_task("text_generation")
        self.assertGreater(len(results), 0)
        ids = [r["plugin_id"] for r in results]
        self.assertIn("claude", ids)

    def test_discover_free_only(self):
        results = discover_free_only()
        for r in results:
            self.assertTrue(r["free_tier"])

    def test_search_catalog(self):
        results = search_catalog("tiktok")
        self.assertGreater(len(results), 0)

    def test_all_task_types(self):
        types = get_all_task_types()
        self.assertIn("analytics", types)
        self.assertIn("text_generation", types)

    def test_catalog_stats(self):
        stats = get_catalog_stats()
        self.assertGreater(stats["total"], 30)
        self.assertGreater(stats["free_tier"], 0)

    def test_catalog_has_key_plugins(self):
        self.assertIn("claude", PLUGIN_CATALOG)
        self.assertIn("windsor", PLUGIN_CATALOG)
        self.assertIn("metricool", PLUGIN_CATALOG)
        self.assertIn("notion", PLUGIN_CATALOG)
        self.assertIn("tiktok_ads", PLUGIN_CATALOG)


class TestConnectionPool(unittest.TestCase):
    def test_acquire_and_release(self):
        pool = ConnectionPool(max_connections=5)
        result = pool.acquire("windsor", "analytics")
        self.assertTrue(result["ok"])
        self.assertEqual(pool.active_count, 1)
        pool.release("windsor")
        self.assertEqual(pool.active_count, 0)

    def test_pool_exhausted(self):
        pool = ConnectionPool(max_connections=2)
        pool.acquire("a")
        pool.acquire("b")
        result = pool.acquire("c")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "pool_exhausted")

    def test_reuse_existing(self):
        pool = ConnectionPool()
        pool.acquire("windsor")
        result = pool.acquire("windsor")
        self.assertTrue(result["ok"])
        self.assertTrue(result["reused"])

    def test_release_all(self):
        pool = ConnectionPool()
        pool.acquire("a")
        pool.acquire("b")
        result = pool.release_all()
        self.assertEqual(result["released"], 2)


class TestQuotaGuard(unittest.TestCase):
    def test_no_quota_allows(self):
        guard = QuotaGuard()
        result = guard.check("unknown")
        self.assertTrue(result["allowed"])

    def test_quota_exceeded(self):
        guard = QuotaGuard()
        guard.set_quota("test", daily_limit=2)
        guard.consume("test")
        guard.consume("test")
        result = guard.check("test")
        self.assertFalse(result["allowed"])

    def test_consume_within_limit(self):
        guard = QuotaGuard()
        guard.set_quota("test", daily_limit=10)
        result = guard.consume("test")
        self.assertTrue(result["ok"])

    def test_reset(self):
        guard = QuotaGuard()
        guard.set_quota("test", daily_limit=5)
        guard.consume("test", 5)
        guard.reset("test")
        result = guard.check("test")
        self.assertTrue(result["allowed"])


class TestRetryManager(unittest.TestCase):
    def test_should_retry(self):
        rm = RetryManager(max_retries=3)
        result = rm.should_retry(0)
        self.assertTrue(result["retry"])
        self.assertEqual(result["attempt"], 1)

    def test_max_retries_exceeded(self):
        rm = RetryManager(max_retries=3)
        result = rm.should_retry(3)
        self.assertFalse(result["retry"])

    def test_non_retryable_error(self):
        rm = RetryManager()
        result = rm.should_retry(0, error_type="auth_failed")
        self.assertFalse(result["retry"])

    def test_backoff_increases(self):
        rm = RetryManager(backoff_base=2)
        self.assertEqual(rm.compute_delay(0), 1.0)
        self.assertEqual(rm.compute_delay(1), 2.0)
        self.assertEqual(rm.compute_delay(2), 4.0)


class TestCircuitBreaker(unittest.TestCase):
    def test_starts_closed(self):
        cb = CircuitBreaker()
        self.assertEqual(cb.get_state("test"), "CLOSED")

    def test_opens_on_threshold(self):
        cb = CircuitBreaker(threshold=3)
        cb.record_failure("bad")
        cb.record_failure("bad")
        result = cb.record_failure("bad")
        self.assertEqual(result["state"], "OPEN")

    def test_success_resets(self):
        cb = CircuitBreaker(threshold=3)
        cb.record_failure("test")
        cb.record_failure("test")
        cb.record_success("test")
        self.assertEqual(cb.get_state("test"), "CLOSED")

    def test_half_open(self):
        cb = CircuitBreaker(threshold=1)
        cb.record_failure("test")
        result = cb.try_half_open("test")
        self.assertEqual(result["state"], "HALF_OPEN")


class TestFailoverManager(unittest.TestCase):
    def test_preferred_available(self):
        fm = FailoverManager()
        result = fm.select_provider("claude")
        self.assertEqual(result["provider_id"], "claude")
        self.assertFalse(result["is_fallback"])

    def test_failover_to_backup(self):
        cb = CircuitBreaker(threshold=1)
        cb.record_failure("claude")
        fm = FailoverManager(circuit_breaker=cb)
        fm.set_fallbacks("claude", ["openai", "gemini"])
        result = fm.select_provider("claude")
        self.assertEqual(result["provider_id"], "openai")
        self.assertTrue(result["is_fallback"])

    def test_no_provider_available(self):
        cb = CircuitBreaker(threshold=1)
        cb.record_failure("claude")
        cb.record_failure("openai")
        fm = FailoverManager(circuit_breaker=cb)
        fm.set_fallbacks("claude", ["openai"])
        result = fm.select_provider("claude")
        self.assertIsNone(result["provider_id"])


class TestACKValidator(unittest.TestCase):
    def test_send_and_ack(self):
        v = ACKValidator()
        v.send_command("cmd_1", "Claude", "analyze")
        result = v.receive_ack("cmd_1", "Claude", "done")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "ACK")

    def test_ack_without_evidence(self):
        v = ACKValidator()
        v.send_command("cmd_2", "GrokBot", "report")
        result = v.receive_ack("cmd_2", "GrokBot", "")
        self.assertEqual(result["status"], "ACK_NO_EVIDENCE")

    def test_auto_ack(self):
        v = ACKValidator()
        v.send_command("cmd_3", "Windsor", "sync")
        result = v.auto_ack("cmd_3")
        self.assertTrue(result["ok"])

    def test_unknown_command(self):
        v = ACKValidator()
        result = v.receive_ack("unknown", "X")
        self.assertFalse(result["ok"])

    def test_stats(self):
        v = ACKValidator()
        v.send_command("s1", "A", "test")
        v.receive_ack("s1", "A", "evidence")
        stats = v.stats()
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["acked"], 1)


class TestCheckpointManager(unittest.TestCase):
    def test_create_and_list(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        cm = CheckpointManager(checkpoint_dir=d)
        result = cm.create_checkpoint({"test": True}, "test_cp")
        self.assertIn("size_kb", result)
        cps = cm.list_checkpoints()
        self.assertEqual(len(cps), 1)

    def test_load_checkpoint(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        cm = CheckpointManager(checkpoint_dir=d)
        cm.create_checkpoint({"data": 42}, "load_test")
        cps = cm.list_checkpoints()
        loaded = cm.load_checkpoint(cps[0]["file"])
        self.assertEqual(loaded["state"]["data"], 42)


class TestWatchdog(unittest.TestCase):
    def test_heartbeat(self):
        wd = Watchdog()
        result = wd.heartbeat("kpi_engine")
        self.assertEqual(result["module"], "kpi_engine")

    def test_check_healthy(self):
        wd = Watchdog(heartbeat_interval=9999)
        wd.heartbeat("mod_a")
        status = wd.check_all()
        self.assertIn("mod_a", status["healthy"])

    def test_registered_modules(self):
        wd = Watchdog()
        wd.heartbeat("a")
        wd.heartbeat("b")
        self.assertEqual(wd.registered_modules(), ["a", "b"])


class TestRecoveryWorker(unittest.TestCase):
    def test_start_recovery(self):
        rw = RecoveryWorker()
        result = rw.start_recovery("tiktok", "timeout")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "IN_PROGRESS")

    def test_complete_recovery_success(self):
        rw = RecoveryWorker()
        rw.start_recovery("tiktok", "timeout")
        result = rw.complete_recovery("tiktok", success=True)
        self.assertEqual(result["status"], "RECOVERED")

    def test_complete_recovery_fail(self):
        rw = RecoveryWorker()
        rw.start_recovery("tiktok", "timeout")
        result = rw.complete_recovery("tiktok", success=False)
        self.assertEqual(result["status"], "FAILED")

    def test_max_retries(self):
        rw = RecoveryWorker(max_retries=2)
        rw.start_recovery("mod", "err")
        rw.retry("mod")
        result = rw.retry("mod")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "max_retries_exceeded")

    def test_stats(self):
        rw = RecoveryWorker()
        rw.start_recovery("a", "err")
        rw.complete_recovery("a", True)
        stats = rw.stats()
        self.assertEqual(stats["recovered"], 1)


class TestMetaAIConnector(unittest.TestCase):
    def test_disabled_by_default(self):
        c = MetaAIConnector()
        self.assertFalse(c.enabled)

    def test_health_check(self):
        c = MetaAIConnector()
        result = c.health_check()
        self.assertEqual(result["status"], "DISABLED")

    def test_enable_requires_owner(self):
        c = MetaAIConnector()
        result = c.enable(owner_confirmed=False)
        self.assertFalse(result["ok"])

    def test_execute_while_disabled(self):
        c = MetaAIConnector()
        result = c.execute("test prompt")
        self.assertFalse(result["ok"])


class TestBaseConnectors(unittest.TestCase):
    def test_all_connectors_return_status(self):
        statuses = get_all_connector_status()
        self.assertGreater(len(statuses), 0)
        for s in statuses:
            self.assertIn("connector", s)
            self.assertIn("status", s)


class TestProductRanking(unittest.TestCase):
    def test_compute_score(self):
        score = compute_score(gmv=1000, orders=50, conversion=5.0, commission=10.0)
        self.assertGreater(score, 0)

    def test_rank_products(self):
        products = [
            {"name": "A", "gmv": 500, "orders": 10, "conversion_rate": 2, "commission_rate": 5},
            {"name": "B", "gmv": 2000, "orders": 50, "conversion_rate": 8, "commission_rate": 15},
        ]
        ranked = rank_products(products, top=2)
        self.assertEqual(ranked[0]["name"], "B")


class TestVideoPerformance(unittest.TestCase):
    def test_engagement_rate(self):
        rate = engagement_rate(1000, 50, 10, 5)
        self.assertEqual(rate, 6.5)

    def test_engagement_rate_zero_views(self):
        rate = engagement_rate(0, 0, 0, 0)
        self.assertEqual(rate, 0.0)

    def test_analyze_videos(self):
        videos = [
            {"title": "V1", "views": 1000, "likes": 50, "comments": 10, "shares": 5},
            {"title": "V2", "views": 5000, "likes": 200, "comments": 30, "shares": 20},
        ]
        result = analyze_videos(videos)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["top_video"], "V2")


class TestAdsProfit(unittest.TestCase):
    def test_roas(self):
        self.assertEqual(compute_roas(500, 100), 5.0)
        self.assertEqual(compute_roas(0, 0), 0.0)

    def test_cpc(self):
        self.assertEqual(compute_cpc(100, 50), 2.0)

    def test_analyze_ads(self):
        ads = [
            {"spend": 100, "revenue": 500, "clicks": 50, "conversions": 10},
            {"spend": 200, "revenue": 800, "clicks": 80, "conversions": 20},
        ]
        result = analyze_ads(ads)
        self.assertEqual(result["profit"], 1000.0)
        self.assertGreater(result["roas"], 0)


if __name__ == "__main__":
    unittest.main()
