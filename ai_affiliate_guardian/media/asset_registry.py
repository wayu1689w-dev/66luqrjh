"""Asset Registry — จัดการไฟล์สื่อทั้งหมด"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "assets.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def register_asset(content_id, asset_type, file_path, metadata=None):
    items = _load()
    entry = {
        "content_id": content_id,
        "asset_type": asset_type,
        "file_path": file_path,
        "metadata": metadata or {},
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(entry)
    _save(items)
    return entry


def get_assets(content_id):
    items = _load()
    return [a for a in items if a.get("content_id") == content_id]
