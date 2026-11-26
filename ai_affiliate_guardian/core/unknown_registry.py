"""Unknown Registry — ติดตามสิ่งที่ยังไม่รู้ ไม่สมมติว่าเป็น 0"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "unknowns.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def flag_unknown(entity_id, field, reason=""):
    items = _load()
    entry = {
        "entity_id": entity_id,
        "field": field,
        "reason": reason,
        "flagged_at": datetime.now(timezone.utc).isoformat(),
        "resolved": False,
    }
    items.append(entry)
    _save(items)
    return entry


def resolve_unknown(entity_id, field):
    items = _load()
    for item in items:
        if item["entity_id"] == entity_id and item["field"] == field:
            item["resolved"] = True
            item["resolved_at"] = datetime.now(timezone.utc).isoformat()
    _save(items)


def list_unresolved():
    items = _load()
    return [i for i in items if not i.get("resolved")]
