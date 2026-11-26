"""Audit — บันทึกทุกการกระทำ"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "audit_log.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def log_action(actor, action, target, details=""):
    items = _load()
    entry = {
        "actor": actor,
        "action": action,
        "target": target,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    items.append(entry)
    _save(items)
    return entry


def get_audit_log(actor=None, action=None):
    items = _load()
    if actor:
        items = [i for i in items if i.get("actor") == actor]
    if action:
        items = [i for i in items if i.get("action") == action]
    return items
