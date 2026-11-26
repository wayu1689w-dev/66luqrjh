"""Product Intake — รับสินค้าเข้าระบบ ตรวจข้อมูลเบื้องต้น"""

import yaml
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "config" / "product_rules.yaml"


def _load_rules():
    with open(RULES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_intake(product):
    rules = _load_rules()
    required = rules["eligibility"]["required_fields"]
    missing = [f for f in required if not product.get(f)]
    if missing:
        return False, f"ขาดข้อมูล: {', '.join(missing)}"
    return True, "ข้อมูลครบ"


def intake_product(product):
    valid, message = validate_intake(product)
    if not valid:
        return {"accepted": False, "reason": message}
    product["state"] = "intake"
    return {"accepted": True, "product": product}
