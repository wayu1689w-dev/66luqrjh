"""Ads Profit Analyzer"""


def compute_roas(revenue: float, spend: float) -> float:
    if spend == 0:
        return 0.0
    return round(revenue / spend, 2)


def compute_cpc(spend: float, clicks: int) -> float:
    if clicks == 0:
        return 0.0
    return round(spend / clicks, 2)


def analyze_ads(ads: list[dict]) -> dict:
    if not ads:
        return {"total": 0, "spend": 0, "revenue": 0, "profit": 0, "roas": 0}
    total_spend = sum(a.get("spend", 0) for a in ads)
    total_revenue = sum(a.get("revenue", 0) for a in ads)
    total_clicks = sum(a.get("clicks", 0) for a in ads)
    return {
        "total": len(ads),
        "spend": round(total_spend, 2),
        "revenue": round(total_revenue, 2),
        "profit": round(total_revenue - total_spend, 2),
        "roas": compute_roas(total_revenue, total_spend),
        "cpc": compute_cpc(total_spend, total_clicks),
    }
