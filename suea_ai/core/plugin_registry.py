"""Plugin Registry — รองรับ 10,000 entries พร้อม lifecycle management"""

from datetime import datetime, timezone, timedelta
import threading

TZ_BKK = timezone(timedelta(hours=7))
MAX_CAPACITY = 10000


class PluginEntry:
    __slots__ = (
        "plugin_id", "name", "category", "provider",
        "status", "version", "capabilities",
        "requires_auth", "risk_level", "registered_at",
    )

    def __init__(self, plugin_id: str, name: str, category: str = "general",
                 provider: str = "unknown", capabilities: tuple = (),
                 requires_auth: bool = False, risk_level: str = "R1"):
        self.plugin_id = plugin_id
        self.name = name
        self.category = category
        self.provider = provider
        self.status = "REGISTERED"
        self.version = "1.0"
        self.capabilities = capabilities
        self.requires_auth = requires_auth
        self.risk_level = risk_level
        self.registered_at = datetime.now(TZ_BKK).isoformat()

    def to_dict(self) -> dict:
        return {s: getattr(self, s) for s in self.__slots__}


class PluginRegistry:
    def __init__(self, capacity: int = MAX_CAPACITY):
        self._capacity = min(capacity, MAX_CAPACITY)
        self._plugins: dict[str, PluginEntry] = {}
        self._lock = threading.Lock()

    @property
    def count(self) -> int:
        return len(self._plugins)

    @property
    def capacity(self) -> int:
        return self._capacity

    def register(self, plugin_id: str, name: str, **kwargs) -> dict:
        with self._lock:
            if plugin_id in self._plugins:
                return {"ok": False, "error": "duplicate", "plugin_id": plugin_id}
            if len(self._plugins) >= self._capacity:
                return {"ok": False, "error": "capacity_exceeded",
                        "current": len(self._plugins), "max": self._capacity}
            entry = PluginEntry(plugin_id, name, **kwargs)
            self._plugins[plugin_id] = entry
            return {"ok": True, "plugin_id": plugin_id, "count": len(self._plugins)}

    def unregister(self, plugin_id: str) -> dict:
        with self._lock:
            if plugin_id not in self._plugins:
                return {"ok": False, "error": "not_found"}
            del self._plugins[plugin_id]
            return {"ok": True, "plugin_id": plugin_id}

    def get(self, plugin_id: str) -> dict | None:
        entry = self._plugins.get(plugin_id)
        return entry.to_dict() if entry else None

    def list_all(self, category: str = "", limit: int = 100, offset: int = 0) -> list:
        entries = list(self._plugins.values())
        if category:
            entries = [e for e in entries if e.category == category]
        return [e.to_dict() for e in entries[offset:offset + limit]]

    def search(self, query: str, limit: int = 50) -> list:
        q = query.lower()
        results = [
            e for e in self._plugins.values()
            if q in e.name.lower() or q in e.category.lower() or q in e.provider.lower()
        ]
        return [e.to_dict() for e in results[:limit]]

    def set_status(self, plugin_id: str, status: str) -> dict:
        entry = self._plugins.get(plugin_id)
        if not entry:
            return {"ok": False, "error": "not_found"}
        entry.status = status
        return {"ok": True, "plugin_id": plugin_id, "status": status}

    def categories(self) -> dict:
        cats: dict[str, int] = {}
        for e in self._plugins.values():
            cats[e.category] = cats.get(e.category, 0) + 1
        return cats

    def stats(self) -> dict:
        by_status: dict[str, int] = {}
        for e in self._plugins.values():
            by_status[e.status] = by_status.get(e.status, 0) + 1
        return {
            "total": len(self._plugins),
            "capacity": self._capacity,
            "utilization_pct": round(len(self._plugins) / self._capacity * 100, 1),
            "by_status": by_status,
            "by_category": self.categories(),
        }

    def bulk_register(self, plugins: list[dict]) -> dict:
        registered = 0
        errors = []
        for p in plugins:
            result = self.register(**p)
            if result["ok"]:
                registered += 1
            else:
                errors.append({"plugin_id": p.get("plugin_id"), "error": result["error"]})
        return {"registered": registered, "errors": errors, "total": self.count}
