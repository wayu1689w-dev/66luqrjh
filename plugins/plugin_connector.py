"""Plugin Connector — เชื่อม plugins กับ v008 Security, Health Monitor, Registry
ทุก plugin ต้องผ่าน connector ก่อนทำงาน"""

from ai_affiliate_guardian.security.auth import validate_session
from ai_affiliate_guardian.security.rbac import check_access
from ai_affiliate_guardian.security.secret_policy import validate_audit_entry
from ai_affiliate_guardian.core.kill_switch import check_action_blocked
from ai_affiliate_guardian.automation.health_monitor import HealthMonitor, HealthStatus
from ai_affiliate_guardian.governance.audit import log_action

_monitor = HealthMonitor()

PLUGIN_REGISTRY = {
    "claude": {
        "name": "Claude",
        "category": "ai_text",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "chatgpt_work": {
        "name": "ChatGPT Work",
        "category": "ai_text",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "grokbot": {
        "name": "GrokBot",
        "category": "ai_text",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "gemini": {
        "name": "Gemini AI",
        "category": "ai_multimodal",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "meta_ai": {
        "name": "Meta AI",
        "category": "ai_multimodal",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "notion": {
        "name": "Notion",
        "category": "productivity",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "google_drive": {
        "name": "Google Drive",
        "category": "storage",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "windsor_tiktok": {
        "name": "Windsor.ai TikTok",
        "category": "analytics",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "metricool": {
        "name": "Metricool",
        "category": "social_media",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "tiktok_business": {
        "name": "TikTok for Business",
        "category": "ads",
        "risk": "R4",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "ADS",
        "external": True,
    },
    "canva": {
        "name": "Canva",
        "category": "design",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
        "disabled": True,
        "disabled_reason": "ไม่ใช้ Canva ตาม spec v008",
    },
    "figma": {
        "name": "Figma",
        "category": "design",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "wordpress": {
        "name": "WordPress",
        "category": "publishing",
        "risk": "R3",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "PUBLISH",
        "external": True,
    },
    "gmail": {
        "name": "Gmail",
        "category": "communication",
        "risk": "R3",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "SEND",
        "external": True,
    },
    "google_calendar": {
        "name": "Google Calendar",
        "category": "productivity",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "outlook_calendar": {
        "name": "Outlook Calendar",
        "category": "productivity",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "dropbox": {
        "name": "Dropbox",
        "category": "storage",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "supermetrics": {
        "name": "Supermetrics",
        "category": "analytics",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "microsoft_365": {
        "name": "Microsoft 365",
        "category": "productivity",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "adwhispr": {
        "name": "AdWhispr Ads",
        "category": "ads_research",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "aftership": {
        "name": "AfterShip TikTok Shop",
        "category": "commerce",
        "risk": "R3",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "COMMERCE",
        "external": True,
    },
    "opusclip": {
        "name": "OpusClip AI Producer",
        "category": "video",
        "risk": "R2",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "airtable": {
        "name": "Airtable",
        "category": "productivity",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "shopify": {
        "name": "Shopify",
        "category": "commerce",
        "risk": "R3",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "COMMERCE",
        "external": True,
    },
    "google_docs": {
        "name": "Google Docs",
        "category": "productivity",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "google_sheets": {
        "name": "Google Sheets",
        "category": "productivity",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "write",
        "action_type": "MCP_CALL",
        "external": True,
    },
    "google_slides": {
        "name": "Google Slides",
        "category": "productivity",
        "risk": "R1",
        "requires_auth": True,
        "required_permission": "read",
        "action_type": "MCP_CALL",
        "external": True,
    },
}


def get_plugin_info(plugin_key: str) -> dict | None:
    return PLUGIN_REGISTRY.get(plugin_key)


def list_all_plugins() -> list[dict]:
    result = []
    for key, info in PLUGIN_REGISTRY.items():
        result.append({"key": key, **info})
    return result


def list_by_category(category: str) -> list[dict]:
    return [
        {"key": k, **v} for k, v in PLUGIN_REGISTRY.items()
        if v["category"] == category
    ]


def execute_plugin(plugin_key: str, session_token: str,
                   action: str = "read", payload: dict | None = None) -> dict:
    info = PLUGIN_REGISTRY.get(plugin_key)
    if not info:
        return {"ok": False, "error": f"ปลั๊กอินไม่พบ: {plugin_key}"}

    if info.get("disabled"):
        return {"ok": False, "error": info.get("disabled_reason", "ปิดการใช้งาน")}

    ok, session = validate_session(session_token)
    if not ok:
        return {"ok": False, "error": f"Session ไม่ถูกต้อง: {session}"}

    role = session["role"]
    perm_ok, perm_msg = check_access(role, info["required_permission"])
    if not perm_ok:
        return {"ok": False, "error": perm_msg}

    blocked, reason = check_action_blocked(
        info["action_type"], external=info["external"]
    )
    if blocked:
        return {"ok": False, "error": f"Kill Switch ทำงาน: {reason}"}

    if payload:
        safe, msg = validate_audit_entry(payload)
        if not safe:
            return {"ok": False, "error": f"Secret Policy: {msg}"}

    comp = _monitor.components.get(plugin_key)
    if not comp:
        comp = _monitor.register(plugin_key)
    comp.report_ok()

    log_action(
        actor=session["user_id"],
        action=f"plugin_execute:{plugin_key}",
        target=action,
        details=f"role={role} risk={info['risk']}",
    )

    return {
        "ok": True,
        "plugin": info["name"],
        "action": action,
        "risk": info["risk"],
        "user": session["user_id"],
        "role": role,
    }


def plugin_health_report() -> dict:
    return _monitor.generate_report()


def plugin_count() -> int:
    return len(PLUGIN_REGISTRY)


def categories() -> list[str]:
    return sorted(set(v["category"] for v in PLUGIN_REGISTRY.values()))
