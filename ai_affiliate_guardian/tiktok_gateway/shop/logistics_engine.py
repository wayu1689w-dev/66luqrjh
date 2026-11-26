"""Logistics Engine — TikTok Shop Logistics API"""

SCOPES = ["logistics.read"]


def get_status():
    return {"engine": "logistics", "documented": True, "authorized": False, "connected": False}
