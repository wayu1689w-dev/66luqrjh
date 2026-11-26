"""Capability Registry — Spec sections 14-15
ลงทะเบียน Tool ที่แต่ละ Plugin มี และจำแนกประเภท + Risk"""

from enum import Enum

_counter = 0
_capabilities = {}


class ToolClass(Enum):
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    ADMIN = "ADMIN"
    FINANCE = "FINANCE"
    PUBLISH = "PUBLISH"
    ANALYZE = "ANALYZE"


TOOL_CLASS_RISK = {
    ToolClass.READ: "R1",
    ToolClass.ANALYZE: "R0",
    ToolClass.WRITE: "R3",
    ToolClass.DELETE: "R3",
    ToolClass.PUBLISH: "R4",
    ToolClass.ADMIN: "R5",
    ToolClass.FINANCE: "R5",
}


def _next_id():
    global _counter
    _counter += 1
    return f"CAP-{_counter:06d}"


def register(plugin_id, tool_name, tool_class, description="",
             requires_approval=None):
    cap_id = _next_id()
    risk = TOOL_CLASS_RISK.get(tool_class, "R3")

    if requires_approval is None:
        requires_approval = risk in ("R3", "R4", "R5")

    cap = {
        "cap_id": cap_id,
        "plugin_id": plugin_id,
        "tool_name": tool_name,
        "tool_class": tool_class.value if isinstance(tool_class, ToolClass) else tool_class,
        "risk": risk,
        "description": description,
        "requires_approval": requires_approval,
        "enabled": True,
    }
    _capabilities[cap_id] = cap
    return cap


def get(cap_id):
    return _capabilities.get(cap_id)


def list_by_plugin(plugin_id):
    return [c for c in _capabilities.values()
            if c["plugin_id"] == plugin_id]


def list_by_class(tool_class):
    tc = tool_class.value if isinstance(tool_class, ToolClass) else tool_class
    return [c for c in _capabilities.values()
            if c["tool_class"] == tc]


def list_by_risk(risk_level):
    return [c for c in _capabilities.values()
            if c["risk"] == risk_level]


def disable(cap_id):
    cap = _capabilities.get(cap_id)
    if cap:
        cap["enabled"] = False
    return cap


def enable(cap_id):
    cap = _capabilities.get(cap_id)
    if cap:
        cap["enabled"] = True
    return cap


def is_enabled(cap_id):
    cap = _capabilities.get(cap_id)
    return cap["enabled"] if cap else False


def reset():
    global _counter
    _counter = 0
    _capabilities.clear()
