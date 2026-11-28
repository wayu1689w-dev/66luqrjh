"""Connection Pool — จำกัดการเชื่อมต่อพร้อมกันตามทรัพยากร"""

import threading
from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

DEFAULT_MAX_CONNECTIONS = 50


class ConnectionPool:
    def __init__(self, max_connections: int = DEFAULT_MAX_CONNECTIONS):
        self._max = max_connections
        self._active: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._history: list[dict] = []

    @property
    def active_count(self) -> int:
        return len(self._active)

    @property
    def available(self) -> int:
        return self._max - len(self._active)

    def acquire(self, connector_id: str, purpose: str = "") -> dict:
        with self._lock:
            if connector_id in self._active:
                return {"ok": True, "reused": True, "connector_id": connector_id}
            if len(self._active) >= self._max:
                return {"ok": False, "error": "pool_exhausted",
                        "active": len(self._active), "max": self._max}
            self._active[connector_id] = {
                "purpose": purpose,
                "acquired_at": datetime.now(TZ_BKK).isoformat(),
            }
            return {"ok": True, "reused": False, "connector_id": connector_id,
                    "active": len(self._active)}

    def release(self, connector_id: str) -> dict:
        with self._lock:
            if connector_id not in self._active:
                return {"ok": False, "error": "not_active"}
            info = self._active.pop(connector_id)
            self._history.append({
                "connector_id": connector_id,
                "released_at": datetime.now(TZ_BKK).isoformat(),
                **info,
            })
            return {"ok": True, "connector_id": connector_id}

    def release_all(self) -> dict:
        with self._lock:
            count = len(self._active)
            self._active.clear()
            return {"released": count}

    def status(self) -> dict:
        return {
            "active": len(self._active),
            "max": self._max,
            "available": self._max - len(self._active),
            "connections": {k: v for k, v in self._active.items()},
        }

    def is_connected(self, connector_id: str) -> bool:
        return connector_id in self._active
