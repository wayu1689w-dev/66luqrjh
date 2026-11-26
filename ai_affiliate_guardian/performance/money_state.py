"""Money State — UNKNOWN ≠ 0, ESTIMATE ≠ CONFIRMED, CONFIRMED ≠ PAID"""

from ..core.state_machine import MoneyState


def classify_money(amount, evidence_level):
    if amount is None or amount == 0:
        if evidence_level == "unknown":
            return MoneyState.UNKNOWN, "ยังไม่ทราบยอด — ห้ามนับเป็น 0"
        return MoneyState.UNKNOWN, "ยอด 0 แต่ยังไม่ยืนยัน"
    if evidence_level == "estimate":
        return MoneyState.ESTIMATED, f"ประมาณ {amount} บาท — ยังไม่ยืนยัน"
    if evidence_level == "confirmed":
        return MoneyState.CONFIRMED, f"ยืนยัน {amount} บาท — ยังไม่จ่าย"
    if evidence_level == "paid":
        return MoneyState.PAID, f"จ่ายแล้ว {amount} บาท"
    return MoneyState.UNKNOWN, f"ไม่ทราบสถานะ — {amount} บาท"
