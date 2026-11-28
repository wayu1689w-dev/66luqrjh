"""KPI Engine — ติดตามสถานะ AI Agent ทุกตัว + บังคับ KPI"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

AGENTS = (
    "ChatGPT",
    "ChatGPT Work",
    "Claude",
    "GrokBot",
    "Windsor.ai",
    "Metricool",
    "TikTok Ads Manager",
    "TikTok Ads Assistant",
    "Notion",
)

POLICY = {
    "system": "SUEA_AI_KPI",
    "owner_control": True,
    "private_mode": True,
    "read_only": True,
    "free_only": True,
    "kpi_enforcement": True,
    "report_required": True,
    "ack_required": True,
    "evidence_required": True,
    "report_interval_minutes": 60,
    "max_retries": 3,
    "block_fake_data": True,
    "block_duplicate_data": True,
    "block_unauthorized_access": True,
    "block_external_sharing": True,
    "block_permission_changes": True,
    "auto_spending": False,
    "auto_connect_new_plugins": False,
    "owner_approval_required": True,
    "report_destination": "OWNER_ONLY",
}


def initial_status(agent: str) -> dict:
    if agent not in AGENTS:
        raise ValueError(f"Unknown agent: {agent}")
    return {
        "agent": agent,
        "status": "UNVERIFIED",
        "ack": False,
        "kpi_score": None,
        "completed_tasks": None,
        "pending_tasks": None,
        "errors": [],
        "evidence": [],
        "last_report": None,
        "checked_at": datetime.now(TZ_BKK).isoformat(),
    }


def get_kpi_status() -> list:
    return [initial_status(agent) for agent in AGENTS]


def validate_evidence(evidence: list) -> dict:
    if not evidence:
        return {"valid": False, "reason": "ไม่มีหลักฐาน"}
    for item in evidence:
        if not isinstance(item, dict):
            return {"valid": False, "reason": "รูปแบบหลักฐานไม่ถูกต้อง"}
        if "type" not in item or "value" not in item:
            return {"valid": False, "reason": "หลักฐานต้องมี type และ value"}
    return {"valid": True, "count": len(evidence)}


def compute_kpi_score(agent_status: dict) -> float:
    score = 0.0
    if agent_status.get("ack"):
        score += 30.0
    if agent_status.get("evidence"):
        ev = validate_evidence(agent_status["evidence"])
        if ev["valid"]:
            score += 30.0
    if agent_status.get("completed_tasks") and agent_status["completed_tasks"] > 0:
        score += 20.0
    if not agent_status.get("errors"):
        score += 20.0
    return score


def enforce_policy(action: str) -> dict:
    blocked = {
        "spend", "auto_spend", "ad_create", "publish",
        "change_permission", "external_share", "connect_new_plugin",
    }
    if action.lower() in blocked:
        return {
            "allowed": False,
            "reason": f"Action '{action}' blocked by SUEA_AI_KPI policy",
            "policy": "owner_approval_required",
        }
    return {"allowed": True}


def get_policy() -> dict:
    return dict(POLICY)
