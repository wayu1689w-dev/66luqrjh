"""Owner Approval — ระบบขออนุมัติจากเจ้าของก่อนดำเนินการ"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

ACTIONS_REQUIRING_APPROVAL = frozenset({
    "plugin_install", "plugin_remove", "connector_enable",
    "credential_manage", "lockdown_release", "billing_change",
    "permission_change", "external_connection", "data_export",
    "auto_execution_enable",
})


class ApprovalRequest:
    __slots__ = ("request_id", "action", "detail", "status",
                 "requested_at", "resolved_at", "resolved_by")

    def __init__(self, request_id: str, action: str, detail: str = ""):
        self.request_id = request_id
        self.action = action
        self.detail = detail
        self.status = "PENDING"
        self.requested_at = datetime.now(TZ_BKK).isoformat()
        self.resolved_at = None
        self.resolved_by = None

    def to_dict(self) -> dict:
        return {s: getattr(self, s) for s in self.__slots__}


class OwnerApproval:
    def __init__(self):
        self._requests: dict[str, ApprovalRequest] = {}
        self._counter = 0

    def requires_approval(self, action: str) -> bool:
        return action in ACTIONS_REQUIRING_APPROVAL

    def request(self, action: str, detail: str = "") -> dict:
        if not self.requires_approval(action):
            return {"ok": True, "auto_approved": True, "action": action}
        self._counter += 1
        rid = f"APR-{self._counter:04d}"
        req = ApprovalRequest(rid, action, detail)
        self._requests[rid] = req
        return {"ok": True, "request_id": rid, "status": "PENDING"}

    def approve(self, request_id: str, owner_token: str) -> dict:
        if owner_token != "OWNER_CONFIRMED":
            return {"ok": False, "error": "invalid_owner_token"}
        req = self._requests.get(request_id)
        if not req:
            return {"ok": False, "error": "not_found"}
        if req.status != "PENDING":
            return {"ok": False, "error": f"already_{req.status.lower()}"}
        req.status = "APPROVED"
        req.resolved_at = datetime.now(TZ_BKK).isoformat()
        req.resolved_by = "owner"
        return {"ok": True, "request_id": request_id, "status": "APPROVED"}

    def deny(self, request_id: str, owner_token: str) -> dict:
        if owner_token != "OWNER_CONFIRMED":
            return {"ok": False, "error": "invalid_owner_token"}
        req = self._requests.get(request_id)
        if not req:
            return {"ok": False, "error": "not_found"}
        if req.status != "PENDING":
            return {"ok": False, "error": f"already_{req.status.lower()}"}
        req.status = "DENIED"
        req.resolved_at = datetime.now(TZ_BKK).isoformat()
        req.resolved_by = "owner"
        return {"ok": True, "request_id": request_id, "status": "DENIED"}

    def get(self, request_id: str) -> dict | None:
        req = self._requests.get(request_id)
        return req.to_dict() if req else None

    def pending(self) -> list[dict]:
        return [r.to_dict() for r in self._requests.values()
                if r.status == "PENDING"]

    def all_requests(self, limit: int = 100) -> list[dict]:
        return [r.to_dict() for r in list(self._requests.values())[-limit:]]

    def stats(self) -> dict:
        by_status: dict[str, int] = {}
        for r in self._requests.values():
            by_status[r.status] = by_status.get(r.status, 0) + 1
        return {"total": len(self._requests), "by_status": by_status}
