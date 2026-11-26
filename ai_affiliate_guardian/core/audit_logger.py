"""Audit Logger — Spec section 46
บันทึกทุก Action ที่เกิดขึ้น ห้ามลบ ห้ามแก้ไข"""

from datetime import datetime, timezone

_counter = 0
_log = []


def _next_id():
    global _counter
    _counter += 1
    return f"AUD-{_counter:06d}"


def log_action(actor, action_type, target, risk, result,
               approval_id=None, task_id=None, evidence_ids=None,
               plugin_id=None, metadata=None):
    audit_id = _next_id()
    entry = {
        "audit_id": audit_id,
        "actor": actor,
        "action_type": action_type,
        "target": target,
        "risk": risk,
        "result": result,
        "approval_id": approval_id,
        "task_id": task_id,
        "evidence_ids": evidence_ids or [],
        "plugin_id": plugin_id,
        "metadata": metadata or {},
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    _log.append(entry)
    return entry


def get_log(audit_id=None, actor=None, action_type=None,
            task_id=None, limit=100):
    result = list(_log)
    if audit_id:
        result = [e for e in result if e["audit_id"] == audit_id]
    if actor:
        result = [e for e in result if e["actor"] == actor]
    if action_type:
        result = [e for e in result if e["action_type"] == action_type]
    if task_id:
        result = [e for e in result if e["task_id"] == task_id]
    return result[-limit:]


def count_by_action(action_type):
    return sum(1 for e in _log if e["action_type"] == action_type)


def count_by_result(result_value):
    return sum(1 for e in _log if e["result"] == result_value)


def last_n(n=10):
    return _log[-n:]


def reset():
    global _counter
    _counter = 0
    _log.clear()
