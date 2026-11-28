"""Watchdog — ตรวจสอบ heartbeat และสถานะโมดูล"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

DEFAULT_HEARTBEAT_INTERVAL = 30


class Watchdog:
    def __init__(self, heartbeat_interval: int = DEFAULT_HEARTBEAT_INTERVAL):
        self._interval = heartbeat_interval
        self._heartbeats: dict[str, str] = {}
        self._alerts: list[dict] = []

    def heartbeat(self, module_name: str) -> dict:
        ts = datetime.now(TZ_BKK).isoformat()
        self._heartbeats[module_name] = ts
        return {"module": module_name, "heartbeat": ts}

    def check_all(self) -> dict:
        now = datetime.now(TZ_BKK)
        healthy = []
        stale = []
        for module, last_ts in self._heartbeats.items():
            last = datetime.fromisoformat(last_ts)
            age_seconds = (now - last).total_seconds()
            if age_seconds > self._interval * 3:
                stale.append({"module": module, "last_heartbeat": last_ts,
                              "age_seconds": round(age_seconds)})
            else:
                healthy.append(module)
        if stale:
            alert = {
                "type": "STALE_HEARTBEAT",
                "modules": [s["module"] for s in stale],
                "timestamp": now.isoformat(),
            }
            self._alerts.append(alert)
        return {"healthy": healthy, "stale": stale, "checked_at": now.isoformat()}

    def get_alerts(self, limit: int = 20) -> list:
        return self._alerts[-limit:]

    def get_module_status(self, module_name: str) -> dict:
        ts = self._heartbeats.get(module_name)
        if not ts:
            return {"module": module_name, "status": "UNKNOWN"}
        now = datetime.now(TZ_BKK)
        age = (now - datetime.fromisoformat(ts)).total_seconds()
        status = "HEALTHY" if age <= self._interval * 3 else "STALE"
        return {"module": module_name, "status": status,
                "last_heartbeat": ts, "age_seconds": round(age)}

    def registered_modules(self) -> list:
        return sorted(self._heartbeats.keys())
