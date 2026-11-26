"""เสือ 945 — HOLD รอยืนยัน"""

CHANNEL_ID = "ch_suea954"
CHANNEL_NAME = "เสือ 945"
CATEGORY = "hold"
ROLE = "reserve"
STATUS = "HOLD"

NOTE = "รอยืนยันว่าเป็น 945 หรือ 954"


def can_accept_product(product):
    return False, f"ช่อง {CHANNEL_NAME} สถานะ HOLD — ไม่รับงานจนกว่าจะเปิด"


def script_guidelines():
    return {
        "channel": CHANNEL_NAME,
        "tone": None,
        "rules": ["ช่องนี้ HOLD — ไม่สร้างสคริปต์"],
    }
