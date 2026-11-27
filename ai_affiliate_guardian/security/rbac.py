"""RBAC — Role-Based Access Control — Spec v008 Area 1
4 ระดับสิทธิ์: owner > admin > editor > viewer
Permission Intersection: FINAL = USER ∩ PLUGIN ∩ CREDENTIAL ∩ RESOURCE ∩ SYSTEM_POLICY"""


ROLES = {
    "owner": {
        "level": 4,
        "permissions": [
            "read", "write", "delete", "approve", "admin",
            "kill_switch", "plugin_manage", "user_manage",
        ],
    },
    "admin": {
        "level": 3,
        "permissions": [
            "read", "write", "delete", "approve", "plugin_manage",
        ],
    },
    "editor": {
        "level": 2,
        "permissions": ["read", "write"],
    },
    "viewer": {
        "level": 1,
        "permissions": ["read"],
    },
}

DEFAULT_ROLE = "viewer"


def get_permissions(role: str) -> list[str]:
    r = ROLES.get(role, ROLES[DEFAULT_ROLE])
    return list(r["permissions"])


def has_permission(role: str, permission: str) -> bool:
    return permission in get_permissions(role)


def check_access(role: str, required_permission: str) -> tuple[bool, str]:
    if has_permission(role, required_permission):
        return True, f"อนุญาต: {role} มีสิทธิ์ {required_permission}"
    return False, f"ปฏิเสธ: {role} ไม่มีสิทธิ์ {required_permission}"


def role_level(role: str) -> int:
    return ROLES.get(role, ROLES[DEFAULT_ROLE])["level"]


def intersect_permissions(user_perms: list[str], plugin_perms: list[str],
                          resource_perms: list[str]) -> list[str]:
    return list(set(user_perms) & set(plugin_perms) & set(resource_perms))


def can_escalate(current_role: str, target_role: str) -> bool:
    return role_level(current_role) > role_level(target_role)
