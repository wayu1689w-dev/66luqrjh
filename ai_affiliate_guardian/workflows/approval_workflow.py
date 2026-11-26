"""Approval Workflow — ขั้นตอนอนุมัติ"""

from ..approval.approval_gate import request_approval, is_approved


def run_approval_pipeline(content):
    content_id = content.get("id", "")
    steps = []

    req = request_approval(content_id, "content_publish", "รอเจ้าของอนุมัติ")
    steps.append({"step": "request_sent", "approval": req})

    approved = is_approved(content_id, "content_publish")
    steps.append({"step": "check_status", "approved": approved})

    return {
        "content_id": content_id,
        "approved": approved,
        "steps": steps,
        "note": "ต้องรอเจ้าของกดอนุมัติ — ไม่มี auto-approve",
    }
