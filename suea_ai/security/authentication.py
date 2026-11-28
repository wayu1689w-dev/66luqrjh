"""Authentication — ตรวจสอบตัวตนก่อนเข้าถึงระบบ"""

from datetime import datetime, timezone, timedelta
import hashlib
import secrets

TZ_BKK = timezone(timedelta(hours=7))


class AuthToken:
    __slots__ = ("token_id", "role", "issued_at", "expires_minutes", "revoked")

    def __init__(self, role: str, expires_minutes: int = 60):
        self.token_id = secrets.token_hex(16)
        self.role = role
        self.issued_at = datetime.now(TZ_BKK)
        self.expires_minutes = expires_minutes
        self.revoked = False

    def is_expired(self) -> bool:
        elapsed = (datetime.now(TZ_BKK) - self.issued_at).total_seconds()
        return elapsed > self.expires_minutes * 60

    def is_valid(self) -> bool:
        return not self.revoked and not self.is_expired()

    def to_dict(self) -> dict:
        return {
            "token_id": self.token_id,
            "role": self.role,
            "issued_at": self.issued_at.isoformat(),
            "valid": self.is_valid(),
        }


class AuthManager:
    def __init__(self):
        self._tokens: dict[str, AuthToken] = {}
        self._failed_attempts: dict[str, int] = {}
        self._max_failed = 5

    def issue_token(self, role: str, expires_minutes: int = 60) -> dict:
        token = AuthToken(role, expires_minutes)
        self._tokens[token.token_id] = token
        return {"ok": True, "token_id": token.token_id, "role": role}

    def validate_token(self, token_id: str) -> dict:
        token = self._tokens.get(token_id)
        if not token:
            return {"valid": False, "reason": "token_not_found"}
        if token.revoked:
            return {"valid": False, "reason": "token_revoked"}
        if token.is_expired():
            return {"valid": False, "reason": "token_expired"}
        return {"valid": True, "role": token.role, "token_id": token_id}

    def revoke_token(self, token_id: str) -> dict:
        token = self._tokens.get(token_id)
        if not token:
            return {"ok": False, "error": "not_found"}
        token.revoked = True
        return {"ok": True, "token_id": token_id}

    def revoke_all(self) -> dict:
        count = 0
        for token in self._tokens.values():
            if not token.revoked:
                token.revoked = True
                count += 1
        return {"ok": True, "revoked": count}

    def record_failed_attempt(self, identifier: str) -> dict:
        self._failed_attempts[identifier] = self._failed_attempts.get(identifier, 0) + 1
        locked = self._failed_attempts[identifier] >= self._max_failed
        return {"identifier": identifier,
                "attempts": self._failed_attempts[identifier],
                "locked": locked}

    def is_locked(self, identifier: str) -> bool:
        return self._failed_attempts.get(identifier, 0) >= self._max_failed

    def reset_failed(self, identifier: str) -> dict:
        self._failed_attempts.pop(identifier, None)
        return {"ok": True, "identifier": identifier}

    def active_tokens(self) -> list[dict]:
        return [t.to_dict() for t in self._tokens.values() if t.is_valid()]

    def stats(self) -> dict:
        total = len(self._tokens)
        valid = sum(1 for t in self._tokens.values() if t.is_valid())
        return {"total": total, "valid": valid, "revoked": total - valid}
