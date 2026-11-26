"""Fulfillment Engine — TikTok Shop Fulfillment API"""

SCOPES = ["fulfillment.read", "fulfillment.write"]


def get_status():
    return {"engine": "fulfillment", "documented": True, "authorized": False, "connected": False}
