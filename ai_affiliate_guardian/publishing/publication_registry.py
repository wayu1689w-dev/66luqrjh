"""Publication Registry — บันทึกการเผยแพร่"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "publications.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def record_publication(content_id, channel_id, platform_post_id=""):
    items = _load()
    entry = {
        "content_id": content_id,
        "channel_id": channel_id,
        "platform_post_id": platform_post_id,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(entry)
    _save(items)
    return entry


def get_publications(channel_id=None):
    items = _load()
    if channel_id:
        return [i for i in items if i.get("channel_id") == channel_id]
    return items
