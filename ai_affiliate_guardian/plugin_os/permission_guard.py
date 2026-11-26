"""Permission Guard — ตรวจสิทธิ์ตาม risk level"""

from .risk_levels import assess_risk, is_safe
from .tool_classification import classify_tool


def check_permission(tool_type, has_approval=False):
    tool_class = classify_tool(tool_type)
    risk = assess_risk(tool_class)
    level = risk["level"]

    if is_safe(level):
        return True, f"{level}: {risk['policy']}"

    if level == "R2":
        return True, f"{level}: controlled — ตรวจก่อนใช้"

    if not has_approval:
        return False, f"{level}: {risk['policy']} — ยังไม่มีอนุมัติ"

    return True, f"{level}: อนุมัติแล้ว"


def guard_ads_safety(action, has_evidence=False, has_policy=False, has_approval=False):
    """
    TikTok Ads MCP Safety:
    AI recommendation → Evidence → Policy → Human Approval → MCP Tool → Validate → Audit
    ห้าม AI recommendation → budget change โดยตรง
    """
    if not has_evidence:
        return False, "ต้องมี evidence ก่อน"
    if not has_policy:
        return False, "ต้องผ่าน policy check"
    if not has_approval:
        return False, "ต้องได้รับอนุมัติจากเจ้าของ"
    return True, f"อนุมัติ action: {action}"
