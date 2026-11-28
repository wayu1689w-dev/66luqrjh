"""Security Guardian — 5-layer defense for SUEA_AI_MASTER"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

BLOCKED_ACTIONS = frozenset({
    "PUBLISH", "SEND", "ADS_WRITE", "AD_CREATE",
    "COMMERCE_WRITE", "OAUTH_GRANT", "BILLING_ENABLE",
    "PERMISSION_CHANGE", "EXTERNAL_SHARE", "SOURCE_WRITE",
    "QUOTA_BYPASS", "AUTO_SPEND", "DELETE_ORIGINAL",
})

RISK_LEVELS = {"R1": "low", "R2": "medium", "R3": "high", "R4": "critical", "R5": "emergency"}


class SecurityGuardian:
    def __init__(self):
        self._lockdown = True
        self._audit = []

    @property
    def is_lockdown(self) -> bool:
        return self._lockdown

    def check_action(self, action: str, actor: str = "system") -> dict:
        ts = datetime.now(TZ_BKK).isoformat()
        upper = action.upper()
        allowed = upper not in BLOCKED_ACTIONS
        result = {
            "action": action,
            "allowed": allowed,
            "actor": actor,
            "lockdown": self._lockdown,
            "timestamp": ts,
        }
        if not allowed:
            result["reason"] = f"Blocked by LOCKDOWN policy: {upper}"
            result["risk"] = "R4"
        self._audit.append(result)
        return result

    def check_permission(self, actor: str, resource: str, operation: str) -> dict:
        if self._lockdown and operation.upper() in ("WRITE", "DELETE", "EXECUTE"):
            return {
                "allowed": False,
                "reason": f"LOCKDOWN: {operation} on {resource} denied for {actor}",
            }
        if operation.upper() == "READ":
            return {"allowed": True}
        return {"allowed": False, "reason": "Owner approval required"}

    def emergency_lockdown(self, reason: str) -> dict:
        self._lockdown = True
        entry = {
            "event": "EMERGENCY_LOCKDOWN",
            "reason": reason,
            "timestamp": datetime.now(TZ_BKK).isoformat(),
        }
        self._audit.append(entry)
        return entry

    def release_lockdown(self, owner_token: str) -> dict:
        if owner_token != "OWNER_CONFIRMED":
            return {"released": False, "reason": "Invalid owner confirmation"}
        self._lockdown = False
        return {"released": True, "timestamp": datetime.now(TZ_BKK).isoformat()}

    def get_audit_log(self, limit: int = 50) -> list:
        return self._audit[-limit:]

    def classify_risk(self, action: str) -> str:
        upper = action.upper()
        if upper in ("BILLING_ENABLE", "DELETE_ORIGINAL", "QUOTA_BYPASS"):
            return "R5"
        if upper in BLOCKED_ACTIONS:
            return "R4"
        if upper in ("EXPORT", "BACKUP", "REPORT"):
            return "R2"
        return "R1"
