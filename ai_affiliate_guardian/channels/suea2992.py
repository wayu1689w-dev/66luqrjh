"""เสือ 2992 — ช่องรอง อาหาร + ร้านยิงแอด"""

CHANNEL_ID = "ch_suea2992"
CHANNEL_NAME = "เสือ 2992"
CATEGORY = "food"
ROLE = "secondary_food"

ALLOWED_CATEGORIES = ["อาหาร", "เครื่องดื่ม", "ขนม", "ร้านอาหาร"]
TONE = "จริงจัง รีวิวละเอียด"


def can_accept_product(product):
    cat = product.get("product_category", "")
    for allowed in ALLOWED_CATEGORIES:
        if allowed in cat:
            return True, f"รับได้ — หมวด {cat}"
    return False, f"ไม่ตรงหมวด — {cat} ไม่ใช่อาหาร"


def script_guidelines():
    return {
        "channel": CHANNEL_NAME,
        "tone": TONE,
        "rules": [
            "เปิดด้วยคำถามชวนสงสัย",
            "รีวิวละเอียด ราคา รสชาติ ปริมาณ",
            "เปรียบเทียบกับของคู่แข่งได้",
            "ปิดด้วย CTA + ลิงก์",
        ],
    }
