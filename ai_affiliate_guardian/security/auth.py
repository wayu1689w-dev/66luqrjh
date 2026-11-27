"""Private Login & Session — Spec v008 Area 1
ระบบล็อกอินส่วนตัว ตรวจสิทธิ์ จัดการ session"""

import hashlib
import hmac
import os
import time
from datetime import datetime, timezone

SESSION_TTL = 3600
_sessions: dict = {}


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(32)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return dk.hex(), salt.hex()


def verify_password(password: str, stored_hash: str, salt_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(dk.hex(), stored_hash)


def create_session(user_id: str, role: str = "viewer") -> dict:
    token = os.urandom(32).hex()
    _sessions[token] = {
        "user_id": user_id,
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": time.time() + SESSION_TTL,
    }
    return {"token": token, "expires_in": SESSION_TTL}


def validate_session(token: str) -> tuple[bool, dict | str]:
    session = _sessions.get(token)
    if not session:
        return False, "SESSION_NOT_FOUND"
    if time.time() > session["expires_at"]:
        del _sessions[token]
        return False, "SESSION_EXPIRED"
    return True, session


def revoke_session(token: str) -> bool:
    return _sessions.pop(token, None) is not None


def clear_expired():
    now = time.time()
    expired = [k for k, v in _sessions.items() if now > v["expires_at"]]
    for k in expired:
        del _sessions[k]
    return len(expired)


def active_session_count() -> int:
    clear_expired()
    return len(_sessions)
