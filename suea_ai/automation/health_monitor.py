"""Health Monitor — ตรวจสุขภาพทุก module และ connector"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

STATUS_HEALTHY = "HEALTHY"
STATUS_DEGRADED = "DEGRADED"
STATUS_DOWN = "DOWN"
STATUS_UNKNOWN = "UNKNOWN"


class HealthMonitor:
    def __init__(self):
        self._modules: dict[str, dict] = {}
        self._alerts: list[dict] = []

    def register_module(self, module_id: str, name: str = "") -> dict:
        self._modules[module_id] = {
            "module_id": module_id,
            "name": name or module_id,
            "status": STATUS_UNKNOWN,
            "last_check": None,
            "consecutive_failures": 0,
            "total_checks": 0,
            "total_failures": 0,
        }
        return {"ok": True, "module_id": module_id}

    def report_healthy(self, module_id: str) -> dict:
        mod = self._modules.get(module_id)
        if not mod:
            return {"ok": False, "error": "not_registered"}
        mod["status"] = STATUS_HEALTHY
        mod["last_check"] = datetime.now(TZ_BKK).isoformat()
        mod["consecutive_failures"] = 0
        mod["total_checks"] += 1
        return {"ok": True, "module_id": module_id, "status": STATUS_HEALTHY}

    def report_failure(self, module_id: str, detail: str = "") -> dict:
        mod = self._modules.get(module_id)
        if not mod:
            return {"ok": False, "error": "not_registered"}
        mod["consecutive_failures"] += 1
        mod["total_failures"] += 1
        mod["total_checks"] += 1
        mod["last_check"] = datetime.now(TZ_BKK).isoformat()

        if mod["consecutive_failures"] >= 3:
            mod["status"] = STATUS_DOWN
        else:
            mod["status"] = STATUS_DEGRADED

        alert = {
            "module_id": module_id,
            "status": mod["status"],
            "consecutive_failures": mod["consecutive_failures"],
            "detail": detail,
            "timestamp": mod["last_check"],
        }
        self._alerts.append(alert)
        return {"ok": True, **alert}

    def get_status(self, module_id: str) -> dict | None:
        return self._modules.get(module_id)

    def get_all_status(self) -> list[dict]:
        return list(self._modules.values())

    def get_down_modules(self) -> list[dict]:
        return [m for m in self._modules.values() if m["status"] == STATUS_DOWN]

    def get_degraded_modules(self) -> list[dict]:
        return [m for m in self._modules.values() if m["status"] == STATUS_DEGRADED]

    def get_alerts(self, limit: int = 50) -> list[dict]:
        return self._alerts[-limit:]

    def overall_health(self) -> dict:
        total = len(self._modules)
        if total == 0:
            return {"status": STATUS_UNKNOWN, "modules": 0}
        healthy = sum(1 for m in self._modules.values()
                      if m["status"] == STATUS_HEALTHY)
        down = sum(1 for m in self._modules.values()
                   if m["status"] == STATUS_DOWN)
        if down > 0:
            overall = STATUS_DOWN
        elif healthy < total:
            overall = STATUS_DEGRADED
        else:
            overall = STATUS_HEALTHY
        return {
            "status": overall,
            "modules": total,
            "healthy": healthy,
            "degraded": total - healthy - down,
            "down": down,
        }

    def stats(self) -> dict:
        return {
            "total_modules": len(self._modules),
            "total_alerts": len(self._alerts),
            **self.overall_health(),
        }
