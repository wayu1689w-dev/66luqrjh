"""Permissions — READ auto, WRITE policy, HIGH_IMPACT human"""


LEVELS = {
    "READ": "auto",
    "WRITE": "policy",
    "HIGH_IMPACT": "human_approval",
}


def check_permission(action_level):
    mode = LEVELS.get(action_level, "human_approval")
    if mode == "auto":
        return True, "อนุญาตอัตโนมัติ"
    if mode == "policy":
        return True, "อนุญาตตามนโยบาย — ต้องตรวจสอบก่อน"
    return False, "ต้องได้รับอนุมัติจากเจ้าของ"
