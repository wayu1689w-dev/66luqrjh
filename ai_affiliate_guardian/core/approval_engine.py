"""Approval Engine — Spec sections 34-35
จัดการขั้นตอนอนุมัติ: R3+ ต้องขออนุมัติก่อนดำเนินการ"""

from datetime import datetime, timezone

_counter = 0
_approvals = {}


APPROVAL_STATES = ["PENDING", "APPROVED", "REJECTED", "REVOKED", "EXPIRED"]


def _next_id():
    global _counter
    _counter += 1
    return f"APR-{_counter:06d}"


def request_approval(task_id, action_type, risk, requested_by,
                     reason="", evidence_ids=None):
    apr_id = _next_id()
    approval = {
        "approval_id": apr_id,
        "task_id": task_id,
        "action_type": action_type,
        "risk": risk,
        "requested_by": requested_by,
        "reason": reason,
        "evidence_ids": evidence_ids or [],
        "state": "PENDING",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "decided_at": None,
        "decided_by": None,
    }
    _approvals[apr_id] = approval
    return approval


def approve(approval_id, decided_by):
    apr = _approvals.get(approval_id)
    if not apr:
        raise ValueError(f"Approval {approval_id} not found")
    if apr["state"] != "PENDING":
        raise ValueError(f"Cannot approve: state is {apr['state']}")
    apr["state"] = "APPROVED"
    apr["decided_at"] = datetime.now(timezone.utc).isoformat()
    apr["decided_by"] = decided_by
    return apr


def reject(approval_id, decided_by, reason=""):
    apr = _approvals.get(approval_id)
    if not apr:
        raise ValueError(f"Approval {approval_id} not found")
    if apr["state"] != "PENDING":
        raise ValueError(f"Cannot reject: state is {apr['state']}")
    apr["state"] = "REJECTED"
    apr["decided_at"] = datetime.now(timezone.utc).isoformat()
    apr["decided_by"] = decided_by
    apr["reject_reason"] = reason
    return apr


def revoke(approval_id, revoked_by, reason=""):
    apr = _approvals.get(approval_id)
    if not apr:
        raise ValueError(f"Approval {approval_id} not found")
    if apr["state"] != "APPROVED":
        raise ValueError(f"Cannot revoke: state is {apr['state']}")
    apr["state"] = "REVOKED"
    apr["decided_at"] = datetime.now(timezone.utc).isoformat()
    apr["decided_by"] = revoked_by
    apr["revoke_reason"] = reason
    return apr


def get(approval_id):
    return _approvals.get(approval_id)


def list_pending(task_id=None):
    result = [a for a in _approvals.values() if a["state"] == "PENDING"]
    if task_id:
        result = [a for a in result if a["task_id"] == task_id]
    return result


def is_approved(approval_id):
    apr = _approvals.get(approval_id)
    return apr["state"] == "APPROVED" if apr else False


def reset():
    global _counter
    _counter = 0
    _approvals.clear()
