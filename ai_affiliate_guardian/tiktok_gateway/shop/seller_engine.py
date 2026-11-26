"""Seller Engine — TikTok Shop Seller API"""

SCOPES = ["seller.read"]


def get_status():
    return {"engine": "seller", "documented": True, "authorized": False, "connected": False}
