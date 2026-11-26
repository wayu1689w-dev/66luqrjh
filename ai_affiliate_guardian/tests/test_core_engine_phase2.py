"""Tests for Core Engine Phase 2 — Capability, QC, Approval, Audit
ครอบคลุม Spec sections 14-15, 32-35, 46"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.capability_registry import (
    register, get, list_by_plugin, list_by_class, list_by_risk,
    disable, enable, is_enabled, ToolClass, TOOL_CLASS_RISK,
    reset as cap_reset,
)
from core.qc_engine import (
    check, check_before_publish, QC_RULES, QCResult,
    reset as qc_reset,
)
from core.approval_engine import (
    request_approval, approve, reject, revoke, get as apr_get,
    list_pending, is_approved, reset as apr_reset,
)
from core.audit_logger import (
    log_action, get_log, count_by_action, count_by_result,
    last_n, reset as audit_reset,
)


class TestCapabilityRegistry(unittest.TestCase):
    def setUp(self):
        cap_reset()

    def test_register_read(self):
        cap = register("PLG-001", "search_products", ToolClass.READ)
        self.assertEqual(cap["risk"], "R1")
        self.assertFalse(cap["requires_approval"])
        self.assertTrue(cap["enabled"])

    def test_register_write(self):
        cap = register("PLG-001", "update_product", ToolClass.WRITE)
        self.assertEqual(cap["risk"], "R3")
        self.assertTrue(cap["requires_approval"])

    def test_register_finance(self):
        cap = register("PLG-001", "set_budget", ToolClass.FINANCE)
        self.assertEqual(cap["risk"], "R5")
        self.assertTrue(cap["requires_approval"])

    def test_register_publish(self):
        cap = register("PLG-001", "publish_post", ToolClass.PUBLISH)
        self.assertEqual(cap["risk"], "R4")
        self.assertTrue(cap["requires_approval"])

    def test_register_analyze_no_approval(self):
        cap = register("PLG-001", "analyze_data", ToolClass.ANALYZE)
        self.assertEqual(cap["risk"], "R0")
        self.assertFalse(cap["requires_approval"])

    def test_list_by_plugin(self):
        register("PLG-001", "read", ToolClass.READ)
        register("PLG-001", "write", ToolClass.WRITE)
        register("PLG-002", "read", ToolClass.READ)
        self.assertEqual(len(list_by_plugin("PLG-001")), 2)
        self.assertEqual(len(list_by_plugin("PLG-002")), 1)

    def test_list_by_class(self):
        register("PLG-001", "read", ToolClass.READ)
        register("PLG-002", "read2", ToolClass.READ)
        register("PLG-003", "write", ToolClass.WRITE)
        self.assertEqual(len(list_by_class(ToolClass.READ)), 2)

    def test_list_by_risk(self):
        register("PLG-001", "admin", ToolClass.ADMIN)
        register("PLG-002", "finance", ToolClass.FINANCE)
        register("PLG-003", "read", ToolClass.READ)
        self.assertEqual(len(list_by_risk("R5")), 2)

    def test_disable_enable(self):
        cap = register("PLG-001", "tool", ToolClass.READ)
        self.assertTrue(is_enabled(cap["cap_id"]))
        disable(cap["cap_id"])
        self.assertFalse(is_enabled(cap["cap_id"]))
        enable(cap["cap_id"])
        self.assertTrue(is_enabled(cap["cap_id"]))

    def test_get(self):
        cap = register("PLG-001", "tool", ToolClass.READ)
        fetched = get(cap["cap_id"])
        self.assertEqual(fetched["tool_name"], "tool")

    def test_unique_ids(self):
        c1 = register("PLG-001", "a", ToolClass.READ)
        c2 = register("PLG-001", "b", ToolClass.READ)
        self.assertNotEqual(c1["cap_id"], c2["cap_id"])

    def test_override_approval(self):
        cap = register("PLG-001", "read", ToolClass.READ, requires_approval=True)
        self.assertTrue(cap["requires_approval"])

    def test_all_tool_classes_have_risk(self):
        for tc in ToolClass:
            self.assertIn(tc, TOOL_CLASS_RISK)


class TestQCEngine(unittest.TestCase):
    def setUp(self):
        qc_reset()

    def test_pass_basic(self):
        content = {"id": "CNT-001", "text": "Great product for cooking everyday meals"}
        result = check(content)
        self.assertTrue(result.passed)
        self.assertEqual(len(result.failures), 0)

    def test_fail_empty_text(self):
        content = {"id": "CNT-002", "text": ""}
        result = check(content)
        self.assertFalse(result.passed)
        self.assertIn("text_not_empty", result.failures)

    def test_fail_too_short(self):
        content = {"id": "CNT-003", "text": "hi"}
        result = check(content)
        self.assertFalse(result.passed)
        self.assertIn("text_min_length", result.failures)

    def test_fail_banned_words(self):
        content = {"id": "CNT-004", "text": "This product is guaranteed to work perfectly"}
        result = check(content)
        self.assertFalse(result.passed)
        self.assertIn("no_banned_words", result.failures)

    def test_banned_thai(self):
        content = {"id": "CNT-005", "text": "สินค้านี้การันตีคุณภาพสูงสุด"}
        result = check(content)
        self.assertFalse(result.passed)

    def test_warnings_no_product_link(self):
        content = {"id": "CNT-006", "text": "Great product for cooking everyday"}
        result = check(content)
        self.assertTrue(result.passed)
        self.assertIn("has_product_link", result.warnings)

    def test_publish_check_needs_link(self):
        content = {"id": "CNT-007", "text": "Great product for cooking everyday"}
        result = check_before_publish(content)
        self.assertFalse(result.passed)
        self.assertIn("has_product_link", result.failures)

    def test_publish_check_pass(self):
        content = {
            "id": "CNT-008",
            "text": "Great product for cooking everyday meals",
            "product_link": "https://shop.tiktok.com/abc",
            "link_status": "OK",
        }
        result = check_before_publish(content)
        self.assertTrue(result.passed)

    def test_broken_link_fails_publish(self):
        content = {
            "id": "CNT-009",
            "text": "Great product for cooking everyday meals",
            "product_link": "https://shop.tiktok.com/xyz",
            "link_status": "BROKEN",
        }
        result = check_before_publish(content)
        self.assertFalse(result.passed)
        self.assertIn("link_not_broken", result.failures)

    def test_qc_result_to_dict(self):
        content = {"id": "CNT-010", "text": "Normal content text here"}
        result = check(content)
        d = result.to_dict()
        self.assertIn("qc_id", d)
        self.assertIn("checked_at", d)

    def test_unique_qc_ids(self):
        c1 = check({"id": "A", "text": "Normal content text"})
        c2 = check({"id": "B", "text": "Normal content text"})
        self.assertNotEqual(c1.qc_id, c2.qc_id)

    def test_custom_rules(self):
        content = {"id": "CNT-011", "text": "Short"}
        result = check(content, rules=["text_not_empty"], warn_rules=[])
        self.assertTrue(result.passed)


class TestApprovalEngine(unittest.TestCase):
    def setUp(self):
        apr_reset()

    def test_request_creates_pending(self):
        apr = request_approval("TASK-001", "PUBLISH", "R4", "USR-000001")
        self.assertEqual(apr["state"], "PENDING")
        self.assertTrue(apr["approval_id"].startswith("APR-"))

    def test_approve(self):
        apr = request_approval("TASK-001", "ADS_WRITE", "R5", "USR-000001")
        result = approve(apr["approval_id"], "ADMIN-001")
        self.assertEqual(result["state"], "APPROVED")
        self.assertEqual(result["decided_by"], "ADMIN-001")

    def test_reject(self):
        apr = request_approval("TASK-001", "DELETE", "R3", "USR-000001")
        result = reject(apr["approval_id"], "ADMIN-001", "Not justified")
        self.assertEqual(result["state"], "REJECTED")
        self.assertEqual(result["reject_reason"], "Not justified")

    def test_revoke_approved(self):
        apr = request_approval("TASK-001", "PUBLISH", "R4", "USR-000001")
        approve(apr["approval_id"], "ADMIN-001")
        result = revoke(apr["approval_id"], "ADMIN-001", "Changed mind")
        self.assertEqual(result["state"], "REVOKED")

    def test_cannot_approve_non_pending(self):
        apr = request_approval("TASK-001", "READ", "R1", "USR-000001")
        reject(apr["approval_id"], "ADMIN-001")
        with self.assertRaises(ValueError):
            approve(apr["approval_id"], "ADMIN-002")

    def test_cannot_revoke_pending(self):
        apr = request_approval("TASK-001", "PUBLISH", "R4", "USR-000001")
        with self.assertRaises(ValueError):
            revoke(apr["approval_id"], "ADMIN-001")

    def test_list_pending(self):
        request_approval("TASK-001", "A", "R3", "USR-000001")
        apr2 = request_approval("TASK-001", "B", "R4", "USR-000001")
        request_approval("TASK-002", "C", "R5", "USR-000001")
        approve(apr2["approval_id"], "ADMIN-001")
        self.assertEqual(len(list_pending()), 2)
        self.assertEqual(len(list_pending("TASK-001")), 1)

    def test_is_approved(self):
        apr = request_approval("TASK-001", "X", "R3", "USR-000001")
        self.assertFalse(is_approved(apr["approval_id"]))
        approve(apr["approval_id"], "ADMIN-001")
        self.assertTrue(is_approved(apr["approval_id"]))

    def test_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            approve("APR-999999", "ADMIN-001")

    def test_evidence_ids_stored(self):
        apr = request_approval("TASK-001", "PUBLISH", "R4", "USR-000001",
                                evidence_ids=["EV-001", "EV-002"])
        self.assertEqual(len(apr["evidence_ids"]), 2)


class TestAuditLogger(unittest.TestCase):
    def setUp(self):
        audit_reset()

    def test_log_action(self):
        entry = log_action("USR-000001", "PUBLISH", "CH-001", "R4", "BLOCKED")
        self.assertTrue(entry["audit_id"].startswith("AUD-"))
        self.assertIn("logged_at", entry)

    def test_get_log_by_actor(self):
        log_action("USR-000001", "READ", "X", "R1", "SUCCESS")
        log_action("USR-000002", "WRITE", "Y", "R3", "SUCCESS")
        self.assertEqual(len(get_log(actor="USR-000001")), 1)

    def test_get_log_by_action(self):
        log_action("USR-000001", "PUBLISH", "X", "R4", "BLOCKED")
        log_action("USR-000001", "READ", "Y", "R1", "SUCCESS")
        log_action("USR-000001", "PUBLISH", "Z", "R4", "SUCCESS")
        self.assertEqual(len(get_log(action_type="PUBLISH")), 2)

    def test_count_by_action(self):
        log_action("U", "READ", "X", "R1", "SUCCESS")
        log_action("U", "READ", "Y", "R1", "SUCCESS")
        log_action("U", "WRITE", "Z", "R3", "SUCCESS")
        self.assertEqual(count_by_action("READ"), 2)

    def test_count_by_result(self):
        log_action("U", "PUBLISH", "X", "R4", "BLOCKED")
        log_action("U", "READ", "Y", "R1", "SUCCESS")
        log_action("U", "WRITE", "Z", "R3", "BLOCKED")
        self.assertEqual(count_by_result("BLOCKED"), 2)

    def test_last_n(self):
        for i in range(20):
            log_action("U", "READ", f"T-{i}", "R1", "SUCCESS")
        self.assertEqual(len(last_n(5)), 5)
        self.assertEqual(last_n(5)[-1]["target"], "T-19")

    def test_log_limit(self):
        for i in range(200):
            log_action("U", "READ", f"T-{i}", "R1", "SUCCESS")
        self.assertEqual(len(get_log(limit=50)), 50)

    def test_metadata_stored(self):
        entry = log_action("U", "PUBLISH", "CH-001", "R4", "SUCCESS",
                           metadata={"channel": "เสือ2992"})
        self.assertEqual(entry["metadata"]["channel"], "เสือ2992")

    def test_immutable_log_grows(self):
        log_action("U", "A", "X", "R1", "SUCCESS")
        log_action("U", "B", "Y", "R2", "SUCCESS")
        log_action("U", "C", "Z", "R3", "BLOCKED")
        self.assertEqual(len(get_log()), 3)


class TestIntegrationPhase2(unittest.TestCase):
    """End-to-end: Capability → QC → Approval → Audit"""

    def setUp(self):
        cap_reset()
        qc_reset()
        apr_reset()
        audit_reset()

    def test_publish_flow(self):
        cap = register("PLG-TIKTOK", "publish_video", ToolClass.PUBLISH)
        self.assertEqual(cap["risk"], "R4")
        self.assertTrue(cap["requires_approval"])

        content = {
            "id": "CNT-100",
            "text": "Amazing cooking product you need in your kitchen today",
            "product_link": "https://shop.tiktok.com/product/123",
            "link_status": "OK",
        }
        qc = check_before_publish(content)
        self.assertTrue(qc.passed)

        apr = request_approval("TASK-100", "PUBLISH", "R4", "USR-000001",
                                evidence_ids=["EV-100"])
        approve(apr["approval_id"], "ADMIN-001")

        log_action("USR-000001", "PUBLISH", "CH-001", "R4", "SUCCESS",
                   approval_id=apr["approval_id"], task_id="TASK-100",
                   plugin_id="PLG-TIKTOK")

        logs = get_log(task_id="TASK-100")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["result"], "SUCCESS")

    def test_blocked_by_qc(self):
        content = {
            "id": "CNT-101",
            "text": "รวยเร็วกับสินค้านี้",
            "product_link": "https://shop.tiktok.com/product/456",
            "link_status": "OK",
        }
        qc = check_before_publish(content)
        self.assertFalse(qc.passed)

        log_action("USR-000001", "PUBLISH", "CH-001", "R4", "BLOCKED_QC",
                   metadata={"qc_failures": qc.failures})

        self.assertEqual(count_by_result("BLOCKED_QC"), 1)

    def test_blocked_by_approval(self):
        apr = request_approval("TASK-102", "ADS_WRITE", "R5", "USR-000001")
        reject(apr["approval_id"], "ADMIN-001", "Budget not approved")

        log_action("USR-000001", "ADS_WRITE", "AD-001", "R5", "REJECTED",
                   approval_id=apr["approval_id"], task_id="TASK-102")

        self.assertEqual(count_by_result("REJECTED"), 1)


if __name__ == "__main__":
    unittest.main()
