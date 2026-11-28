"""Sales Growth Analyzer — วิเคราะห์การเติบโตของยอดขาย"""


def growth_rate(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0 if current == 0 else 100.0
    return round((current - previous) / previous * 100, 2)


def moving_average(values: list[float], window: int = 7) -> list[float]:
    if not values or window <= 0:
        return []
    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        segment = values[start:i + 1]
        result.append(round(sum(segment) / len(segment), 2))
    return result


def analyze_sales(daily_sales: list[dict]) -> dict:
    if not daily_sales:
        return {"total_days": 0, "total_revenue": 0, "avg_daily": 0,
                "growth_pct": 0, "best_day": None}
    revenues = [d.get("revenue", 0) for d in daily_sales]
    total = sum(revenues)
    avg = round(total / len(revenues), 2)

    if len(revenues) >= 2:
        mid = len(revenues) // 2
        first_half = sum(revenues[:mid])
        second_half = sum(revenues[mid:])
        g = growth_rate(second_half, first_half)
    else:
        g = 0.0

    best = max(daily_sales, key=lambda d: d.get("revenue", 0))
    return {
        "total_days": len(daily_sales),
        "total_revenue": round(total, 2),
        "avg_daily": avg,
        "growth_pct": g,
        "best_day": best.get("date", "unknown"),
    }
