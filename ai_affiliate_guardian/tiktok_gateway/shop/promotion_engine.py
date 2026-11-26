"""Promotion Engine — TikTok Shop Promotion API"""

SCOPES = ["promotion.read", "promotion.write"]


def get_status():
    return {"engine": "promotion", "documented": True, "authorized": False, "connected": False}
