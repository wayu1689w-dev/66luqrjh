"""Health Monitor — Spec v008 Area 6
ทำงาน 24 ชั่วโมง ตรวจสถานะทุก 30 วินาที รายงาน/สำรองทุก 30 นาที"""

from datetime import datetime, timezone
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class ComponentHealth:
    def __init__(self, name: str):
        self.name = name
        self.status = HealthStatus.UNKNOWN
        self.last_check = None
        self.error_count = 0
        self.consecutive_failures = 0

    def report_ok(self):
        self.status = HealthStatus.HEALTHY
        self.last_check = datetime.now(timezone.utc).isoformat()
        self.consecutive_failures = 0

    def report_error(self, error: str = ""):
        self.error_count += 1
        self.consecutive_failures += 1
        self.last_check = datetime.now(timezone.utc).isoformat()
        if self.consecutive_failures >= 3:
            self.status = HealthStatus.DOWN
        else:
            self.status = HealthStatus.DEGRADED

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "last_check": self.last_check,
            "error_count": self.error_count,
            "consecutive_failures": self.consecutive_failures,
        }


class HealthMonitor:
    CHECK_INTERVAL = 30
    REPORT_INTERVAL = 1800

    def __init__(self):
        self.components: dict[str, ComponentHealth] = {}
        self.alerts: list[dict] = []

    def register(self, name: str) -> ComponentHealth:
        comp = ComponentHealth(name)
        self.components[name] = comp
        return comp

    def check_all(self) -> dict:
        summary = {}
        for name, comp in self.components.items():
            summary[name] = comp.status.value
        return summary

    def overall_status(self) -> HealthStatus:
        if not self.components:
            return HealthStatus.UNKNOWN
        statuses = [c.status for c in self.components.values()]
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        if any(s == HealthStatus.DOWN for s in statuses):
            return HealthStatus.DOWN
        return HealthStatus.DEGRADED

    def add_alert(self, component: str, message: str, severity: str = "warning"):
        self.alerts.append({
            "component": component,
            "message": message,
            "severity": severity,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    def get_alerts(self, severity: str | None = None) -> list[dict]:
        if severity:
            return [a for a in self.alerts if a["severity"] == severity]
        return list(self.alerts)

    def generate_report(self) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall": self.overall_status().value,
            "components": {n: c.to_dict() for n, c in self.components.items()},
            "total_alerts": len(self.alerts),
            "recent_alerts": self.alerts[-10:],
        }

    def clear_alerts(self):
        self.alerts.clear()
