"""Plugin Lifecycle — จัดการสถานะปลั๊กอินตลอดอายุการใช้งาน

สถานะ:
  REGISTERED → ACTIVE → SUSPENDED → REMOVED
                ↑           ↓
                └───────────┘ (reactivate)
"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

VALID_STATES = ("REGISTERED", "ACTIVE", "SUSPENDED", "REMOVED")
TRANSITIONS = {
    "REGISTERED": ("ACTIVE", "REMOVED"),
    "ACTIVE": ("SUSPENDED", "REMOVED"),
    "SUSPENDED": ("ACTIVE", "REMOVED"),
    "REMOVED": (),
}


class PluginLifecycle:
    def __init__(self, registry):
        self._registry = registry
        self._history: list[dict] = []

    def activate(self, plugin_id: str) -> dict:
        return self._transition(plugin_id, "ACTIVE")

    def suspend(self, plugin_id: str, reason: str = "") -> dict:
        result = self._transition(plugin_id, "SUSPENDED")
        if result["ok"] and reason:
            result["reason"] = reason
        return result

    def remove(self, plugin_id: str) -> dict:
        return self._transition(plugin_id, "REMOVED")

    def reactivate(self, plugin_id: str) -> dict:
        return self._transition(plugin_id, "ACTIVE")

    def _transition(self, plugin_id: str, target: str) -> dict:
        entry = self._registry.get(plugin_id)
        if not entry:
            return {"ok": False, "error": "not_found", "plugin_id": plugin_id}

        current = entry["status"]
        allowed = TRANSITIONS.get(current, ())
        if target not in allowed:
            return {
                "ok": False,
                "error": "invalid_transition",
                "current": current,
                "target": target,
                "allowed": allowed,
            }

        self._registry.set_status(plugin_id, target)
        ts = datetime.now(TZ_BKK).isoformat()
        self._history.append({
            "plugin_id": plugin_id,
            "from": current,
            "to": target,
            "timestamp": ts,
        })
        return {"ok": True, "plugin_id": plugin_id, "status": target}

    def get_history(self, plugin_id: str = "", limit: int = 100) -> list:
        if plugin_id:
            return [h for h in self._history if h["plugin_id"] == plugin_id][-limit:]
        return self._history[-limit:]

    def bulk_suspend(self, plugin_ids: list[str], reason: str = "") -> dict:
        done = 0
        errors = []
        for pid in plugin_ids:
            result = self.suspend(pid, reason)
            if result["ok"]:
                done += 1
            else:
                errors.append({"plugin_id": pid, "error": result.get("error")})
        return {"suspended": done, "errors": errors}

    def bulk_activate(self, plugin_ids: list[str]) -> dict:
        done = 0
        errors = []
        for pid in plugin_ids:
            result = self.activate(pid)
            if result["ok"]:
                done += 1
            else:
                errors.append({"plugin_id": pid, "error": result.get("error")})
        return {"activated": done, "errors": errors}
