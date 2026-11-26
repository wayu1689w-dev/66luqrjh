"""Content Registry — จัดการคอนเทนต์ทุกชิ้นทุกช่อง"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "content.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def add_content(content):
    items = _load()
    content["created_at"] = datetime.now(timezone.utc).isoformat()
    content["state"] = "draft"
    items.append(content)
    _save(items)
    return content


def get_content(content_id):
    items = _load()
    for c in items:
        if c.get("id") == content_id:
            return c
    return None


def list_by_channel(channel_id, state=None):
    items = _load()
    result = [c for c in items if c.get("channel_id") == channel_id]
    if state:
        result = [c for c in result if c.get("state") == state]
    return result


def update_content(content_id, updates):
    items = _load()
    for c in items:
        if c.get("id") == content_id:
            c.update(updates)
            c["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save(items)
            return c
    return None
