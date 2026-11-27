"""Plugin เสือเจาะข้อมูล — ตรวจจับและป้องกันการโจรกรรมข้อมูลในระบบ SUEA
ใช้สำหรับป้องกันระบบของตัวเองเท่านั้น ห้ามใช้โจมตีระบบอื่น"""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


class DataLeakDetector:
    """ตรวจจับการรั่วไหลของข้อมูลสำคัญ"""

    SENSITIVE_PATTERNS = {
        "api_key": r"(?i)['\"]?(api[_-]?key|secret[_-]?key)['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9+/=_\-]{16,}",
        "token": r"(?i)(access[_-]?token|refresh[_-]?token|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9+/=_\-]{16,}",
        "password": r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]{6,}",
        "private_key": r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----",
        "credit_card": r"\b[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}\b",
        "thai_id": r"\b[0-9]{1}-[0-9]{4}-[0-9]{5}-[0-9]{2}-[0-9]{1}\b",
        "email_leak": r"(?i)(email|อีเมล)\s*[:=]\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+",
        "phone_th": r"(?i)(phone|โทร|เบอร์)\s*[:=]\s*0[0-9]{8,9}",
    }

    @classmethod
    def scan_text(cls, text: str) -> list[dict]:
        findings = []
        for name, pattern in cls.SENSITIVE_PATTERNS.items():
            for match in re.finditer(pattern, text):
                findings.append({
                    "type": name,
                    "severity": cls._severity(name),
                    "position": match.start(),
                    "preview": match.group()[:15] + "***",
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                })
        return findings

    @classmethod
    def scan_file(cls, file_path: str) -> list[dict]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            findings = cls.scan_text(content)
            for f_item in findings:
                f_item["file"] = file_path
            return findings
        except (OSError, IOError):
            return [{"type": "READ_ERROR", "file": file_path}]

    @classmethod
    def scan_directory(cls, dir_path: str, extensions: tuple = (".py", ".json", ".yaml", ".yml", ".env", ".txt")) -> list[dict]:
        all_findings = []
        path = Path(dir_path)
        for f in path.rglob("*"):
            if f.is_file() and f.suffix in extensions:
                all_findings.extend(cls.scan_file(str(f)))
        return all_findings

    @staticmethod
    def _severity(pattern_name: str) -> str:
        critical = {"private_key", "credit_card", "thai_id", "password"}
        high = {"api_key", "token"}
        if pattern_name in critical:
            return "CRITICAL"
        if pattern_name in high:
            return "HIGH"
        return "MEDIUM"


class AccessMonitor:
    """ตรวจจับพฤติกรรมการเข้าถึงผิดปกติ"""

    def __init__(self):
        self.access_log: list[dict] = []
        self.blocked_ips: set = set()
        self.rate_limits: dict[str, list[float]] = {}

    def log_access(self, user_id: str, resource: str, action: str,
                   ip: str = "", success: bool = True) -> dict:
        import time
        entry = {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "ip": ip,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "epoch": time.time(),
        }
        self.access_log.append(entry)
        return entry

    def detect_brute_force(self, user_id: str, window_sec: float = 60.0,
                           threshold: int = 5) -> tuple[bool, str]:
        import time
        now = time.time()
        recent_failures = [
            e for e in self.access_log
            if e["user_id"] == user_id
            and not e["success"]
            and now - e["epoch"] < window_sec
        ]
        if len(recent_failures) >= threshold:
            return True, f"Brute force: {len(recent_failures)} ครั้งใน {window_sec} วินาที"
        return False, "ปกติ"

    def detect_unusual_access(self, user_id: str) -> list[dict]:
        alerts = []
        user_actions = [e for e in self.access_log if e["user_id"] == user_id]

        resources = set()
        for entry in user_actions[-50:]:
            resources.add(entry["resource"])
        if len(resources) > 20:
            alerts.append({
                "type": "MASS_ACCESS",
                "detail": f"เข้าถึง {len(resources)} ทรัพยากรภายในช่วงสั้น",
                "severity": "HIGH",
            })

        sensitive_resources = [
            e for e in user_actions
            if any(w in e["resource"].lower()
                   for w in ("secret", "key", "token", "password", "credential",
                             "backup", "audit", "finance", "payment"))
        ]
        if len(sensitive_resources) > 3:
            alerts.append({
                "type": "SENSITIVE_ACCESS",
                "detail": f"เข้าถึงข้อมูลสำคัญ {len(sensitive_resources)} ครั้ง",
                "severity": "CRITICAL",
            })

        return alerts

    def block_ip(self, ip: str):
        self.blocked_ips.add(ip)

    def is_blocked(self, ip: str) -> bool:
        return ip in self.blocked_ips

    def check_rate_limit(self, user_id: str, max_per_minute: int = 30) -> tuple[bool, str]:
        import time
        now = time.time()
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        self.rate_limits[user_id] = [
            t for t in self.rate_limits[user_id] if now - t < 60
        ]
        if len(self.rate_limits[user_id]) >= max_per_minute:
            return False, f"เกินขีดจำกัด: {max_per_minute} ครั้ง/นาที"
        self.rate_limits[user_id].append(now)
        return True, "ผ่าน"


