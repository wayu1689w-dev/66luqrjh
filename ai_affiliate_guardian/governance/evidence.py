"""Evidence Governance — กฎหลักฐาน"""


RULES = {
    "UNKNOWN_IS_NOT_ZERO": "ยังไม่รู้ ≠ 0 — ห้ามนับเป็นศูนย์",
    "ESTIMATE_IS_NOT_CONFIRMED": "ประมาณ ≠ ยืนยัน — ห้ามใช้ตัวเลขประมาณเสมือนจริง",
    "CONFIRMED_IS_NOT_PAID": "ยืนยัน ≠ จ่ายแล้ว — ห้ามนับรายได้ที่ยังไม่เข้าบัญชี",
}


def validate_evidence_claim(level, assertion):
    if level == "unknown" and assertion in ("zero", "none", "0"):
        return False, RULES["UNKNOWN_IS_NOT_ZERO"]
    if level == "estimate" and assertion == "confirmed":
        return False, RULES["ESTIMATE_IS_NOT_CONFIRMED"]
    if level == "confirmed" and assertion == "paid":
        return False, RULES["CONFIRMED_IS_NOT_PAID"]
    return True, "ถูกต้อง"
