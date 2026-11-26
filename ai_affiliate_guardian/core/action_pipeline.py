"""Action Pipeline — Spec sections 44-45
ACTION → IDENTITY → RESOURCE → PERMISSION → EVIDENCE → CONFLICT →
POLICY → APPROVAL → PRECHECK → EXECUTION → VALIDATION → AUDIT"""

from datetime import datetime, timezone

_counter = 0


def _next_id():
    global _counter
    _counter += 1
    return f"ACT-{_counter:06d}"


class ActionResult:
    def __init__(self, action_id, state, reason=None, stage=None):
        self.action_id = action_id
        self.state = state
        self.reason = reason
        self.stage = stage

    def to_dict(self):
        return {
            "action_id": self.action_id,
            "state": self.state,
            "reason": self.reason,
            "stage": self.stage,
        }


PIPELINE_STAGES = [
    "IDENTITY",
    "RESOURCE",
    "PERMISSION",
    "EVIDENCE",
    "CONFLICT",
    "POLICY",
    "APPROVAL",
    "PRECHECK",
    "EXECUTION",
    "VALIDATION",
    "AUDIT",
]


def create_action(task_id, action_type, target, external=False,
                   approval_required=False):
    action_id = _next_id()
    return {
        "action_id": action_id,
        "task_id": task_id,
        "action_type": action_type,
        "target": target,
        "external": external,
        "approval_required": approval_required,
        "state": "READY",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def run_pipeline(action, checks):
    """Run the action through the full pipeline.

    checks: dict mapping stage name → bool or callable returning (bool, reason).
    Missing stages pass by default.
    """
    action_id = action.get("action_id", _next_id())
    results = []

    for stage in PIPELINE_STAGES:
        checker = checks.get(stage)
        if checker is None:
            results.append((stage, True, None))
            continue

        if callable(checker):
            outcome = checker(action)
            if isinstance(outcome, tuple):
                passed, reason = outcome
            else:
                passed = bool(outcome)
                reason = None
        elif isinstance(checker, tuple):
            passed, reason = checker
        else:
            passed = bool(checker)
            reason = None

        results.append((stage, passed, reason))

        if not passed:
            return ActionResult(
                action_id=action_id,
                state="BLOCKED",
                reason=reason or f"Failed at {stage}",
                stage=stage,
            )

    return ActionResult(
        action_id=action_id,
        state="COMPLETED",
        reason=None,
        stage="AUDIT",
    )


def reset():
    global _counter
    _counter = 0
