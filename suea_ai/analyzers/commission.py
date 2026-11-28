"""Commission Analyzer — คำนวณค่าคอมมิชชัน Affiliate"""


def compute_commission(sale_amount: float, rate_pct: float) -> float:
    if sale_amount <= 0 or rate_pct <= 0:
        return 0.0
    return round(sale_amount * rate_pct / 100, 2)


def analyze_commissions(orders: list[dict]) -> dict:
    if not orders:
        return {"total_orders": 0, "total_sales": 0, "total_commission": 0,
                "avg_rate": 0, "avg_commission": 0}

    total_sales = sum(o.get("sale_amount", 0) for o in orders)
    total_commission = sum(
        compute_commission(o.get("sale_amount", 0), o.get("rate_pct", 0))
        for o in orders
    )
    rates = [o.get("rate_pct", 0) for o in orders if o.get("rate_pct", 0) > 0]
    avg_rate = round(sum(rates) / len(rates), 2) if rates else 0

    return {
        "total_orders": len(orders),
        "total_sales": round(total_sales, 2),
        "total_commission": round(total_commission, 2),
        "avg_rate": avg_rate,
        "avg_commission": round(total_commission / len(orders), 2),
    }


def top_products_by_commission(orders: list[dict], limit: int = 10) -> list[dict]:
    product_map: dict[str, float] = {}
    for o in orders:
        pid = o.get("product_id", "unknown")
        comm = compute_commission(o.get("sale_amount", 0), o.get("rate_pct", 0))
        product_map[pid] = product_map.get(pid, 0) + comm

    ranked = sorted(product_map.items(), key=lambda x: x[1], reverse=True)
    return [{"product_id": pid, "total_commission": round(c, 2)}
            for pid, c in ranked[:limit]]
