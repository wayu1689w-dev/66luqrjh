"""Approval Gate — ประตูอนุมัติ ต้องผ่านคนเสมอ"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "approvals.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def request_approval(content_id, gate_type, details=""):
    items = _load()
    entry = {
        "content_id": content_id,
        "gate_type": gate_type,
        "state": "pending",
        "details": details,
        "requested_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(entry)
    _save(items)
    return entry


def approve(content_id, gate_type, approved_by="owner"):
    items = _load()
    for item in items:
        if item["content_id"] == content_id and item["gate_type"] == gate_type:
            item["state"] = "approved"
            item["approved_by"] = approved_by
            item["approved_at"] = datetime.now(timezone.utc).isoformat()
    _save(items)


def reject(content_id, gate_type, reason=""):
    items = _load()
    for item in items:
        if item["content_id"] == content_id and item["gate_type"] == gate_type:
            item["state"] = "rejected"
            item["reason"] = reason
            item["rejected_at"] = datetime.now(timezone.utc).isoformat()
    _save(items)


def is_approved(content_id, gate_type):
    items = _load()
    for item in items:
        if item["content_id"] == content_id and item["gate_type"] == gate_type:
            return item["state"] == "approved"
    return False
