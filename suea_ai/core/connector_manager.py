"""Connector Manager — จัดการ connector instances ทั้งหมดผ่าน Gateway"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))


class ConnectorInstance:
    __slots__ = ("connector_id", "name", "provider", "status",
                 "requires_credential", "connected_at", "last_health")

    def __init__(self, connector_id: str, name: str, provider: str,
                 requires_credential: bool = True):
        self.connector_id = connector_id
        self.name = name
        self.provider = provider
        self.status = "DISCONNECTED"
        self.requires_credential = requires_credential
        self.connected_at = None
        self.last_health = None

    def to_dict(self) -> dict:
        return {s: getattr(self, s) for s in self.__slots__}


class ConnectorManager:
    def __init__(self):
        self._connectors: dict[str, ConnectorInstance] = {}
        self._audit: list[dict] = []
        self._init_defaults()

    def _init_defaults(self):
        defaults = [
            ("windsor", "Windsor.ai", "windsor", False),
            ("metricool", "Metricool", "metricool", False),
            ("tiktok_ads", "TikTok Ads", "tiktok", False),
            ("tiktok_organic", "TikTok Organic", "tiktok", False),
            ("notion", "Notion", "notion", False),
            ("google_drive", "Google Drive", "google", False),
            ("gmail", "Gmail", "google", False),
            ("claude", "Claude AI", "anthropic", True),
            ("gemini", "Gemini AI", "google", True),
            ("grok", "GrokBot", "xai", True),
            ("meta_ai", "Meta AI", "meta", True),
            ("opusclip", "OpusClip", "opusclip", False),
        ]
        for cid, name, provider, req_cred in defaults:
            self._connectors[cid] = ConnectorInstance(cid, name, provider, req_cred)

    def connect(self, connector_id: str) -> dict:
        inst = self._connectors.get(connector_id)
        if not inst:
            return {"ok": False, "error": "not_found"}
        inst.status = "CONNECTED"
        inst.connected_at = datetime.now(TZ_BKK).isoformat()
        self._audit.append({"action": "CONNECT", "connector": connector_id,
                            "timestamp": inst.connected_at})
        return {"ok": True, "connector_id": connector_id, "status": "CONNECTED"}

    def disconnect(self, connector_id: str) -> dict:
        inst = self._connectors.get(connector_id)
        if not inst:
            return {"ok": False, "error": "not_found"}
        inst.status = "DISCONNECTED"
        ts = datetime.now(TZ_BKK).isoformat()
        self._audit.append({"action": "DISCONNECT", "connector": connector_id,
                            "timestamp": ts})
        return {"ok": True, "connector_id": connector_id, "status": "DISCONNECTED"}

    def disconnect_all(self) -> dict:
        count = 0
        for inst in self._connectors.values():
            if inst.status == "CONNECTED":
                inst.status = "DISCONNECTED"
                count += 1
        self._audit.append({"action": "DISCONNECT_ALL", "count": count,
                            "timestamp": datetime.now(TZ_BKK).isoformat()})
        return {"ok": True, "disconnected": count}

    def health_check(self, connector_id: str) -> dict:
        inst = self._connectors.get(connector_id)
        if not inst:
            return {"ok": False, "error": "not_found"}
        ts = datetime.now(TZ_BKK).isoformat()
        inst.last_health = ts
        return {
            "connector_id": connector_id,
            "status": inst.status,
            "requires_credential": inst.requires_credential,
            "checked_at": ts,
        }

    def get(self, connector_id: str) -> dict | None:
        inst = self._connectors.get(connector_id)
        return inst.to_dict() if inst else None

    def list_all(self) -> list[dict]:
        return [c.to_dict() for c in self._connectors.values()]

    def list_connected(self) -> list[dict]:
        return [c.to_dict() for c in self._connectors.values()
                if c.status == "CONNECTED"]

    def list_by_provider(self, provider: str) -> list[dict]:
        return [c.to_dict() for c in self._connectors.values()
                if c.provider == provider]

    def register(self, connector_id: str, name: str, provider: str,
                 requires_credential: bool = True) -> dict:
        if connector_id in self._connectors:
            return {"ok": False, "error": "duplicate"}
        self._connectors[connector_id] = ConnectorInstance(
            connector_id, name, provider, requires_credential)
        return {"ok": True, "connector_id": connector_id,
                "total": len(self._connectors)}

    def stats(self) -> dict:
        connected = sum(1 for c in self._connectors.values()
                        if c.status == "CONNECTED")
        return {
            "total": len(self._connectors),
            "connected": connected,
            "disconnected": len(self._connectors) - connected,
            "by_provider": self._count_by_provider(),
        }

    def _count_by_provider(self) -> dict:
        counts: dict[str, int] = {}
        for c in self._connectors.values():
            counts[c.provider] = counts.get(c.provider, 0) + 1
        return counts

    def get_audit(self, limit: int = 50) -> list:
        return self._audit[-limit:]
