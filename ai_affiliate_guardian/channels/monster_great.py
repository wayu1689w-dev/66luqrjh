"""มอนสเตอร์ เกรท — ช่องหลัก อาหาร + ร้านยิงแอด"""

CHANNEL_ID = "ch_monster_great"
CHANNEL_NAME = "มอนสเตอร์ เกรท"
CATEGORY = "food"
ROLE = "primary_food"

ALLOWED_CATEGORIES = ["อาหาร", "เครื่องดื่ม", "ขนม", "ร้านอาหาร"]
TONE = "สนุก กินจริง โชว์จริง"


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
            "เปิดด้วย hook 3 วินาที",
            "โชว์สินค้าจริง กินจริง",
            "ห้ามอ้างสรรพคุณเกินจริง",
            "ปิดด้วย CTA + ลิงก์",
        ],
    }
