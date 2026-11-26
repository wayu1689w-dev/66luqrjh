"""Product Ranking — จัดอันดับสินค้าตามน้ำหนักที่กำหนด"""

import yaml
from pathlib import Path

RULES_PATH = Path(__file__).parent.parent / "config" / "product_rules.yaml"


def _load_weights():
    with open(RULES_PATH, encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    return rules["ranking"]["weights"], rules["ranking"]["min_score"]


def score_product(product):
    weights, _ = _load_weights()
    score = 0.0
    for field, weight in weights.items():
        value = product.get(field, 0)
        if isinstance(value, (int, float)):
            score += value * weight
    return round(score, 4)


def rank_products(products):
    _, min_score = _load_weights()
    scored = []
    for p in products:
        s = score_product(p)
        if s >= min_score:
            scored.append({**p, "rank_score": s})
    scored.sort(key=lambda x: x["rank_score"], reverse=True)
    return scored
