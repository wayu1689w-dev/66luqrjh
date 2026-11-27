"""Plugin Pipeline — เชื่อม Auto-Discovery + Connector + v008 Security
รับคำสั่งภาษาธรรมชาติ → ค้นหาปลั๊กอิน → ตรวจสิทธิ์ → ดำเนินการ → ตรวจผลลัพธ์"""

from datetime import datetime, timezone

from plugins.plugin_auto_discovery import (
    auto_match, auto_respond, search, search_by_task,
    health_summary, EXTENDED_REGISTRY,
)
from plugins.plugin_connector import (
    execute_plugin, get_plugin_info, PLUGIN_REGISTRY,
)
from ai_affiliate_guardian.security.auth import validate_session
from ai_affiliate_guardian.security.rbac import check_access
from ai_affiliate_guardian.core.kill_switch import check_action_blocked
from ai_affiliate_guardian.automation.health_monitor import HealthMonitor, HealthStatus
from ai_affiliate_guardian.governance.audit import log_action


_pipeline_monitor = HealthMonitor()
_pipeline_log: list[dict] = []

APPROVAL_REQUIRED_RISK = 3
MAX_RETRY = 3


def _risk_level(risk_str: str) -> int:
    try:
        return int(risk_str.replace("R", ""))
    except (ValueError, AttributeError):
        return 0


def smart_execute(task_description: str, session_token: str,
                  action: str = "read", payload: dict | None = None,
                  auto_approve: bool = False) -> dict:
    """Pipeline หลัก: รับคำสั่ง → ค้นหา → ตรวจ → ดำเนินการ"""

    response = auto_respond(task_description)
    recommended = response["recommended"]

    if not recommended:
        entry = _log_entry("NO_MATCH", task_description, None, "ไม่พบปลั๊กอินที่เหมาะ")
        return {
            "ok": False,
            "stage": "discovery",
            "error": "ไม่พบปลั๊กอินที่เหมาะกับงานนี้",
            "suggestions": [p["name"] for p in response["needs_setup"][:5]],
            "log": entry,
        }

    plugin_key = recommended["key"]
    plugin_name = recommended["name"]
    risk = _risk_level(recommended.get("risk", "R0"))

    ok_session, session = validate_session(session_token)
    if not ok_session:
        entry = _log_entry("AUTH_FAIL", task_description, plugin_key, str(session))
        return {"ok": False, "stage": "auth", "error": f"Session ไม่ถูกต้อง: {session}", "log": entry}

    if risk >= APPROVAL_REQUIRED_RISK and not auto_approve:
        entry = _log_entry("APPROVAL_NEEDED", task_description, plugin_key,
                           f"R{risk} ต้องอนุมัติก่อนดำเนินการ")
        return {
            "ok": False,
            "stage": "approval",
            "error": f"ปลั๊กอิน {plugin_name} (R{risk}) ต้องได้รับการอนุมัติก่อน",
            "plugin": plugin_name,
            "risk": f"R{risk}",
            "alternatives": [p["name"] for p in response["available"][1:4]],
            "log": entry,
        }

    connector_info = get_plugin_info(plugin_key)
    if connector_info:
        result = execute_plugin(plugin_key, session_token, action, payload)
        if result["ok"]:
            _record_health(plugin_key, True)
            entry = _log_entry("SUCCESS", task_description, plugin_key, action)
            result["log"] = entry
            result["discovery"] = {"matched_task": recommended.get("matched_task", ""),
                                   "total_options": response["total_matched"]}
            return result

        _record_health(plugin_key, False)
        return _try_failover(response, session_token, action, payload,
                             task_description, plugin_key, result.get("error", ""))

    entry = _log_entry("NOT_IN_CONNECTOR", task_description, plugin_key,
                       f"{plugin_name} อยู่ใน discovery แต่ยังไม่มีใน connector")
    return {
        "ok": False,
        "stage": "connector",
        "error": f"{plugin_name} ค้นพบแล้วแต่ยังไม่ได้ลงทะเบียนใน plugin_connector",
        "plugin": plugin_name,
        "status": recommended["status"],
        "alternatives": [p["name"] for p in response["available"][1:4]],
        "log": entry,
    }


