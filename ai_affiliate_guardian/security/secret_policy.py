"""Secret Policy — Spec section 61
ห้ามเก็บค่าจริงของ PASSWORD, API KEY, APP SECRET, CLIENT SECRET,
ACCESS TOKEN, REFRESH TOKEN, PRIVATE KEY, OTP ใน Prompt / Git / Evidence / Audit"""

import re

FORBIDDEN_PATTERNS = [
    r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|refresh[_-]?token"
    r"|private[_-]?key|client[_-]?secret|app[_-]?secret|password|otp)"
    r"\s*[:=]\s*['\"]?[A-Za-z0-9+/=_\-]{8,}",
]

FORBIDDEN_FIELDS = {
    "password", "api_key", "app_secret", "client_secret",
    "access_token", "refresh_token", "private_key", "otp",
}


def scan_text(text: str) -> list[dict]:
    findings = []
    for pattern in FORBIDDEN_PATTERNS:
        for match in re.finditer(pattern, text):
            findings.append({
                "type": "SECRET_DETECTED",
                "match": match.group()[:20] + "...",
                "position": match.start(),
            })
    return findings


def is_safe_to_store(field_name: str) -> bool:
    return field_name.lower() not in FORBIDDEN_FIELDS


def redact(text: str) -> str:
    for pattern in FORBIDDEN_PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text)
    return text


def validate_audit_entry(entry: dict) -> tuple[bool, str]:
    for key, value in entry.items():
        if key.lower() in FORBIDDEN_FIELDS:
            return False, f"ห้ามเก็บ {key} ใน Audit"
        if isinstance(value, str) and scan_text(value):
            return False, f"พบ secret ในฟิลด์ {key}"
    return True, "ปลอดภัย"
