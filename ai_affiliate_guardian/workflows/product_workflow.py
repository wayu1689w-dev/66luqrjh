"""Product Workflow — ขั้นตอนสินค้าตั้งแต่รับเข้าถึงเผยแพร่"""

from ..products.intake import intake_product
from ..products.eligibility import check_eligibility
from ..products.duplicate_guard import check_duplicate
from ..products.ranking import score_product


def run_product_pipeline(product, existing_products=None):
    steps = []

    result = intake_product(product)
    steps.append({"step": "intake", "result": result})
    if not result["accepted"]:
        return {"completed": False, "steps": steps}

    is_dup, dup_id = check_duplicate(product, existing_products or [])
    steps.append({"step": "duplicate_check", "is_duplicate": is_dup, "duplicate_of": dup_id})
    if is_dup:
        return {"completed": False, "steps": steps, "reason": f"ซ้ำกับ {dup_id}"}

    eligible, msg = check_eligibility(product)
    steps.append({"step": "eligibility", "eligible": eligible, "message": msg})
    if not eligible:
        return {"completed": False, "steps": steps}

    score = score_product(product)
    steps.append({"step": "ranking", "score": score})

    return {"completed": True, "steps": steps, "score": score}
