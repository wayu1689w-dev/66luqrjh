"""Tests for Core Engine — Task, Guardian, IYO, Action Pipeline, Kill Switch
ครอบคลุม Spec sections 8-13, 44-45, 62, 77"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.task_registry import (
    create_task, transition, get_task, get_tasks_by_state,
    attach_evidence, TaskState, VALID_TRANSITIONS, reset as task_reset,
)
from core.guardian_engine import (
    evaluate_action, permission_intersection, GuardianVerdict,
    RISK_APPROVAL_MAP,
)
from core.iyo import (
    analyze, Confidence, ScoreState, Recommendation,
    reset as iyo_reset,
)
from core.action_pipeline import (
    create_action, run_pipeline, ActionResult, PIPELINE_STAGES,
    reset as action_reset,
)
from core.kill_switch import (
    get_state, is_killed, activate, deactivate, kill_all,
    check_action_blocked, reset_all,
)


class TestTaskRegistry(unittest.TestCase):
    def setUp(self):
        task_reset()

    def test_create_task(self):
        t = create_task("USR-000001", "SELECT_PRODUCT", "CH-001")
        self.assertEqual(t["state"], "NEW")
        self.assertTrue(t["task_id"].startswith("TASK-"))
        self.assertEqual(t["created_by"], "USR-000001")

    def test_transition_new_to_planning(self):
        t = create_task("USR-000001", "ANALYZE")
        t2 = transition(t["task_id"], TaskState.PLANNING)
        self.assertEqual(t2["state"], "PLANNING")

    def test_invalid_transition_blocked(self):
        t = create_task("USR-000001", "TEST")
        with self.assertRaises(ValueError):
            transition(t["task_id"], TaskState.COMPLETED)

    def test_full_happy_path(self):
        t = create_task("USR-000001", "PUBLISH")
        path = [
            TaskState.PLANNING,
            TaskState.EVIDENCE_CHECK,
            TaskState.IYO_ANALYSIS,
            TaskState.GUARDIAN_REVIEW,
            TaskState.APPROVAL_REQUIRED,
            TaskState.APPROVED,
            TaskState.EXECUTING,
            TaskState.VALIDATING,
            TaskState.COMPLETED,
        ]
        for state in path:
            t = transition(t["task_id"], state)
        self.assertEqual(t["state"], "COMPLETED")
        self.assertEqual(len(t["history"]), 10)

    def test_cancel_from_new(self):
        t = create_task("USR-000001", "X")
        t = transition(t["task_id"], TaskState.CANCELLED)
        self.assertEqual(t["state"], "CANCELLED")

    def test_attach_evidence(self):
        t = create_task("USR-000001", "X")
        attach_evidence(t["task_id"], "EV-001")
        attach_evidence(t["task_id"], "EV-002")
        attach_evidence(t["task_id"], "EV-001")  # dedup
        self.assertEqual(len(get_task(t["task_id"])["evidence_ids"]), 2)

    def test_get_tasks_by_state(self):
        create_task("USR-000001", "A")
        t2 = create_task("USR-000001", "B")
        transition(t2["task_id"], TaskState.PLANNING)
        self.assertEqual(len(get_tasks_by_state("NEW")), 1)
        self.assertEqual(len(get_tasks_by_state(TaskState.PLANNING)), 1)

    def test_blocked_to_planning_recovery(self):
        t = create_task("USR-000001", "X")
        transition(t["task_id"], TaskState.PLANNING)
        transition(t["task_id"], TaskState.BLOCKED)
        t = transition(t["task_id"], TaskState.PLANNING)
        self.assertEqual(t["state"], "PLANNING")

    def test_failed_to_planning_retry(self):
        t = create_task("USR-000001", "X")
        transition(t["task_id"], TaskState.PLANNING)
        transition(t["task_id"], TaskState.EVIDENCE_CHECK)
        transition(t["task_id"], TaskState.IYO_ANALYSIS)
        transition(t["task_id"], TaskState.GUARDIAN_REVIEW)
        transition(t["task_id"], TaskState.READY)
        transition(t["task_id"], TaskState.EXECUTING)
        transition(t["task_id"], TaskState.FAILED)
        t = transition(t["task_id"], TaskState.PLANNING)
        self.assertEqual(t["state"], "PLANNING")

    def test_nonexistent_task(self):
        with self.assertRaises(ValueError):
            transition("TASK-999999", TaskState.PLANNING)


class TestGuardianEngine(unittest.TestCase):
    def test_allow_local_action(self):
        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "ANALYZE",
            "risk": "R0",
            "plugin_state": None,
            "evidence_ids": [],
            "approval_id": None,
            "external": False,
            "system_policy": {},
        })
        self.assertTrue(v.allowed)
        self.assertEqual(v.reason, "PASS")

    def test_block_no_actor(self):
        v = evaluate_action({
            "actor": None,
            "action_type": "READ",
            "risk": "R0",
            "system_policy": {},
        })
        self.assertFalse(v.allowed)
        self.assertIn("No actor", v.reason)

    def test_block_r5_no_approval(self):
        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "ADS_WRITE",
            "risk": "R5",
            "plugin_state": "CONNECTED",
            "evidence_ids": ["EV-001"],
            "approval_id": None,
            "external": True,
            "system_policy": {},
        })
        self.assertFalse(v.allowed)
        self.assertIn("Approval required", v.reason)

    def test_allow_r5_with_approval(self):
        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "ADS_WRITE",
            "risk": "R5",
            "plugin_state": "PRODUCTION_READY",
            "evidence_ids": ["EV-001"],
            "approval_id": "APR-001",
            "external": True,
            "system_policy": {},
        })
        self.assertTrue(v.allowed)

    def test_kill_switch_blocks(self):
        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "PUBLISH",
            "risk": "R4",
            "approval_id": "APR-001",
            "external": True,
            "system_policy": {"KILL_PUBLISH": True},
        })
        self.assertFalse(v.allowed)
        self.assertIn("KILL_PUBLISH", v.reason)

    def test_kill_all_external(self):
        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "READ",
            "risk": "R1",
            "external": True,
            "system_policy": {"KILL_ALL_EXTERNAL": True},
        })
        self.assertFalse(v.allowed)

    def test_unhealthy_plugin(self):
        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "READ",
            "risk": "R1",
            "plugin_state": "FAILED",
            "external": False,
            "system_policy": {},
        })
        self.assertFalse(v.allowed)
        self.assertIn("not healthy", v.reason)

    def test_evidence_required_missing(self):
        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "PUBLISH",
            "risk": "R4",
            "approval_id": "APR-001",
            "evidence_required": True,
            "evidence_ids": [],
            "external": False,
            "system_policy": {},
        })
        self.assertFalse(v.allowed)
        self.assertIn("Evidence required", v.reason)

    def test_permission_intersection_all_true(self):
        self.assertTrue(permission_intersection(True, True, True, True, True))

    def test_permission_intersection_one_false(self):
        self.assertFalse(permission_intersection(True, False, True, True, True))

    def test_verdict_to_dict(self):
        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "ANALYZE",
            "risk": "R0",
            "system_policy": {},
        })
        d = v.to_dict()
        self.assertIn("allowed", d)
        self.assertIn("evaluated_at", d)

    def test_risk_approval_map_r0_r2_no_approval(self):
        for r in ("R0", "R1", "R2"):
            self.assertFalse(RISK_APPROVAL_MAP[r])

    def test_risk_approval_map_r3_r5_needs_approval(self):
        for r in ("R3", "R4", "R5"):
            self.assertTrue(RISK_APPROVAL_MAP[r])


class TestIYO(unittest.TestCase):
    def setUp(self):
        iyo_reset()

    def test_complete_data_high_score(self):
        result = analyze(
            task_id="TASK-000001",
            data={"price": 99, "commission": 15, "stock": 500,
                  "affiliate": True, "category": "food"},
            evidence_ids=["EV-001", "EV-002", "EV-003"],
        )
        self.assertEqual(result["score_state"], "COMPLETE")
        self.assertEqual(result["confidence"], "HIGH")
        self.assertEqual(result["score"], 100.0)
        self.assertTrue(result["action_allowed"])

    def test_incomplete_with_unknowns(self):
        result = analyze(
            task_id="TASK-000002",
            data={"price": None, "commission": None, "stock": 100},
            unknowns=["price", "commission", "promotion"],
        )
        self.assertEqual(result["score_state"], "INCOMPLETE")
        self.assertEqual(result["recommendation"], "NEED_MORE_DATA")
        self.assertFalse(result["action_allowed"])
        self.assertIn("price", result["unknowns"])

    def test_conflicting_data(self):
        result = analyze(
            task_id="TASK-000003",
            data={"price": 99},
            conflicts=[{"conflict_id": "CONF-001", "field": "price", "status": "OPEN"}],
        )
        self.assertEqual(result["score_state"], "CONFLICTING")
        self.assertEqual(result["recommendation"], "BLOCK")
        self.assertFalse(result["action_allowed"])

    def test_low_score_reject(self):
        result = analyze(
            task_id="TASK-000004",
            data={"a": None, "b": None, "c": "ok"},
            evidence_ids=["EV-001"],
        )
        self.assertLess(result["score"], 50)
        self.assertEqual(result["recommendation"], "REJECT")

    def test_medium_score_review(self):
        result = analyze(
            task_id="TASK-000005",
            data={"a": "ok", "b": "ok", "c": None, "d": "ok"},
            evidence_ids=["EV-001"],
        )
        self.assertEqual(result["score"], 75.0)
        self.assertEqual(result["recommendation"], "SELECT_FOR_REVIEW")

    def test_no_data(self):
        result = analyze(task_id="TASK-000006", data={})
        self.assertEqual(result["recommendation"], "REJECT")

    def test_resolved_conflict_not_blocking(self):
        result = analyze(
            task_id="TASK-000007",
            data={"price": 99},
            conflicts=[{"conflict_id": "CONF-001", "status": "RESOLVED"}],
            evidence_ids=["EV-001"],
        )
        self.assertNotEqual(result["recommendation"], "BLOCK")

    def test_iyo_result_id(self):
        r1 = analyze("T1", {"x": 1}, evidence_ids=["E1"])
        r2 = analyze("T2", {"x": 1}, evidence_ids=["E1"])
        self.assertNotEqual(r1["iyo_result_id"], r2["iyo_result_id"])

    def test_recommendation_not_permission(self):
        result = analyze("T", {"price": 99, "stock": 100, "comm": 20,
                                "aff": True, "cat": "food"},
                          evidence_ids=["E1", "E2", "E3"])
        self.assertEqual(result["recommendation"], "APPROVE")
        self.assertNotIn("permission", result)


class TestActionPipeline(unittest.TestCase):
    def setUp(self):
        action_reset()

    def test_all_pass(self):
        a = create_action("TASK-001", "ANALYZE", {"product_id": "PRD-001"})
        result = run_pipeline(a, {})
        self.assertEqual(result.state, "COMPLETED")

    def test_identity_fail(self):
        a = create_action("TASK-001", "READ", {})
        result = run_pipeline(a, {
            "IDENTITY": False,
        })
        self.assertEqual(result.state, "BLOCKED")
        self.assertEqual(result.stage, "IDENTITY")

    def test_approval_fail(self):
        a = create_action("TASK-001", "PUBLISH", {}, approval_required=True)
        result = run_pipeline(a, {
            "IDENTITY": True,
            "RESOURCE": True,
            "PERMISSION": True,
            "EVIDENCE": True,
            "CONFLICT": True,
            "POLICY": True,
            "APPROVAL": (False, "No approval for PUBLISH"),
        })
        self.assertEqual(result.state, "BLOCKED")
        self.assertEqual(result.stage, "APPROVAL")
        self.assertIn("No approval", result.reason)

    def test_callable_checker(self):
        a = create_action("TASK-001", "READ", {})

        def check_evidence(action):
            return action.get("task_id") == "TASK-001"

        result = run_pipeline(a, {"EVIDENCE": check_evidence})
        self.assertEqual(result.state, "COMPLETED")

    def test_callable_tuple_checker(self):
        a = create_action("TASK-001", "WRITE", {"target": "X"})

        def check_policy(action):
            return False, "Policy KILL_ADS active"

        result = run_pipeline(a, {"POLICY": check_policy})
        self.assertEqual(result.state, "BLOCKED")
        self.assertIn("KILL_ADS", result.reason)

    def test_pipeline_stages_order(self):
        self.assertEqual(PIPELINE_STAGES[0], "IDENTITY")
        self.assertEqual(PIPELINE_STAGES[-1], "AUDIT")
        self.assertEqual(len(PIPELINE_STAGES), 11)

    def test_create_action_fields(self):
        a = create_action("TASK-001", "PUBLISH", {"ch": "CH-001"},
                           external=True, approval_required=True)
        self.assertTrue(a["external"])
        self.assertTrue(a["approval_required"])
        self.assertEqual(a["state"], "READY")

    def test_result_to_dict(self):
        r = ActionResult("ACT-001", "COMPLETED")
        d = r.to_dict()
        self.assertEqual(d["state"], "COMPLETED")


class TestKillSwitch(unittest.TestCase):
    def setUp(self):
        reset_all()

    def test_all_killed_by_default(self):
        state = get_state()
        for k, v in state.items():
            self.assertTrue(v, f"{k} should be killed by default")

    def test_deactivate_and_activate(self):
        deactivate("KILL_PUBLISH")
        self.assertFalse(is_killed("KILL_PUBLISH"))
        activate("KILL_PUBLISH")
        self.assertTrue(is_killed("KILL_PUBLISH"))

    def test_unknown_switch_raises(self):
        with self.assertRaises(ValueError):
            activate("KILL_NONEXISTENT")

    def test_check_action_blocked_external(self):
        blocked, reason = check_action_blocked("READ", external=True)
        self.assertTrue(blocked)
        self.assertEqual(reason, "KILL_ALL_EXTERNAL")

    def test_check_action_blocked_publish(self):
        blocked, reason = check_action_blocked("PUBLISH")
        self.assertTrue(blocked)
        self.assertEqual(reason, "KILL_PUBLISH")

    def test_check_action_blocked_ads(self):
        blocked, reason = check_action_blocked("ADS_WRITE")
        self.assertTrue(blocked)
        self.assertEqual(reason, "KILL_ADS")

    def test_check_action_blocked_commerce(self):
        blocked, reason = check_action_blocked("COMMERCE_WRITE")
        self.assertTrue(blocked)
        self.assertEqual(reason, "KILL_COMMERCE")

    def test_check_action_not_blocked_local(self):
        deactivate("KILL_ALL_EXTERNAL")
        blocked, reason = check_action_blocked("ANALYZE", external=False)
        self.assertFalse(blocked)
        self.assertIsNone(reason)

    def test_kill_all_resets(self):
        deactivate("KILL_PUBLISH")
        deactivate("KILL_ADS")
        kill_all()
        self.assertTrue(is_killed("KILL_PUBLISH"))
        self.assertTrue(is_killed("KILL_ADS"))

    def test_kill_switch_stops_action_not_audit(self):
        blocked, _ = check_action_blocked("PUBLISH")
        self.assertTrue(blocked)


class TestIntegration(unittest.TestCase):
    """End-to-end: Task → IYO → Guardian → Action Pipeline"""

    def setUp(self):
        task_reset()
        iyo_reset()
        action_reset()
        reset_all()

    def test_happy_path_local_analysis(self):
        t = create_task("USR-000001", "ANALYZE_PRODUCT", "CH-001")
        transition(t["task_id"], TaskState.PLANNING)
        transition(t["task_id"], TaskState.EVIDENCE_CHECK)

        attach_evidence(t["task_id"], "EV-001")
        attach_evidence(t["task_id"], "EV-002")
        attach_evidence(t["task_id"], "EV-003")

        transition(t["task_id"], TaskState.IYO_ANALYSIS)

        iyo = analyze(
            task_id=t["task_id"],
            data={"price": 99, "commission": 15, "stock": 200,
                  "affiliate": True, "category": "food"},
            evidence_ids=t["evidence_ids"],
        )
        self.assertEqual(iyo["recommendation"], "APPROVE")
        self.assertTrue(iyo["action_allowed"])

        transition(t["task_id"], TaskState.GUARDIAN_REVIEW)

        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "ANALYZE",
            "risk": "R0",
            "plugin_state": None,
            "evidence_ids": t["evidence_ids"],
            "approval_id": None,
            "external": False,
            "system_policy": get_state(),
        })
        self.assertTrue(v.allowed)

        transition(t["task_id"], TaskState.READY)
        transition(t["task_id"], TaskState.EXECUTING)

        a = create_action(t["task_id"], "ANALYZE",
                           {"product_id": "PRD-001", "channel_id": "CH-001"})
        result = run_pipeline(a, {})
        self.assertEqual(result.state, "COMPLETED")

        transition(t["task_id"], TaskState.VALIDATING)
        transition(t["task_id"], TaskState.COMPLETED)
        self.assertEqual(get_task(t["task_id"])["state"], "COMPLETED")

    def test_blocked_by_kill_switch(self):
        t = create_task("USR-000001", "PUBLISH_VIDEO", "CH-001",
                         requires_approval=True)
        transition(t["task_id"], TaskState.PLANNING)

        v = evaluate_action({
            "actor": "USR-000001",
            "action_type": "PUBLISH",
            "risk": "R4",
            "approval_id": "APR-001",
            "external": True,
            "system_policy": get_state(),
        })
        self.assertFalse(v.allowed)

        transition(t["task_id"], TaskState.BLOCKED)
        self.assertEqual(get_task(t["task_id"])["state"], "BLOCKED")

    def test_iyo_conflict_blocks_task(self):
        t = create_task("USR-000001", "SELECT_PRODUCT")
        transition(t["task_id"], TaskState.PLANNING)
        transition(t["task_id"], TaskState.EVIDENCE_CHECK)
        transition(t["task_id"], TaskState.IYO_ANALYSIS)

        iyo = analyze(
            task_id=t["task_id"],
            data={"price": 99},
            conflicts=[{"conflict_id": "CONF-001", "field": "price",
                        "status": "OPEN"}],
        )
        self.assertEqual(iyo["recommendation"], "BLOCK")
        self.assertFalse(iyo["action_allowed"])

        transition(t["task_id"], TaskState.CONFLICTING)
        self.assertEqual(get_task(t["task_id"])["state"], "CONFLICTING")


if __name__ == "__main__":
    unittest.main()
