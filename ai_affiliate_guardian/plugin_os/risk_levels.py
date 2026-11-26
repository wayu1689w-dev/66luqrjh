"""Risk Levels — R0 ถึง R5"""

from .tool_classification import ToolClass


RISK_MAP = {
    ToolClass.SEARCH: "R1",
    ToolClass.READ: "R1",
    ToolClass.ANALYZE: "R0",
    ToolClass.GENERATE: "R2",
    ToolClass.DRAFT: "R2",
    ToolClass.CREATE: "R3",
    ToolClass.UPDATE: "R3",
    ToolClass.PUBLISH: "R4",
    ToolClass.SEND: "R4",
    ToolClass.DELETE: "R3",
    ToolClass.COMMERCE: "R5",
    ToolClass.FINANCE: "R5",
    ToolClass.ADS: "R5",
    ToolClass.IDENTITY: "R5",
    ToolClass.ADMIN: "R5",
}

RISK_POLICIES = {
    "R0": "policy may auto-allow — local computation",
    "R1": "policy may auto-allow — external read",
    "R2": "controlled — draft/local changes",
    "R3": "approval required — external write",
    "R4": "explicit approval required — publish/send",
    "R5": "strongest approval required — finance/ads/permission/admin",
}


def assess_risk(tool_class):
    level = RISK_MAP.get(tool_class, "R5")
    policy = RISK_POLICIES.get(level, "unknown")
    return {"level": level, "policy": policy}


def is_safe(risk_level):
    return risk_level in ("R0", "R1")
