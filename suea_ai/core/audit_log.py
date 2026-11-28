"""Audit Log — บันทึกทุก action ในระบบ SUEA_AI_MASTER"""

from datetime import datetime, timezone, timedelta
import threading

TZ_BKK = timezone(timedelta(hours=7))
MAX_LOG_SIZE = 50000


class AuditLog:
    def __init__(self, max_size: int = MAX_LOG_SIZE):
        self._entries: list[dict] = []
        self._max_size = max_size
        self._lock = threading.Lock()

    def log(self, action: str, module: str, actor: str = "system",
            detail: str = "", risk: str = "R1") -> dict:
        entry = {
            "id": len(self._entries) + 1,
            "action": action,
            "module": module,
            "actor": actor,
            "detail": detail,
            "risk": risk,
            "timestamp": datetime.now(TZ_BKK).isoformat(),
        }
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max_size:
                self._entries = self._entries[-self._max_size:]
        return entry

    def query(self, module: str = "", action: str = "", actor: str = "",
              risk: str = "", limit: int = 100) -> list:
        results = self._entries
        if module:
            results = [e for e in results if e["module"] == module]
        if action:
            results = [e for e in results if e["action"] == action]
        if actor:
            results = [e for e in results if e["actor"] == actor]
        if risk:
            results = [e for e in results if e["risk"] == risk]
        return results[-limit:]

    def count(self) -> int:
        return len(self._entries)

    def stats(self) -> dict:
        by_module: dict[str, int] = {}
        by_action: dict[str, int] = {}
        by_risk: dict[str, int] = {}
        for e in self._entries:
            by_module[e["module"]] = by_module.get(e["module"], 0) + 1
            by_action[e["action"]] = by_action.get(e["action"], 0) + 1
            by_risk[e["risk"]] = by_risk.get(e["risk"], 0) + 1
        return {
            "total": len(self._entries),
            "by_module": by_module,
            "by_action": by_action,
            "by_risk": by_risk,
        }

    def recent(self, limit: int = 20) -> list:
        return self._entries[-limit:]

    def clear(self, before_id: int = 0) -> dict:
        if before_id <= 0:
            return {"ok": False, "error": "before_id must be > 0"}
        with self._lock:
            original = len(self._entries)
            self._entries = [e for e in self._entries if e["id"] >= before_id]
            removed = original - len(self._entries)
        return {"ok": True, "removed": removed, "remaining": len(self._entries)}
