"""ACK Validator — ตรวจสอบการตอบรับคำสั่งอัตโนมัติ"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))


class ACKValidator:
    def __init__(self):
        self._pending: dict[str, dict] = {}
        self._completed: list[dict] = []
        self._auto_ack_enabled = True

    def send_command(self, command_id: str, target: str, action: str,
                     timeout_seconds: int = 30) -> dict:
        entry = {
            "command_id": command_id,
            "target": target,
            "action": action,
            "status": "PENDING",
            "sent_at": datetime.now(TZ_BKK).isoformat(),
            "timeout_seconds": timeout_seconds,
        }
        self._pending[command_id] = entry
        return entry

    def receive_ack(self, command_id: str, source: str, evidence: str = "") -> dict:
        cmd = self._pending.get(command_id)
        if not cmd:
            return {"ok": False, "error": "unknown_command"}
        cmd["status"] = "ACK" if evidence else "ACK_NO_EVIDENCE"
        cmd["acked_by"] = source
        cmd["evidence"] = evidence
        cmd["acked_at"] = datetime.now(TZ_BKK).isoformat()
        self._completed.append(cmd)
        del self._pending[command_id]
        return {"ok": True, "status": cmd["status"], "command_id": command_id}

    def auto_ack(self, command_id: str) -> dict:
        if not self._auto_ack_enabled:
            return {"ok": False, "error": "auto_ack_disabled"}
        return self.receive_ack(command_id, source="AUTO_ACK", evidence="auto")

    def timeout_check(self) -> list:
        timed_out = []
        now = datetime.now(TZ_BKK)
        for cid, cmd in list(self._pending.items()):
            sent = datetime.fromisoformat(cmd["sent_at"])
            if (now - sent).total_seconds() > cmd["timeout_seconds"]:
                cmd["status"] = "TIMEOUT"
                timed_out.append(cmd)
                self._completed.append(cmd)
                del self._pending[cid]
        return timed_out

    def get_pending(self) -> list:
        return list(self._pending.values())

    def get_completed(self, limit: int = 50) -> list:
        return self._completed[-limit:]

    def stats(self) -> dict:
        acked = sum(1 for c in self._completed if c["status"].startswith("ACK"))
        timed_out = sum(1 for c in self._completed if c["status"] == "TIMEOUT")
        return {
            "pending": len(self._pending),
            "completed": len(self._completed),
            "acked": acked,
            "timed_out": timed_out,
            "auto_ack_enabled": self._auto_ack_enabled,
        }
