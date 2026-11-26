"""Metrics — วัดผลคลิปและช่อง"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "metrics.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def record_metrics(content_id, channel_id, data):
    items = _load()
    entry = {
        "content_id": content_id,
        "channel_id": channel_id,
        "views": data.get("views", 0),
        "likes": data.get("likes", 0),
        "comments": data.get("comments", 0),
        "shares": data.get("shares", 0),
        "clicks": data.get("clicks", 0),
        "conversions": data.get("conversions", 0),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(entry)
    _save(items)
    return entry


def get_metrics(content_id):
    items = _load()
    return [m for m in items if m.get("content_id") == content_id]
