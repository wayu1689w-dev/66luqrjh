"""ชีวิตติดรีวิวของดี — ช่องรีวิวสินค้าทั่วไป"""

CHANNEL_ID = "ch_review_good"
CHANNEL_NAME = "ชีวิตติดรีวิวของดี"
CATEGORY = "product_review"
ROLE = "product_review"

ALLOWED_CATEGORIES = ["สินค้าทั่วไป", "เครื่องใช้", "อุปกรณ์", "ของใช้", "แกดเจ็ต"]
TONE = "เล่าให้ฟัง ใช้จริงบอกจริง"


def can_accept_product(product):
    return True, f"ช่องรีวิว — รับสินค้าทุกประเภท"


def script_guidelines():
    return {
        "channel": CHANNEL_NAME,
        "tone": TONE,
        "rules": [
            "เปิดด้วยปัญหาที่สินค้าแก้ได้",
            "ใช้จริง โชว์จริง ไม่โม้",
            "บอกข้อดีข้อเสีย",
            "ปิดด้วย CTA + ลิงก์ + ราคา",
        ],
    }
