"""Universal Plugin Gateway — จุดเชื่อมต่อกลางของทุกปลั๊กอิน
ทุก request ต้องผ่าน Permission Check ก่อนเข้า Gateway
Module ที่ BLOCKED จะไม่รับงานจนกว่า Owner จะ approve"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

BLOCKED = "BLOCKED"
ACTIVE = "ACTIVE"
PENDING = "PENDING"
DISABLED = "DISABLED"


class ModuleGate:
    __slots__ = ("module_id", "name", "status", "reason", "updated_at")

    def __init__(self, module_id: str, name: str, status: str = BLOCKED,
                 reason: str = "Awaiting owner approval"):
        self.module_id = module_id
        self.name = name
        self.status = status
        self.reason = reason
        self.updated_at = datetime.now(TZ_BKK).isoformat()

    def to_dict(self) -> dict:
        return {s: getattr(self, s) for s in self.__slots__}


class UniversalPluginGateway:
    def __init__(self):
        self._modules: dict[str, ModuleGate] = {}
        self._audit: list[dict] = []
        self._connection_policy = {
            "verify_identity": True,
            "verify_permission": True,
            "verify_api": True,
            "owner_approval_required": True,
            "free_mode_only": True,
            "billing_enabled": False,
            "read_only": True,
            "copy_only": True,
            "source_write": False,
            "bypass_lockdown": False,
        }
        self._init_default_modules()

    def _init_default_modules(self):
        defaults = [
            ("universal_gateway", "Universal Plugin Gateway", BLOCKED,
             "Gateway ต้อง owner approve ก่อนเปิด"),
            ("meta_ai_adapter", "Meta AI Adapter", BLOCKED,
             "Meta AI ต้อง owner confirm + API key"),
            ("affiliate", "TikTok Affiliate", BLOCKED,
             "Affiliate ต้อง verify permission ก่อน"),
            ("plugin_registry", "Plugin Registry 10000", ACTIVE,
             "Internal registry — active"),
            ("windsor", "Windsor.ai Connector", ACTIVE,
             "Read-only analytics"),
            ("metricool", "Metricool Connector", ACTIVE,
             "Read-only social analytics"),
            ("tiktok_ads", "TikTok Ads Manager", ACTIVE,
             "Read-only ads data"),
            ("kpi_engine", "KPI Engine", ACTIVE,
             "Internal tracking — active"),
            ("ack_validator", "ACK Validator", ACTIVE,
             "Auto-ACK — active"),
            ("security_guardian", "Security Guardian", ACTIVE,
             "5-layer defense — active"),
            ("emergency_lockdown", "Emergency Lockdown", ACTIVE,
             "Override all — active"),
            ("backup_worker", "Backup Worker", ACTIVE,
             "Auto backup — active"),
        ]
        for mid, name, status, reason in defaults:
            self._modules[mid] = ModuleGate(mid, name, status, reason)

    def get_module(self, module_id: str) -> dict | None:
        gate = self._modules.get(module_id)
        return gate.to_dict() if gate else None

    def list_modules(self) -> list[dict]:
        return [g.to_dict() for g in self._modules.values()]

    def get_blocked(self) -> list[dict]:
        return [g.to_dict() for g in self._modules.values() if g.status == BLOCKED]

    def get_active(self) -> list[dict]:
        return [g.to_dict() for g in self._modules.values() if g.status == ACTIVE]

    def request_route(self, module_id: str, action: str, actor: str = "system") -> dict:
        ts = datetime.now(TZ_BKK).isoformat()
        gate = self._modules.get(module_id)
        if not gate:
            result = {"allowed": False, "reason": f"Module '{module_id}' not registered",
                      "timestamp": ts}
            self._audit.append({"type": "ROUTE_DENIED", "module": module_id,
                                "action": action, **result})
            return result

        if gate.status == BLOCKED:
            result = {"allowed": False, "module": module_id, "status": BLOCKED,
                      "reason": gate.reason, "timestamp": ts}
            self._audit.append({"type": "ROUTE_BLOCKED", "actor": actor,
                                "action": action, **result})
            return result

        if gate.status != ACTIVE:
            result = {"allowed": False, "module": module_id, "status": gate.status,
                      "reason": f"Module is {gate.status}", "timestamp": ts}
            self._audit.append({"type": "ROUTE_DENIED", "actor": actor,
                                "action": action, **result})
            return result

        if not self._check_policy(action):
            result = {"allowed": False, "module": module_id,
                      "reason": f"Action '{action}' blocked by connection policy",
                      "timestamp": ts}
            self._audit.append({"type": "POLICY_BLOCKED", "actor": actor,
                                "action": action, **result})
            return result

        result = {"allowed": True, "module": module_id, "status": ACTIVE,
                  "timestamp": ts}
        self._audit.append({"type": "ROUTE_ALLOWED", "actor": actor,
                            "action": action, **result})
        return result

    def _check_policy(self, action: str) -> bool:
        blocked_actions = {
            "spend", "billing", "publish", "oauth_grant",
            "external_share", "permission_change", "ad_create",
            "commerce_write", "source_write", "bypass_lockdown",
        }
        return action.lower() not in blocked_actions

    def approve_module(self, module_id: str, owner_token: str) -> dict:
        if owner_token != "OWNER_CONFIRMED":
            return {"ok": False, "error": "Owner confirmation required"}
        gate = self._modules.get(module_id)
        if not gate:
            return {"ok": False, "error": f"Module '{module_id}' not found"}
        gate.status = ACTIVE
        gate.reason = "Approved by owner"
        gate.updated_at = datetime.now(TZ_BKK).isoformat()
        self._audit.append({"type": "MODULE_APPROVED", "module": module_id,
                            "timestamp": gate.updated_at})
        return {"ok": True, "module": module_id, "status": ACTIVE}

    def block_module(self, module_id: str, reason: str = "Blocked by system") -> dict:
        gate = self._modules.get(module_id)
        if not gate:
            return {"ok": False, "error": f"Module '{module_id}' not found"}
        gate.status = BLOCKED
        gate.reason = reason
        gate.updated_at = datetime.now(TZ_BKK).isoformat()
        self._audit.append({"type": "MODULE_BLOCKED", "module": module_id,
                            "reason": reason, "timestamp": gate.updated_at})
        return {"ok": True, "module": module_id, "status": BLOCKED}

    def register_module(self, module_id: str, name: str,
                        initial_status: str = BLOCKED) -> dict:
        if module_id in self._modules:
            return {"ok": False, "error": "duplicate"}
        self._modules[module_id] = ModuleGate(module_id, name, initial_status)
        return {"ok": True, "module": module_id, "status": initial_status,
                "total": len(self._modules)}

    def get_connection_policy(self) -> dict:
        return dict(self._connection_policy)

    def get_audit_log(self, limit: int = 50) -> list:
        return self._audit[-limit:]

    def stats(self) -> dict:
        by_status: dict[str, int] = {}
        for g in self._modules.values():
            by_status[g.status] = by_status.get(g.status, 0) + 1
        return {
            "total_modules": len(self._modules),
            "by_status": by_status,
            "audit_entries": len(self._audit),
            "policy": self._connection_policy,
        }

    def kill_all_external(self) -> dict:
        blocked_count = 0
        for gate in self._modules.values():
            if gate.module_id in ("meta_ai_adapter", "affiliate", "universal_gateway"):
                if gate.status != BLOCKED:
                    gate.status = BLOCKED
                    gate.reason = "kill_all_external"
                    gate.updated_at = datetime.now(TZ_BKK).isoformat()
                    blocked_count += 1
        self._audit.append({"type": "KILL_ALL_EXTERNAL",
                            "blocked": blocked_count,
                            "timestamp": datetime.now(TZ_BKK).isoformat()})
        return {"ok": True, "blocked": blocked_count}
