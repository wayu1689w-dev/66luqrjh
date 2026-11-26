"""Conflict Registry — ตรวจจับความขัดแย้งระหว่างข้อมูล"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "conflicts.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def report_conflict(entity_id, field, value_a, source_a, value_b, source_b):
    items = _load()
    entry = {
        "entity_id": entity_id,
        "field": field,
        "value_a": value_a,
        "source_a": source_a,
        "value_b": value_b,
        "source_b": source_b,
        "reported_at": datetime.now(timezone.utc).isoformat(),
        "resolved": False,
    }
    items.append(entry)
    _save(items)
    return entry


def list_unresolved():
    items = _load()
    return [i for i in items if not i.get("resolved")]


def resolve_conflict(entity_id, field, chosen_value, chosen_source):
    items = _load()
    for item in items:
        if item["entity_id"] == entity_id and item["field"] == field and not item["resolved"]:
            item["resolved"] = True
            item["chosen_value"] = chosen_value
            item["chosen_source"] = chosen_source
            item["resolved_at"] = datetime.now(timezone.utc).isoformat()
    _save(items)
