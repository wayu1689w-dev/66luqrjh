"""Emergency Lockdown — overrides all modules"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))


class EmergencyLockdown:
    def __init__(self):
        self._active = True
        self._history = []
        self._blocked_modules = set()

    @property
    def active(self) -> bool:
        return self._active

    def activate(self, reason: str, triggered_by: str = "system") -> dict:
        self._active = True
        entry = {
            "action": "LOCKDOWN_ACTIVATED",
            "reason": reason,
            "triggered_by": triggered_by,
            "timestamp": datetime.now(TZ_BKK).isoformat(),
        }
        self._history.append(entry)
        return entry

    def deactivate(self, owner_confirmation: str) -> dict:
        if owner_confirmation != "OWNER_CONFIRMED":
            return {"deactivated": False, "reason": "Owner confirmation required"}
        self._active = False
        entry = {
            "action": "LOCKDOWN_DEACTIVATED",
            "timestamp": datetime.now(TZ_BKK).isoformat(),
        }
        self._history.append(entry)
        return entry

    def block_module(self, module_name: str, reason: str) -> dict:
        self._blocked_modules.add(module_name)
        return {"blocked": module_name, "reason": reason}

    def is_module_blocked(self, module_name: str) -> bool:
        return self._active or module_name in self._blocked_modules

    def can_execute(self, action: str) -> dict:
        if self._active:
            return {
                "allowed": False,
                "reason": f"Emergency lockdown active — '{action}' denied",
            }
        return {"allowed": True}

    def get_history(self) -> list:
        return list(self._history)

    def get_status(self) -> dict:
        return {
            "active": self._active,
            "blocked_modules": sorted(self._blocked_modules),
            "history_count": len(self._history),
        }
