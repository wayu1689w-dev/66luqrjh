"""Commercial Analysis — วิเคราะห์เชิงพาณิชย์"""


def revenue_summary(commissions):
    by_state = {}
    for c in commissions:
        s = c.get("state", "unknown")
        by_state[s] = by_state.get(s, 0) + c.get("amount", 0)
    return {
        "unknown": by_state.get("unknown", 0),
        "estimated": by_state.get("estimated", 0),
        "confirmed": by_state.get("confirmed", 0),
        "paid": by_state.get("paid", 0),
        "total_confirmed_or_paid": by_state.get("confirmed", 0) + by_state.get("paid", 0),
        "warning": "UNKNOWN ≠ 0, ESTIMATE ≠ CONFIRMED",
    }
