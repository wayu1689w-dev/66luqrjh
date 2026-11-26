"""Commission Ledger — บัญชีค่าคอมมิชชั่น"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "commissions.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def record_commission(content_id, product_id, channel_id, amount, state="unknown"):
    items = _load()
    entry = {
        "content_id": content_id,
        "product_id": product_id,
        "channel_id": channel_id,
        "amount": amount,
        "state": state,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(entry)
    _save(items)
    return entry


def get_ledger(channel_id=None, state=None):
    items = _load()
    if channel_id:
        items = [i for i in items if i.get("channel_id") == channel_id]
    if state:
        items = [i for i in items if i.get("state") == state]
    return items


def total_by_state():
    items = _load()
    totals = {}
    for i in items:
        s = i.get("state", "unknown")
        totals[s] = totals.get(s, 0) + i.get("amount", 0)
    return totals
