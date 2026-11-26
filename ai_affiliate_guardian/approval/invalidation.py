"""Invalidation — ถอนอนุมัติเมื่อข้อมูลเปลี่ยน"""

from .approval_gate import _load, _save
from datetime import datetime, timezone

TRIGGERS = [
    "price_changed",
    "product_unavailable",
    "commission_changed",
    "claim_disputed",
    "link_expired",
]


def invalidate(content_id, reason):
    if reason not in TRIGGERS:
        return False, f"เหตุผล '{reason}' ไม่อยู่ในรายการ"
    items = _load()
    for item in items:
        if item["content_id"] == content_id and item["state"] == "approved":
            item["state"] = "revoked"
            item["revoked_reason"] = reason
            item["revoked_at"] = datetime.now(timezone.utc).isoformat()
    _save(items)
    return True, f"ถอนอนุมัติ {content_id} เหตุ: {reason}"
