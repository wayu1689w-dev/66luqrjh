"""Product Eligibility — ตรวจสอบว่าสินค้าผ่านเกณฑ์หรือไม่"""

import yaml
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "config" / "product_rules.yaml"


def _load_rules():
    with open(RULES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_eligibility(product):
    rules = _load_rules()
    forbidden = rules["eligibility"].get("forbidden", [])
    category = product.get("product_category", "")
    for f in forbidden:
        if f in category:
            return False, f"สินค้าต้องห้าม: {f}"
    required = rules["eligibility"]["required_fields"]
    missing = [field for field in required if not product.get(field)]
    if missing:
        return False, f"ข้อมูลไม่ครบ: {', '.join(missing)}"
    return True, "ผ่านเกณฑ์"
