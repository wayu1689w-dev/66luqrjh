"""Base Connector — ฐานสำหรับ connector ทั้งหมด"""

import os
from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))


class BaseConnector:
    connector_id: str = ""
    name: str = ""
    env_key: str = ""
    connector_type: str = "generic"

    def has_credential(self) -> bool:
        return bool(os.getenv(self.env_key, "").strip())

    def health_check(self) -> dict:
        return {
            "connector": self.connector_id,
            "name": self.name,
            "type": self.connector_type,
            "has_credential": self.has_credential(),
            "status": "READY" if self.has_credential() else "NO_CREDENTIAL",
            "checked_at": datetime.now(TZ_BKK).isoformat(),
        }

    def validate_credential(self) -> dict:
        if not self.has_credential():
            return {"valid": False, "error": f"{self.env_key} not set"}
        return {"valid": True, "connector": self.connector_id}


class WindsorConnector(BaseConnector):
    connector_id = "windsor"
    name = "Windsor.ai"
    env_key = "WINDSOR_API_KEY"
    connector_type = "analytics"


class MetricoolConnector(BaseConnector):
    connector_id = "metricool"
    name = "Metricool"
    env_key = "METRICOOL_API_KEY"
    connector_type = "social"


class TikTokConnector(BaseConnector):
    connector_id = "tiktok"
    name = "TikTok Marketing API"
    env_key = "TIKTOK_ACCESS_TOKEN"
    connector_type = "ads"


class NotionConnector(BaseConnector):
    connector_id = "notion"
    name = "Notion"
    env_key = "NOTION_API_KEY"
    connector_type = "productivity"


class GeminiConnector(BaseConnector):
    connector_id = "gemini"
    name = "Google Gemini"
    env_key = "GEMINI_API_KEY"
    connector_type = "ai"


class ClaudeConnector(BaseConnector):
    connector_id = "claude"
    name = "Claude (Anthropic)"
    env_key = "ANTHROPIC_API_KEY"
    connector_type = "ai"


class GrokConnector(BaseConnector):
    connector_id = "grok"
    name = "GrokBot (xAI)"
    env_key = "GROK_API_KEY"
    connector_type = "ai"


ALL_CONNECTORS = [
    WindsorConnector(), MetricoolConnector(), TikTokConnector(),
    NotionConnector(), GeminiConnector(), ClaudeConnector(), GrokConnector(),
]


def get_all_connector_status() -> list:
    return [c.health_check() for c in ALL_CONNECTORS]
