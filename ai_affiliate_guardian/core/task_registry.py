"""Task Registry — Spec sections 12-13
Task state machine + registry ตาม Master Spec"""

from datetime import datetime, timezone
from enum import Enum

_counter = 0
_tasks = {}


class TaskState(Enum):
    NEW = "NEW"
    PLANNING = "PLANNING"
    DATA_REQUIRED = "DATA_REQUIRED"
    EVIDENCE_CHECK = "EVIDENCE_CHECK"
    IYO_ANALYSIS = "IYO_ANALYSIS"
    GUARDIAN_REVIEW = "GUARDIAN_REVIEW"
    READY = "READY"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    # Side states
    WAITING_FOR_DATA = "WAITING_FOR_DATA"
    WAITING_FOR_EVIDENCE = "WAITING_FOR_EVIDENCE"
    BLOCKED = "BLOCKED"
    CONFLICTING = "CONFLICTING"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


VALID_TRANSITIONS = {
    TaskState.NEW: {TaskState.PLANNING, TaskState.CANCELLED},
    TaskState.PLANNING: {TaskState.DATA_REQUIRED, TaskState.EVIDENCE_CHECK, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.DATA_REQUIRED: {TaskState.WAITING_FOR_DATA, TaskState.EVIDENCE_CHECK, TaskState.CANCELLED},
    TaskState.WAITING_FOR_DATA: {TaskState.DATA_REQUIRED, TaskState.EVIDENCE_CHECK, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.EVIDENCE_CHECK: {TaskState.IYO_ANALYSIS, TaskState.WAITING_FOR_EVIDENCE, TaskState.CONFLICTING, TaskState.CANCELLED},
    TaskState.WAITING_FOR_EVIDENCE: {TaskState.EVIDENCE_CHECK, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.IYO_ANALYSIS: {TaskState.GUARDIAN_REVIEW, TaskState.CONFLICTING, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.GUARDIAN_REVIEW: {TaskState.READY, TaskState.APPROVAL_REQUIRED, TaskState.BLOCKED, TaskState.REJECTED, TaskState.CANCELLED},
    TaskState.READY: {TaskState.EXECUTING, TaskState.APPROVAL_REQUIRED, TaskState.CANCELLED},
    TaskState.APPROVAL_REQUIRED: {TaskState.APPROVED, TaskState.REJECTED, TaskState.CANCELLED},
    TaskState.APPROVED: {TaskState.EXECUTING, TaskState.CANCELLED},
    TaskState.EXECUTING: {TaskState.VALIDATING, TaskState.FAILED},
    TaskState.VALIDATING: {TaskState.COMPLETED, TaskState.FAILED},
    TaskState.CONFLICTING: {TaskState.EVIDENCE_CHECK, TaskState.CANCELLED},
    TaskState.BLOCKED: {TaskState.PLANNING, TaskState.CANCELLED},
    TaskState.FAILED: {TaskState.PLANNING},
}


def _next_id():
    global _counter
    _counter += 1
    return f"TASK-{_counter:06d}"


def create_task(user_id, objective, channel_id=None,
                requires_fresh_data=True, requires_external_data=False,
                requires_approval=False):
    task_id = _next_id()
    task = {
        "task_id": task_id,
        "created_by": user_id,
        "objective": objective,
        "channel_id": channel_id,
        "state": TaskState.NEW.value,
        "requires_fresh_data": requires_fresh_data,
        "requires_external_data": requires_external_data,
        "requires_approval": requires_approval,
        "evidence_ids": [],
        "result_id": None,
        "history": [{"state": TaskState.NEW.value,
                      "at": datetime.now(timezone.utc).isoformat()}],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _tasks[task_id] = task
    return task


def transition(task_id, new_state):
    if isinstance(new_state, str):
        new_state = TaskState(new_state)
    task = _tasks.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    current = TaskState(task["state"])
    allowed = VALID_TRANSITIONS.get(current, set())
    if new_state not in allowed:
        raise ValueError(
            f"Cannot transition {task_id} from {current.value} to {new_state.value}")
    task["state"] = new_state.value
    task["history"].append({
        "state": new_state.value,
        "at": datetime.now(timezone.utc).isoformat(),
    })
    return task


def get_task(task_id):
    return _tasks.get(task_id)


def get_tasks_by_state(state):
    if isinstance(state, TaskState):
        state = state.value
    return [t for t in _tasks.values() if t["state"] == state]


def attach_evidence(task_id, evidence_id):
    task = _tasks.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    if evidence_id not in task["evidence_ids"]:
        task["evidence_ids"].append(evidence_id)
    return task


def reset():
    global _counter
    _counter = 0
    _tasks.clear()
