"""Kill Switch — Spec section 77
KILL หยุด Action แต่ไม่ลบ Audit/Evidence"""


SWITCHES = {
    "KILL_ALL_EXTERNAL": True,
    "KILL_PLUGIN": True,
    "KILL_MCP": True,
    "KILL_OAUTH": True,
    "KILL_PUBLISH": True,
    "KILL_ADS": True,
    "KILL_COMMERCE": True,
}


def get_state():
    return dict(SWITCHES)


def is_killed(switch_name):
    return SWITCHES.get(switch_name, False)


def activate(switch_name):
    if switch_name not in SWITCHES:
        raise ValueError(f"Unknown switch: {switch_name}")
    SWITCHES[switch_name] = True


def deactivate(switch_name):
    if switch_name not in SWITCHES:
        raise ValueError(f"Unknown switch: {switch_name}")
    SWITCHES[switch_name] = False


def kill_all():
    for k in SWITCHES:
        SWITCHES[k] = True


def reset_all():
    """Reset to safe defaults: all killed"""
    kill_all()


def check_action_blocked(action_type, external=False):
    """Return (blocked, reason) for a given action type."""
    if external and SWITCHES["KILL_ALL_EXTERNAL"]:
        return True, "KILL_ALL_EXTERNAL"

    mapping = {
        "PUBLISH": "KILL_PUBLISH",
        "SEND": "KILL_PUBLISH",
        "ADS": "KILL_ADS",
        "ADS_WRITE": "KILL_ADS",
        "AD_CREATE": "KILL_ADS",
        "COMMERCE": "KILL_COMMERCE",
        "COMMERCE_WRITE": "KILL_COMMERCE",
        "PLUGIN_EXECUTE": "KILL_PLUGIN",
        "MCP_CALL": "KILL_MCP",
        "OAUTH_GRANT": "KILL_OAUTH",
    }

    at = action_type.upper() if action_type else ""
    switch = mapping.get(at)
    if switch and SWITCHES.get(switch):
        return True, switch

    return False, None
