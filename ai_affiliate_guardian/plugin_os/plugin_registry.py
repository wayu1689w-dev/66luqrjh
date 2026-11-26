"""Plugin Registry — Scalable registry รองรับ PLG-00000001 ถึง PLG-00100000+"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "plugin_registry.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def _next_id(items):
    if not items:
        return "PLG-00000001"
    max_num = 0
    for item in items:
        pid = item.get("plugin_id", "PLG-00000000")
        num = int(pid.split("-")[1])
        if num > max_num:
            max_num = num
    return f"PLG-{max_num + 1:08d}"


def register_plugin(provider, gateway, name, documentation_status="VERIFIED"):
    items = _load()
    plugin_id = _next_id(items)
    record = {
        "plugin_id": plugin_id,
        "provider": provider,
        "gateway": gateway,
        "name": name,
        "documentation": documentation_status,
        "discovered": True,
        "registered": True,
        "authorized": False,
        "connected": False,
        "permissions_verified": False,
        "health_check": "NOT_RUN",
        "production_ready": False,
        "risk": "UNKNOWN",
        "state": "registered",
        "evidence_ids": [],
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(record)
    _save(items)
    return record


def get_plugin(plugin_id):
    items = _load()
    for p in items:
        if p.get("plugin_id") == plugin_id:
            return p
    return None


def list_plugins(provider=None, gateway=None, state=None):
    items = _load()
    if provider:
        items = [p for p in items if p.get("provider") == provider]
    if gateway:
        items = [p for p in items if p.get("gateway") == gateway]
    if state:
        items = [p for p in items if p.get("state") == state]
    return items


def update_plugin(plugin_id, updates):
    items = _load()
    for p in items:
        if p.get("plugin_id") == plugin_id:
            p.update(updates)
            p["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save(items)
            return p
    return None


def count_plugins():
    return len(_load())
