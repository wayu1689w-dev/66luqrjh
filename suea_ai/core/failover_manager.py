"""Failover Manager — สลับไปยังระบบสำรองที่ได้รับอนุญาต"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))


class CircuitBreaker:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, threshold: int = 5, recovery_seconds: int = 60):
        self._threshold = threshold
        self._recovery_seconds = recovery_seconds
        self._failures: dict[str, int] = {}
        self._state: dict[str, str] = {}
        self._opened_at: dict[str, str] = {}

    def record_failure(self, provider_id: str) -> dict:
        self._failures[provider_id] = self._failures.get(provider_id, 0) + 1
        if self._failures[provider_id] >= self._threshold:
            self._state[provider_id] = self.OPEN
            self._opened_at[provider_id] = datetime.now(TZ_BKK).isoformat()
            return {"state": self.OPEN, "provider_id": provider_id,
                    "failures": self._failures[provider_id]}
        return {"state": self.CLOSED, "provider_id": provider_id,
                "failures": self._failures[provider_id]}

    def record_success(self, provider_id: str) -> dict:
        self._failures[provider_id] = 0
        self._state[provider_id] = self.CLOSED
        return {"state": self.CLOSED, "provider_id": provider_id}

    def get_state(self, provider_id: str) -> str:
        return self._state.get(provider_id, self.CLOSED)

    def is_available(self, provider_id: str) -> bool:
        return self.get_state(provider_id) != self.OPEN

    def try_half_open(self, provider_id: str) -> dict:
        if self.get_state(provider_id) == self.OPEN:
            self._state[provider_id] = self.HALF_OPEN
            return {"state": self.HALF_OPEN, "provider_id": provider_id}
        return {"state": self.get_state(provider_id), "provider_id": provider_id}

    def get_all_states(self) -> dict:
        providers = set(list(self._state.keys()) + list(self._failures.keys()))
        return {
            pid: {
                "state": self._state.get(pid, self.CLOSED),
                "failures": self._failures.get(pid, 0),
            }
            for pid in sorted(providers)
        }


class FailoverManager:
    def __init__(self, circuit_breaker: CircuitBreaker | None = None):
        self._cb = circuit_breaker or CircuitBreaker()
        self._fallback_map: dict[str, list[str]] = {}
        self._history: list[dict] = []

    def set_fallbacks(self, provider_id: str, fallbacks: list[str]) -> dict:
        self._fallback_map[provider_id] = fallbacks
        return {"ok": True, "provider_id": provider_id, "fallbacks": fallbacks}

    def select_provider(self, preferred: str) -> dict:
        if self._cb.is_available(preferred):
            return {"provider_id": preferred, "is_fallback": False}
        fallbacks = self._fallback_map.get(preferred, [])
        for fb in fallbacks:
            if self._cb.is_available(fb):
                entry = {
                    "event": "FAILOVER",
                    "from": preferred,
                    "to": fb,
                    "timestamp": datetime.now(TZ_BKK).isoformat(),
                }
                self._history.append(entry)
                return {"provider_id": fb, "is_fallback": True, "original": preferred}
        return {"provider_id": None, "error": "no_available_provider",
                "original": preferred, "tried": fallbacks}

    def report_failure(self, provider_id: str) -> dict:
        return self._cb.record_failure(provider_id)

    def report_success(self, provider_id: str) -> dict:
        return self._cb.record_success(provider_id)

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        return self._cb

    def get_failover_history(self, limit: int = 50) -> list:
        return self._history[-limit:]
