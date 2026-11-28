"""Product Ranking Analyzer"""


def compute_score(gmv: float, orders: int, conversion: float, commission: float) -> float:
    return round((gmv * 0.3) + (orders * 0.3) + (conversion * 0.2) + (commission * 0.2), 2)


def rank_products(products: list[dict], top: int = 10) -> list[dict]:
    for p in products:
        if "score" not in p or not p["score"]:
            p["score"] = compute_score(
                p.get("gmv", 0), p.get("orders", 0),
                p.get("conversion_rate", 0), p.get("commission_rate", 0),
            )
    ranked = sorted(products, key=lambda x: x.get("score", 0), reverse=True)
    return ranked[:top]


def estimate_profit(gmv: float, commission_rate: float) -> float:
    return round(gmv * commission_rate / 100, 2)
