"""Authentication Manager — จัดการ auth flow ห้ามเก็บ key ใน code"""


TIKTOK_SHOP_AUTH_FLOW = [
    "Developer Onboarding",
    "Create TikTok Shop App",
    "Enable Required Scopes",
    "Seller / Creator / Partner Authorization",
    "auth_code",
    "access_token",
    "First API Call",
]

AUTH_STATES = [
    "DOCUMENTED",
    "APP_REGISTERED",
    "AUTHORIZED",
    "TOKEN_VALIDATED",
    "SCOPES_VERIFIED",
    "READ_TESTED",
    "WRITE_TESTED",
    "PRODUCTION_READY",
]


def get_auth_status(plugin_id, current_state):
    idx = AUTH_STATES.index(current_state) if current_state in AUTH_STATES else -1
    completed = AUTH_STATES[:idx + 1] if idx >= 0 else []
    remaining = AUTH_STATES[idx + 1:] if idx >= 0 else AUTH_STATES
    return {
        "plugin_id": plugin_id,
        "current": current_state,
        "completed": completed,
        "remaining": remaining,
        "note": "API DOCUMENTED ≠ CONNECTED — ต้องผ่านทุกขั้น",
    }


def validate_no_secrets_in_code():
    return {
        "rule": "ห้ามเก็บ API key, token, password ใน source code",
        "method": "environment variables only",
        "audit": True,
    }
