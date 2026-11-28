"""Permission Control — RBAC + Owner Approval Gate"""

ROLES = {
    "owner": {"read", "write", "execute", "admin", "approve"},
    "operator": {"read", "execute"},
    "viewer": {"read"},
    "plugin": {"read", "execute_limited"},
    "ai_agent": {"read", "report", "ack"},
}

OWNER_ONLY_ACTIONS = frozenset({
    "approve", "admin", "billing", "lockdown_release",
    "permission_change", "plugin_install", "credential_manage",
})


def check_permission(role: str, action: str) -> dict:
    perms = ROLES.get(role, set())
    if action in OWNER_ONLY_ACTIONS:
        return {
            "allowed": role == "owner",
            "reason": f"'{action}' requires owner role" if role != "owner" else "granted",
        }
    return {
        "allowed": action in perms,
        "reason": "granted" if action in perms else f"Role '{role}' lacks '{action}'",
    }


def list_roles() -> dict:
    return {r: sorted(p) for r, p in ROLES.items()}


def get_role_permissions(role: str) -> set:
    return ROLES.get(role, set())
