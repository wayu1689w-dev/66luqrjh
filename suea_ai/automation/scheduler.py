"""Scheduler — จัดตารางงานอัตโนมัติ (heartbeat, backup, report, health check)"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))


class ScheduledTask:
    __slots__ = ("task_id", "name", "interval_seconds", "enabled",
                 "last_run", "next_run", "run_count")

    def __init__(self, task_id: str, name: str, interval_seconds: int,
                 enabled: bool = True):
        self.task_id = task_id
        self.name = name
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self.last_run = None
        self.next_run = None
        self.run_count = 0

    def to_dict(self) -> dict:
        return {s: getattr(self, s) for s in self.__slots__}


class Scheduler:
    def __init__(self):
        self._tasks: dict[str, ScheduledTask] = {}
        self._log: list[dict] = []
        self._init_defaults()

    def _init_defaults(self):
        defaults = [
            ("heartbeat", "Heartbeat Check", 30),
            ("backup", "Auto Backup", 1800),
            ("report", "Status Report", 1800),
            ("health", "Health Monitor", 60),
            ("kpi", "KPI Enforcement", 300),
            ("ack_timeout", "ACK Timeout Check", 120),
            ("quota_reset", "Quota Daily Reset", 86400),
        ]
        for tid, name, interval in defaults:
            self._tasks[tid] = ScheduledTask(tid, name, interval)

    def add_task(self, task_id: str, name: str, interval_seconds: int) -> dict:
        if task_id in self._tasks:
            return {"ok": False, "error": "duplicate"}
        if interval_seconds < 10:
            return {"ok": False, "error": "interval too short (min 10s)"}
        self._tasks[task_id] = ScheduledTask(task_id, name, interval_seconds)
        return {"ok": True, "task_id": task_id}

    def remove_task(self, task_id: str) -> dict:
        if task_id not in self._tasks:
            return {"ok": False, "error": "not_found"}
        del self._tasks[task_id]
        return {"ok": True, "task_id": task_id}

    def enable(self, task_id: str) -> dict:
        task = self._tasks.get(task_id)
        if not task:
            return {"ok": False, "error": "not_found"}
        task.enabled = True
        return {"ok": True, "task_id": task_id, "enabled": True}

    def disable(self, task_id: str) -> dict:
        task = self._tasks.get(task_id)
        if not task:
            return {"ok": False, "error": "not_found"}
        task.enabled = False
        return {"ok": True, "task_id": task_id, "enabled": False}

    def mark_run(self, task_id: str) -> dict:
        task = self._tasks.get(task_id)
        if not task:
            return {"ok": False, "error": "not_found"}
        ts = datetime.now(TZ_BKK).isoformat()
        task.last_run = ts
        task.run_count += 1
        self._log.append({"task_id": task_id, "ran_at": ts,
                          "run_count": task.run_count})
        return {"ok": True, "task_id": task_id, "run_count": task.run_count}

    def get_task(self, task_id: str) -> dict | None:
        task = self._tasks.get(task_id)
        return task.to_dict() if task else None

    def list_tasks(self) -> list[dict]:
        return [t.to_dict() for t in self._tasks.values()]

    def list_enabled(self) -> list[dict]:
        return [t.to_dict() for t in self._tasks.values() if t.enabled]

    def get_log(self, limit: int = 50) -> list:
        return self._log[-limit:]

    def stats(self) -> dict:
        total = len(self._tasks)
        enabled = sum(1 for t in self._tasks.values() if t.enabled)
        total_runs = sum(t.run_count for t in self._tasks.values())
        return {
            "total_tasks": total,
            "enabled": enabled,
            "disabled": total - enabled,
            "total_runs": total_runs,
        }
