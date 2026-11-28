"""Recovery Worker — กู้คืนเมื่อระบบผิดพลาด"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))


class RecoveryWorker:
    def __init__(self, max_retries: int = 3):
        self._max_retries = max_retries
        self._recovery_log: list[dict] = []
        self._active_recoveries: dict[str, dict] = {}

    def start_recovery(self, module_name: str, error: str, severity: str = "medium") -> dict:
        if module_name in self._active_recoveries:
            return {"ok": False, "error": "recovery_already_active",
                    "module": module_name}
        entry = {
            "module": module_name,
            "error": error,
            "severity": severity,
            "attempt": 1,
            "status": "IN_PROGRESS",
            "started_at": datetime.now(TZ_BKK).isoformat(),
        }
        self._active_recoveries[module_name] = entry
        return {"ok": True, **entry}

    def retry(self, module_name: str) -> dict:
        rec = self._active_recoveries.get(module_name)
        if not rec:
            return {"ok": False, "error": "no_active_recovery"}
        if rec["attempt"] >= self._max_retries:
            rec["status"] = "FAILED"
            self._recovery_log.append(rec)
            del self._active_recoveries[module_name]
            return {"ok": False, "error": "max_retries_exceeded",
                    "module": module_name, "attempts": rec["attempt"]}
        rec["attempt"] += 1
        return {"ok": True, "module": module_name, "attempt": rec["attempt"]}

    def complete_recovery(self, module_name: str, success: bool) -> dict:
        rec = self._active_recoveries.get(module_name)
        if not rec:
            return {"ok": False, "error": "no_active_recovery"}
        rec["status"] = "RECOVERED" if success else "FAILED"
        rec["completed_at"] = datetime.now(TZ_BKK).isoformat()
        self._recovery_log.append(rec)
        del self._active_recoveries[module_name]
        return {"ok": True, "module": module_name, "status": rec["status"]}

    def get_active(self) -> list:
        return list(self._active_recoveries.values())

    def get_log(self, limit: int = 50) -> list:
        return self._recovery_log[-limit:]

    def stats(self) -> dict:
        recovered = sum(1 for r in self._recovery_log if r["status"] == "RECOVERED")
        failed = sum(1 for r in self._recovery_log if r["status"] == "FAILED")
        return {
            "active_recoveries": len(self._active_recoveries),
            "total_completed": len(self._recovery_log),
            "recovered": recovered,
            "failed": failed,
            "recovery_rate_pct": round(recovered / max(1, len(self._recovery_log)) * 100, 1),
        }
