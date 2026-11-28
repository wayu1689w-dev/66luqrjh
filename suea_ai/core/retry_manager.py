"""Retry Manager — controlled retry with backoff"""

import time
from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 2


class RetryManager:
    def __init__(self, max_retries: int = DEFAULT_MAX_RETRIES,
                 backoff_base: float = DEFAULT_BACKOFF_BASE):
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._history: list[dict] = []

    def compute_delay(self, attempt: int) -> float:
        return min(self._backoff_base ** attempt, 60.0)

    def should_retry(self, attempt: int, error_type: str = "") -> dict:
        non_retryable = {"auth_failed", "permission_denied", "quota_exceeded", "billing_required"}
        if error_type in non_retryable:
            return {"retry": False, "reason": f"Non-retryable error: {error_type}"}
        if attempt >= self._max_retries:
            return {"retry": False, "reason": f"Max retries ({self._max_retries}) exceeded"}
        delay = self.compute_delay(attempt)
        return {"retry": True, "attempt": attempt + 1, "delay_seconds": delay}

    def record(self, task_id: str, attempt: int, success: bool, error: str = "") -> dict:
        entry = {
            "task_id": task_id,
            "attempt": attempt,
            "success": success,
            "error": error,
            "timestamp": datetime.now(TZ_BKK).isoformat(),
        }
        self._history.append(entry)
        return entry

    def get_history(self, task_id: str = "", limit: int = 50) -> list:
        entries = self._history
        if task_id:
            entries = [e for e in entries if e["task_id"] == task_id]
        return entries[-limit:]
