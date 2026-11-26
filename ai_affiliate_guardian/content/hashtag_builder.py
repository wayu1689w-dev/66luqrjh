"""Hashtag Builder — สร้างแฮชแท็กตามหมวด"""

BASE_TAGS = ["#affiliate", "#รีวิว", "#ของดี", "#tiktokshop"]

CATEGORY_TAGS = {
    "food": ["#อาหาร", "#กินเที่ยว", "#foodtiktok", "#อร่อย"],
    "product_review": ["#รีวิวสินค้า", "#ของดีบอกต่อ", "#shopปัง"],
}


def build_hashtags(channel_category, extra_tags=None):
    tags = list(BASE_TAGS)
    tags.extend(CATEGORY_TAGS.get(channel_category, []))
    if extra_tags:
        tags.extend(extra_tags)
    seen = set()
    unique = []
    for t in tags:
        lower = t.lower()
        if lower not in seen:
            seen.add(lower)
            unique.append(t)
    return unique
