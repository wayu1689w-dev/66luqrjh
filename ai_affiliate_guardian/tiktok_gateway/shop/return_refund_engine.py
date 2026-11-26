"""Return & Refund Engine — TikTok Shop Return/Refund API"""

SCOPES = ["return.read", "return.write"]


def get_status():
    return {"engine": "return_refund", "documented": True, "authorized": False, "connected": False}