def _try_failover(response: dict, session_token: str, action: str,
                  payload: dict | None, task_desc: str,
                  failed_key: str, error_msg: str) -> dict:
    alternatives = [p for p in response["available"]
                    if p["key"] != failed_key and not p.get("disabled")]

    for alt in alternatives[:MAX_RETRY]:
        alt_key = alt["key"]
        connector_info = get_plugin_info(alt_key)
        if not connector_info:
            continue

        result = execute_plugin(alt_key, session_token, action, payload)
        if result["ok"]:
            _record_health(alt_key, True)
            entry = _log_entry("FAILOVER_SUCCESS", task_desc, alt_key,
                               f"เปลี่ยนจาก {failed_key} → {alt_key}")
            result["log"] = entry
            result["failover_from"] = failed_key
            return result

        _record_health(alt_key, False)

    entry = _log_entry("ALL_FAILED", task_desc, failed_key,
                       f"ลองทั้งหมดแล้วล้มเหลว: {error_msg}")
    return {
        "ok": False,
        "stage": "failover",
        "error": f"ปลั๊กอินทั้งหมดล้มเหลว (เริ่มจาก {failed_key}): {error_msg}",
        "tried": [failed_key] + [a["key"] for a in alternatives[:MAX_RETRY]],
        "log": entry,
    }


def batch_execute(tasks: list[dict], session_token: str) -> list[dict]:
    """ดำเนินการหลายงานพร้อมกัน"""
    results = []
    for task in tasks:
        desc = task.get("description", "")
        action = task.get("action", "read")
        payload = task.get("payload")
        result = smart_execute(desc, session_token, action, payload)
        result["task_description"] = desc
        results.append(result)
    return results


def Windsor_auto_respond(connector: str = "tiktok_organic",
                         date_range: str = "last_7_days") -> dict:
    """Windsor.ai Auto-Response — ดึงข้อมูลอัตโนมัติ
    ไม่ได้เรียก API จริง เตรียมคำสั่งสำหรับ orchestrator"""
    supported = {
        "tiktok_organic": {
            "name": "Windsor.ai TikTok Organic",
            "fields": ["date", "source", "views", "likes", "comments",
                       "shares", "followers", "video_title"],
            "plugin_key": "windsor_tiktok",
        },
        "instagram": {
            "name": "Windsor.ai Instagram",
            "fields": ["date", "source", "impressions", "reach",
                       "likes", "comments", "followers"],
            "plugin_key": "windsor_social",
        },
        "facebook_organic": {
            "name": "Windsor.ai Facebook Organic",
            "fields": ["date", "source", "impressions", "reach",
                       "reactions", "comments", "shares"],
            "plugin_key": "windsor_social",
        },
        "youtube": {
            "name": "Windsor.ai YouTube",
            "fields": ["date", "source", "views", "watch_time",
                       "likes", "comments", "subscribers"],
            "plugin_key": "windsor_social",
        },
    }

    info = supported.get(connector)
    if not info:
        return {
            "ok": False,
            "error": f"Connector ไม่รองรับ: {connector}",
            "supported": list(supported.keys()),
        }

    return {
        "ok": True,
        "connector": connector,
        "name": info["name"],
        "plugin_key": info["plugin_key"],
        "date_range": date_range,
        "fields": info["fields"],
        "auto_response": True,
        "instruction": f"เรียก Windsor get_data(connector={connector}, "
                       f"date_range_type={date_range}, fields={info['fields']})",
    }


def _record_health(plugin_key: str, success: bool):
    comp = _pipeline_monitor.components.get(plugin_key)
    if not comp:
        comp = _pipeline_monitor.register(plugin_key)
    if success:
        comp.report_ok()
    else:
        comp.report_error(f"execute failed at {datetime.now(timezone.utc).isoformat()}")


def _log_entry(status: str, task: str, plugin_key: str | None, detail: str) -> dict:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "task": task[:100],
        "plugin": plugin_key,
        "detail": detail[:200],
    }
    _pipeline_log.append(entry)
    if len(_pipeline_log) > 1000:
        _pipeline_log.pop(0)
    return entry


def pipeline_report() -> dict:
    health = _pipeline_monitor.generate_report()
    discovery = health_summary()

    success = sum(1 for e in _pipeline_log if e["status"] == "SUCCESS")
    failover = sum(1 for e in _pipeline_log if e["status"] == "FAILOVER_SUCCESS")
    failed = sum(1 for e in _pipeline_log if e["status"] in ("ALL_FAILED", "NO_MATCH"))

    return {
        "pipeline_health": health,
        "discovery": discovery,
        "execution_stats": {
            "total_requests": len(_pipeline_log),
            "success": success,
            "failover_success": failover,
            "failed": failed,
            "success_rate": f"{(success + failover) / max(len(_pipeline_log), 1) * 100:.1f}%",
        },
        "recent_log": _pipeline_log[-10:],
    }


def clear_log():
    _pipeline_log.clear()
