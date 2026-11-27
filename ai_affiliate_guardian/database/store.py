"""Database Store — Spec v008 Area 7
JSON-file storage พร้อม SHA-256 integrity, backup, recovery"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

from ..security.data_integrity import compute_hash

STORAGE_ROOT = Path(__file__).parent.parent / "storage"


class Store:
    def __init__(self, collection: str):
        self.collection = collection
        self.path = STORAGE_ROOT / f"{collection}.json"

    def _load(self) -> list[dict]:
        if self.path.exists():
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self, items: list[dict]):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    def insert(self, record: dict) -> dict:
        items = self._load()
        record["_created_at"] = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(record, sort_keys=True, ensure_ascii=False)
        record["_hash"] = compute_hash(payload)
        items.append(record)
        self._save(items)
        return record

    def find(self, **filters) -> list[dict]:
        items = self._load()
        result = []
        for item in items:
            if all(item.get(k) == v for k, v in filters.items()):
                result.append(item)
        return result

    def find_one(self, **filters) -> dict | None:
        matches = self.find(**filters)
        return matches[0] if matches else None

    def count(self, **filters) -> int:
        return len(self.find(**filters))

    def all(self) -> list[dict]:
        return self._load()

    def delete(self, **filters) -> int:
        items = self._load()
        before = len(items)
        items = [i for i in items if not all(i.get(k) == v for k, v in filters.items())]
        self._save(items)
        return before - len(items)

    def update(self, filters: dict, updates: dict) -> int:
        items = self._load()
        updated = 0
        for item in items:
            if all(item.get(k) == v for k, v in filters.items()):
                item.update(updates)
                item["_updated_at"] = datetime.now(timezone.utc).isoformat()
                updated += 1
        self._save(items)
        return updated

    def backup(self) -> str:
        backup_dir = STORAGE_ROOT / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dest = backup_dir / f"{self.collection}_{ts}.json"
        if self.path.exists():
            shutil.copy2(self.path, dest)
        return str(dest)

    def integrity_check(self) -> list[dict]:
        items = self._load()
        failures = []
        for i, item in enumerate(items):
            stored = item.get("_hash")
            if not stored:
                continue
            clean = {k: v for k, v in item.items()
                     if k not in ("_hash", "_signed_at", "_created_at", "_updated_at")}
            payload = json.dumps(clean, sort_keys=True, ensure_ascii=False)
            if compute_hash(payload) != stored:
                failures.append({"index": i, "status": "TAMPERED"})
        return failures
