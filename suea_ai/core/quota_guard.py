"""Quota Guard — ป้องกันการใช้เกิน API Quota"""

import threading
from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))


class QuotaGuard:
    def __init__(self):
        self._quotas: dict[str, dict] = {}
        self._usage: dict[str, int] = {}
        self._lock = threading.Lock()

    def set_quota(self, connector_id: str, daily_limit: int, hourly_limit: int = 0) -> dict:
        self._quotas[connector_id] = {
            "daily_limit": daily_limit,
            "hourly_limit": hourly_limit or daily_limit,
        }
        if connector_id not in self._usage:
            self._usage[connector_id] = 0
        return {"ok": True, "connector_id": connector_id}

    def check(self, connector_id: str) -> dict:
        quota = self._quotas.get(connector_id)
        if not quota:
            return {"allowed": True, "reason": "no_quota_set"}
        used = self._usage.get(connector_id, 0)
        if used >= quota["daily_limit"]:
            return {
                "allowed": False,
                "reason": f"Daily quota exceeded: {used}/{quota['daily_limit']}",
                "connector_id": connector_id,
            }
        return {
            "allowed": True,
            "used": used,
            "remaining": quota["daily_limit"] - used,
            "connector_id": connector_id,
        }

    def consume(self, connector_id: str, amount: int = 1) -> dict:
        check = self.check(connector_id)
        if not check["allowed"]:
            return check
        with self._lock:
            self._usage[connector_id] = self._usage.get(connector_id, 0) + amount
        return {"ok": True, "used": self._usage[connector_id]}

    def reset(self, connector_id: str) -> dict:
        self._usage[connector_id] = 0
        return {"ok": True, "connector_id": connector_id}

    def reset_all(self) -> dict:
        count = len(self._usage)
        self._usage.clear()
        return {"reset": count}

    def get_all_usage(self) -> dict:
        return {
            cid: {
                "used": self._usage.get(cid, 0),
                "limit": q["daily_limit"],
                "remaining": max(0, q["daily_limit"] - self._usage.get(cid, 0)),
            }
            for cid, q in self._quotas.items()
        }
