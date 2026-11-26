"""Channel Isolation — บังคับแยกช่องสมบูรณ์"""

from . import monster_great, suea2992, suea954, review_good

CHANNEL_MAP = {
    "ch_monster_great": monster_great,
    "ch_suea2992": suea2992,
    "ch_suea954": suea954,
    "ch_review_good": review_good,
}


def get_channel_module(channel_id):
    return CHANNEL_MAP.get(channel_id)


def route_product(product, channel_id):
    module = get_channel_module(channel_id)
    if not module:
        return False, f"ไม่พบช่อง {channel_id}"
    return module.can_accept_product(product)


def check_cross_channel(content_id, from_channel, to_channel):
    if from_channel == to_channel:
        return True, "ช่องเดียวกัน"
    return False, f"ห้ามใช้คอนเทนต์ข้ามช่อง ({from_channel} → {to_channel})"


def get_all_guidelines():
    result = {}
    for ch_id, module in CHANNEL_MAP.items():
        result[ch_id] = module.script_guidelines()
    return result
