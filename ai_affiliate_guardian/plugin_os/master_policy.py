"""Master Policy — สถานะจริงของระบบ ทุกอย่างปิดไว้"""

MASTER_POLICY = {
    "EXTERNAL_CONNECTIONS": "DISABLED",
    "PLUGIN_CONNECTIONS": "DISABLED",
    "MCP_CONNECTIONS": "DISABLED",
    "OAUTH_CONNECTIONS": "DISABLED",
    "AUTO_DISCOVER": True,
    "AUTO_CLASSIFY": True,
    "AUTO_CONNECT": False,
    "AUTO_OAUTH": False,
    "AUTO_PUBLISH": False,
    "AUTO_ADS_WRITE": False,
    "AUTO_COMMERCE_WRITE": False,
    "HUMAN_APPROVAL": True,
    "AUDIT_REQUIRED": True,
}


def get_policy():
    return dict(MASTER_POLICY)


def is_allowed(action):
    auto_key = f"AUTO_{action.upper()}"
    if auto_key in MASTER_POLICY:
        return MASTER_POLICY[auto_key], f"{auto_key} = {MASTER_POLICY[auto_key]}"
    return False, f"ไม่พบ policy สำหรับ {action} — ปิดเป็นค่าเริ่มต้น"


def get_checklist():
    return {
        "documented": {
            "TikTok Shop Documentation": True,
            "TikTok Shop Domains Identified": True,
            "TikTok Social MCP Documentation": True,
            "TikTok Business MCP Documentation": True,
            "Plugin Architecture": True,
            "Evidence Architecture": True,
            "Approval Architecture": True,
            "Audit Architecture": True,
            "Scalable Registry Design": True,
        },
        "not_done": {
            "TikTok Shop Authorized": False,
            "TikTok Shop Connected": False,
            "TikTok Social MCP Connected": False,
            "TikTok Business MCP Connected": False,
            "OAuth/Authorization Verified": False,
            "Permissions Verified": False,
            "Health Check Passed": False,
            "Production Ready": False,
        },
    }
