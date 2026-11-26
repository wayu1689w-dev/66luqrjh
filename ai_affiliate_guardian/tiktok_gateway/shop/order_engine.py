"""Order Engine — TikTok Shop Order API"""

SCOPES = ["order.read", "order.write"]


def get_status():
    return {"engine": "order", "documented": True, "authorized": False, "connected": False}
