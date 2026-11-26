"""Discovery Engine — ค้นพบ Tool ใหม่ ห้าม auto full access"""

from .tool_classification import classify_tool
from .risk_levels import assess_risk


def discover_tool(tool_name, tool_type, provider, gateway):
    """
    NEW TOOL → DISCOVER → REGISTER METADATA → CLASSIFY →
    RISK CHECK → PERMISSION CHECK → QUARANTINE → APPROVAL → ENABLE
    """
    classification = classify_tool(tool_type)
    risk = assess_risk(classification)
    return {
        "tool_name": tool_name,
        "provider": provider,
        "gateway": gateway,
        "classification": classification,
        "risk_level": risk["level"],
        "risk_policy": risk["policy"],
        "state": "quarantined",
        "note": "ห้าม DISCOVER → AUTO FULL ACCESS — ต้องผ่าน approval",
    }


def approve_tool(tool_record, approved_by="owner"):
    tool_record["state"] = "enabled"
    tool_record["approved_by"] = approved_by
    return tool_record