class IntegrityChecker:
    """ตรวจว่าไฟล์ระบบไม่ถูกแก้ไขโดยไม่ได้รับอนุญาต"""

    def __init__(self):
        self.baseline: dict[str, str] = {}

    def create_baseline(self, file_paths: list[str]) -> int:
        count = 0
        for fp in file_paths:
            try:
                h = self._hash_file(fp)
                self.baseline[fp] = h
                count += 1
            except (OSError, IOError):
                pass
        return count

    def check_integrity(self) -> list[dict]:
        changes = []
        for fp, expected_hash in self.baseline.items():
            try:
                current = self._hash_file(fp)
                if current != expected_hash:
                    changes.append({
                        "file": fp,
                        "status": "MODIFIED",
                        "expected": expected_hash[:16] + "...",
                        "actual": current[:16] + "...",
                    })
            except FileNotFoundError:
                changes.append({"file": fp, "status": "DELETED"})
            except (OSError, IOError):
                changes.append({"file": fp, "status": "READ_ERROR"})
        return changes

    @staticmethod
    def _hash_file(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()


class ExfiltrationGuard:
    """ป้องกันการส่งข้อมูลออกนอกระบบ"""

    BLOCKED_DESTINATIONS = {
        "pastebin.com", "hastebin.com", "ghostbin.com",
        "transfer.sh", "file.io",
    }

    MAX_EXPORT_SIZE_MB = 50

    @classmethod
    def check_destination(cls, url: str) -> tuple[bool, str]:
        for blocked in cls.BLOCKED_DESTINATIONS:
            if blocked in url.lower():
                return False, f"ปลายทางถูกบล็อก: {blocked}"
        return True, "ปลายทางอนุญาต"

    @classmethod
    def check_export_size(cls, size_bytes: int) -> tuple[bool, str]:
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > cls.MAX_EXPORT_SIZE_MB:
            return False, f"ไฟล์ใหญ่เกิน ({size_mb:.1f} MB > {cls.MAX_EXPORT_SIZE_MB} MB)"
        return True, f"ขนาดไฟล์ปกติ ({size_mb:.1f} MB)"

    @classmethod
    def check_bulk_download(cls, file_count: int, threshold: int = 100) -> tuple[bool, str]:
        if file_count > threshold:
            return False, f"ดาวน์โหลดจำนวนมาก: {file_count} ไฟล์ (เกิน {threshold})"
        return True, "จำนวนปกติ"


class SecurityReport:
    """สร้างรายงานความปลอดภัยรวม"""

    @staticmethod
    def generate(leak_findings: list, access_alerts: list,
                 integrity_changes: list, timestamp: str = "") -> dict:
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()

        critical = sum(
            1 for f in leak_findings if f.get("severity") == "CRITICAL"
        ) + sum(
            1 for a in access_alerts if a.get("severity") == "CRITICAL"
        )
        high = sum(
            1 for f in leak_findings if f.get("severity") == "HIGH"
        ) + sum(
            1 for a in access_alerts if a.get("severity") == "HIGH"
        )

        if critical > 0:
            overall = "CRITICAL"
        elif high > 0 or integrity_changes:
            overall = "WARNING"
        elif leak_findings or access_alerts:
            overall = "NOTICE"
        else:
            overall = "CLEAN"

        return {
            "timestamp": timestamp,
            "overall": overall,
            "summary": {
                "leak_findings": len(leak_findings),
                "access_alerts": len(access_alerts),
                "integrity_changes": len(integrity_changes),
                "critical_count": critical,
                "high_count": high,
            },
            "leaks": leak_findings[:20],
            "access": access_alerts[:20],
            "integrity": integrity_changes[:20],
        }
