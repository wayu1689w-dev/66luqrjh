"""Plugin State Machine — ทุก plugin ใช้มาตรฐานเดียว"""

from enum import Enum


class PluginState(Enum):
    DISCOVERED = "discovered"
    DOCUMENTATION_VERIFIED = "documentation_verified"
    REGISTERED = "registered"
    DISABLED = "disabled"
    AUTH_REQUIRED = "auth_required"
    AUTHORIZED = "authorized"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    HEALTH_CHECK = "health_check"
    READY = "ready"
    PRODUCTION_READY = "production_ready"
    # Error states
    DEGRADED = "degraded"
    FAILED = "failed"
    BLOCKED = "blocked"
    REVOKED = "revoked"
    QUARANTINED = "quarantined"


TRANSITIONS = {
    PluginState.DISCOVERED: [PluginState.DOCUMENTATION_VERIFIED, PluginState.DISABLED],
    PluginState.DOCUMENTATION_VERIFIED: [PluginState.REGISTERED, PluginState.DISABLED],
    PluginState.REGISTERED: [PluginState.DISABLED, PluginState.AUTH_REQUIRED],
    PluginState.DISABLED: [PluginState.AUTH_REQUIRED, PluginState.REGISTERED],
    PluginState.AUTH_REQUIRED: [PluginState.AUTHORIZED, PluginState.BLOCKED],
    PluginState.AUTHORIZED: [PluginState.CONNECTING, PluginState.REVOKED],
    PluginState.CONNECTING: [PluginState.CONNECTED, PluginState.FAILED],
    PluginState.CONNECTED: [PluginState.HEALTH_CHECK, PluginState.DEGRADED, PluginState.FAILED],
    PluginState.HEALTH_CHECK: [PluginState.READY, PluginState.FAILED, PluginState.DEGRADED],
    PluginState.READY: [PluginState.PRODUCTION_READY, PluginState.DEGRADED, PluginState.FAILED],
    PluginState.PRODUCTION_READY: [PluginState.DEGRADED, PluginState.FAILED, PluginState.REVOKED, PluginState.DISABLED],
    # Recovery from error states
    PluginState.DEGRADED: [PluginState.HEALTH_CHECK, PluginState.FAILED, PluginState.DISABLED],
    PluginState.FAILED: [PluginState.CONNECTING, PluginState.DISABLED, PluginState.QUARANTINED],
    PluginState.BLOCKED: [PluginState.AUTH_REQUIRED, PluginState.DISABLED],
    PluginState.REVOKED: [PluginState.AUTH_REQUIRED, PluginState.DISABLED],
    PluginState.QUARANTINED: [PluginState.DISABLED],
}


def can_transition(current, target):
    return target in TRANSITIONS.get(current, [])


def transition(current, target):
    if not can_transition(current, target):
        raise ValueError(
            f"ไม่สามารถเปลี่ยนสถานะจาก {current.value} เป็น {target.value}"
        )
    return target
