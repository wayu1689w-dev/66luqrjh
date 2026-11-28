"""Meta AI Connector — Adapter สำหรับ Meta AI (ยังไม่เปิดใช้งานจริง)"""

import os
from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))


class MetaAIConnector:
    def __init__(self):
        self._enabled = False
        self._status = "DISABLED"

    @property
    def enabled(self) -> bool:
        return self._enabled

    def health_check(self) -> dict:
        key = os.getenv("MODEL_API_KEY", "").strip()
        return {
            "connector": "meta_ai",
            "enabled": self._enabled,
            "status": self._status,
            "has_credential": bool(key),
            "checked_at": datetime.now(TZ_BKK).isoformat(),
        }

    def enable(self, owner_confirmed: bool = False) -> dict:
        if not owner_confirmed:
            return {"ok": False, "error": "Owner confirmation required"}
        key = os.getenv("MODEL_API_KEY", "").strip()
        if not key:
            return {"ok": False, "error": "MODEL_API_KEY not set"}
        self._enabled = True
        self._status = "READY"
        return {"ok": True, "status": "READY"}

    def disable(self) -> dict:
        self._enabled = False
        self._status = "DISABLED"
        return {"ok": True, "status": "DISABLED"}

    def execute(self, prompt: str, model: str = "meta-llama/Llama-4-Scout-17B-16E") -> dict:
        if not self._enabled:
            return {"ok": False, "error": "Meta AI connector is disabled"}
        return {
            "ok": False,
            "error": "Live execution not implemented — requires owner approval and API key",
            "model": model,
        }
