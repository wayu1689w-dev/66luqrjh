"""TikTok Shop API Gateway — 10 API domains documented"""

APIS = {
    "product": {"documented": True, "authorized": False, "connected": False},
    "order": {"documented": True, "authorized": False, "connected": False},
    "fulfillment": {"documented": True, "authorized": False, "connected": False},
    "return_refund": {"documented": True, "authorized": False, "connected": False},
    "logistics": {"documented": True, "authorized": False, "connected": False},
    "promotion": {"documented": True, "authorized": False, "connected": False},
    "finance": {"documented": True, "authorized": False, "connected": False},
    "seller": {"documented": True, "authorized": False, "connected": False},
    "authorization": {"documented": True, "authorized": False, "connected": False},
    "events_webhooks": {"documented": True, "authorized": False, "connected": False},
}

AUTH_FLOW = [
    "DOCUMENTED",
    "APP_REGISTERED",
    "AUTHORIZED",
    "TOKEN_VALIDATED",
    "SCOPES_VERIFIED",
    "READ_TESTED",
    "WRITE_TESTED",
    "PRODUCTION_READY",
]


def get_status():
    return {
        "gateway": "tiktok_shop",
        "apis": APIS,
        "auth_state": "DOCUMENTED",
        "note": "API DOCUMENTED ≠ CONNECTED",
    }
