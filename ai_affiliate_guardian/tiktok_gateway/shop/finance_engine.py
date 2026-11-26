"""Finance Engine — TikTok Shop Finance API"""

SCOPES = ["finance.read"]


def get_status():
    return {"engine": "finance", "documented": True, "authorized": False, "connected": False}
