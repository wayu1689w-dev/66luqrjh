"""Evidence Registry — UNKNOWN ≠ 0, ESTIMATE ≠ CONFIRMED, CONFIRMED ≠ PAID"""

import json
from pathlib import Path
from datetime import datetime, timezone
from enum import Enum

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "evidence.json"


class EvidenceLevel(Enum):
    UNKNOWN = "unknown"
    ESTIMATE = "estimate"
    CONFIRMED = "confirmed"
    VERIFIED = "verified"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def record_evidence(entity_id, field, value, level, source):
    items = _load()
    entry = {
        "entity_id": entity_id,
        "field": field,
        "value": value,
        "level": level if isinstance(level, str) else level.value,
        "source": source,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(entry)
    _save(items)
    return entry


def get_evidence(entity_id, field=None):
    items = _load()
    result = [e for e in items if e.get("entity_id") == entity_id]
    if field:
        result = [e for e in result if e.get("field") == field]
    return result


def is_confirmed(entity_id, field):
    evidence = get_evidence(entity_id, field)
    if not evidence:
        return False
    latest = evidence[-1]
    return latest.get("level") in ("confirmed", "verified")
