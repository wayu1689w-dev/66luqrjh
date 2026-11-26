"""Experiment Registry — ทดลอง A/B ระหว่างมุมนำเสนอ"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "experiments.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def create_experiment(name, channel_id, variants):
    items = _load()
    entry = {
        "name": name,
        "channel_id": channel_id,
        "variants": variants,
        "state": "running",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "results": {},
    }
    items.append(entry)
    _save(items)
    return entry


def record_result(name, variant, metrics):
    items = _load()
    for item in items:
        if item["name"] == name:
            item["results"][variant] = metrics
    _save(items)
