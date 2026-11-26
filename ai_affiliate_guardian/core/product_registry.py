"""Product Registry — ศูนย์กลางข้อมูลสินค้า"""

import json
from pathlib import Path
from datetime import datetime, timezone

STORAGE_PATH = Path(__file__).parent.parent / "storage" / "products.json"


def _load():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(products):
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def add_product(product):
    products = _load()
    product["created_at"] = datetime.now(timezone.utc).isoformat()
    product["state"] = "intake"
    products.append(product)
    _save(products)
    return product


def get_product(product_id):
    products = _load()
    for p in products:
        if p.get("id") == product_id:
            return p
    return None


def list_products(state=None):
    products = _load()
    if state:
        return [p for p in products if p.get("state") == state]
    return products


def update_product(product_id, updates):
    products = _load()
    for p in products:
        if p.get("id") == product_id:
            p.update(updates)
            p["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save(products)
            return p
    return None
