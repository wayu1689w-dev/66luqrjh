"""AI Guardian Engine — Spec sections 11, 45, 62
ตรวจ Identity, Resource, Permission, Evidence, Risk, Approval
ACTION_ALLOWED = ALL checks pass"""

from datetime import datetime, timezone


class GuardianVerdict:
    def __init__(self, allowed, reason, checks):
        self.allowed = allowed
        self.reason = reason
        self.checks = checks

    def to_dict(self):
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "checks": self.checks,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }


RISK_APPROVAL_MAP = {
    "R0": False,
    "R1": False,
    "R2": False,
    "R3": True,
    "R4": True,
    "R5": True,
}

RISK_LABELS = {
    "R0": "local computation",
    "R1": "external read",
    "R2": "draft/local change",
    "R3": "external write",
    "R4": "publish/send",
    "R5": "finance/ads/admin/permission",
}


def evaluate_action(action):
    """Evaluate an action dict through Guardian checks.

    Required keys:
        actor, action_type, risk, plugin_state (or None),
        evidence_ids, approval_id (or None),
        external (bool), system_policy (dict with kill switches)
    """
    checks = {}
    reasons = []

    # 1. Identity
    actor = action.get("actor")
    checks["identity_verified"] = bool(actor)
    if not actor:
        reasons.append("No actor identity")

    # 2. Plugin health
    plugin_state = action.get("plugin_state")
    if plugin_state is not None:
        healthy = plugin_state in ("CONNECTED", "READ_READY", "WRITE_READY",
                                    "PRODUCTION_READY", "HEALTH_CHECK")
        checks["plugin_healthy"] = healthy
        if not healthy:
            reasons.append(f"Plugin state {plugin_state} not healthy")
    else:
        checks["plugin_healthy"] = True  # no plugin needed

    # 3. Risk level
    risk = action.get("risk", "R0")
    checks["risk_level"] = risk
    checks["risk_label"] = RISK_LABELS.get(risk, "unknown")

    # 4. Kill switch
    policy = action.get("system_policy", {})
    external = action.get("external", False)
    action_type = action.get("action_type", "")

    kill_checks = _check_kill_switches(action_type, risk, external, policy)
    checks.update(kill_checks)
    if kill_checks.get("killed"):
        reasons.append(f"Kill switch active: {kill_checks.get('kill_reason')}")

    # 5. Evidence
    evidence_ids = action.get("evidence_ids", [])
    evidence_required = action.get("evidence_required", False)
    if evidence_required and not evidence_ids:
        checks["evidence_sufficient"] = False
        reasons.append("Evidence required but none provided")
    else:
        checks["evidence_sufficient"] = True

    # 6. Approval
    needs_approval = RISK_APPROVAL_MAP.get(risk, True)
    if action.get("requires_approval") is not None:
        needs_approval = action["requires_approval"]
    approval_id = action.get("approval_id")
    if needs_approval and not approval_id:
        checks["approval_valid"] = False
        reasons.append(f"Approval required for {risk} action")
    else:
        checks["approval_valid"] = True

    # 7. Policy check
    checks["policy_allows"] = not checks.get("killed", False)

    # Final verdict
    allowed = (
        checks["identity_verified"]
        and checks["plugin_healthy"]
        and checks["evidence_sufficient"]
        and checks["approval_valid"]
        and checks["policy_allows"]
    )

    reason = "PASS" if allowed else "; ".join(reasons)
    return GuardianVerdict(allowed=allowed, reason=reason, checks=checks)


def _check_kill_switches(action_type, risk, external, policy):
    result = {"killed": False, "kill_reason": None}

    if policy.get("KILL_ALL_EXTERNAL") and external:
        result = {"killed": True, "kill_reason": "KILL_ALL_EXTERNAL"}
        return result

    action_upper = action_type.upper() if action_type else ""

    if policy.get("KILL_PUBLISH") and action_upper in ("PUBLISH", "SEND"):
        result = {"killed": True, "kill_reason": "KILL_PUBLISH"}
    elif policy.get("KILL_ADS") and action_upper in ("ADS", "ADS_WRITE", "AD_CREATE"):
        result = {"killed": True, "kill_reason": "KILL_ADS"}
    elif policy.get("KILL_COMMERCE") and action_upper in ("COMMERCE", "COMMERCE_WRITE"):
        result = {"killed": True, "kill_reason": "KILL_COMMERCE"}
    elif policy.get("KILL_PLUGIN") and action_upper == "PLUGIN_EXECUTE":
        result = {"killed": True, "kill_reason": "KILL_PLUGIN"}
    elif policy.get("KILL_MCP") and action_upper == "MCP_CALL":
        result = {"killed": True, "kill_reason": "KILL_MCP"}
    elif policy.get("KILL_OAUTH") and action_upper == "OAUTH_GRANT":
        result = {"killed": True, "kill_reason": "KILL_OAUTH"}

    return result


def permission_intersection(user_perm, plugin_perm, credential_perm,
                            resource_perm, system_policy_allows):
    """Spec section 62: FINAL = intersection of all permission layers"""
    return all([user_perm, plugin_perm, credential_perm,
                resource_perm, system_policy_allows])
