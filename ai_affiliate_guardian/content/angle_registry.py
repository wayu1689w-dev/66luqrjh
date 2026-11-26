"""Angle Registry — มุมนำเสนอสินค้าแต่ละช่อง"""


ANGLES = {
    "taste_test": {"label": "ชิมสด", "channels": ["ch_monster_great", "ch_suea2992"]},
    "price_compare": {"label": "เทียบราคา", "channels": ["ch_monster_great", "ch_suea2992"]},
    "unboxing": {"label": "แกะกล่อง", "channels": ["ch_review_good"]},
    "problem_solve": {"label": "แก้ปัญหา", "channels": ["ch_review_good"]},
    "daily_use": {"label": "ใช้ในชีวิตจริง", "channels": ["ch_review_good"]},
    "before_after": {"label": "ก่อน-หลัง", "channels": ["ch_review_good"]},
}


def get_angles_for_channel(channel_id):
    return {k: v for k, v in ANGLES.items() if channel_id in v["channels"]}


def suggest_angle(product, channel_id):
    available = get_angles_for_channel(channel_id)
    if not available:
        return None
    return list(available.keys())[0]
