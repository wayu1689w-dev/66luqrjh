"""Capability Registry — ลงทะเบียนความสามารถของแต่ละ plugin"""

import json
from pathlib import Path

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "capabilities.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def register_capability(plugin_id, tool_name, tool_class, risk_level, description=""):
    items = _load()
    entry = {
        "plugin_id": plugin_id,
        "tool_name": tool_name,
        "tool_class": tool_class,
        "risk_level": risk_level,
        "description": description,
        "enabled": False,
    }
    items.append(entry)
    _save(items)
    return entry


def get_capabilities(plugin_id):
    items = _load()
    return [c for c in items if c.get("plugin_id") == plugin_id]


def enable_capability(plugin_id, tool_name):
    items = _load()
    for c in items:
        if c["plugin_id"] == plugin_id and c["tool_name"] == tool_name:
            c["enabled"] = True
    _save(items)
