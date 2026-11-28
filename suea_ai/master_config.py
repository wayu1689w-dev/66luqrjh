"""SUEA_AI_MASTER — Master Configuration v008 LOCKDOWN"""

import json
from pathlib import Path

MASTER_CONFIG = {
    "system": "SUEA_AI_MASTER",
    "target_version": "008",
    "requested_mode": "LOCKDOWN",
    "owner_control": True,
    "private_mode": True,
    "plugin_capacity_target": 10000,
    "auto_discovery": True,
    "auto_ack": True,
    "auto_kpi": True,
    "auto_recovery": True,
    "auto_failover": True,
    "auto_checkpoint": True,
    "duplicate_protection": True,
    "heartbeat_seconds": 30,
    "report_interval_minutes": 30,
    "backup_interval_minutes": 30,
    "runtime_target": "24/7",
    "meta_ai_adapter_enabled": False,
    "external_connections_allowed": False,
    "external_ack_allowed": False,
    "auto_execution_allowed": False,
    "auto_spending_allowed": False,
    "free_mode_only": True,
    "billing_enabled": False,
    "quota_bypass": False,
    "preserve_original_data": True,
    "copy_only": True,
    "source_write": False,
    "public_access": False,
    "auto_publish": False,
    "kill_all_external": True,
    "modules": {
        "universal_gateway": "BLOCKED",
        "meta_ai_adapter": "BLOCKED",
        "affiliate": "BLOCKED",
        "plugin_registry": "ACTIVE",
        "security_guardian": "ACTIVE",
        "emergency_lockdown": "ACTIVE",
        "kpi_engine": "ACTIVE",
        "ack_validator": "ACTIVE",
        "backup_worker": "ACTIVE",
        "windsor": "ACTIVE",
        "metricool": "ACTIVE",
        "tiktok_ads": "ACTIVE",
    },
    "connection_policy": {
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
    },
    "pending_work_reviewed": False,
    "lockdown_verified": False,
    "production_ready": False,
    "max_concurrent_plugins": 50,
    "max_concurrent_tasks": 100,
    "max_retry_per_task": 3,
    "circuit_breaker_threshold": 5,
    "circuit_breaker_recovery_seconds": 60,
}


def get_master_config() -> dict:
    return dict(MASTER_CONFIG)


def is_lockdown() -> bool:
    return MASTER_CONFIG["requested_mode"] == "LOCKDOWN"


def is_action_allowed(action: str) -> bool:
    blocked = {
        "spend", "billing", "publish", "oauth_grant",
        "external_share", "permission_change", "ad_create",
        "commerce_write", "source_write", "quota_bypass",
    }
    return action.lower() not in blocked


def validate_config() -> dict:
    errors = []
    if MASTER_CONFIG["billing_enabled"]:
        errors.append("billing_enabled must be False in LOCKDOWN")
    if MASTER_CONFIG["auto_spending_allowed"]:
        errors.append("auto_spending_allowed must be False in LOCKDOWN")
    if MASTER_CONFIG["public_access"]:
        errors.append("public_access must be False in LOCKDOWN")
    if MASTER_CONFIG["source_write"]:
        errors.append("source_write must be False in LOCKDOWN")
    if not MASTER_CONFIG["owner_control"]:
        errors.append("owner_control must be True in LOCKDOWN")
    return {"valid": len(errors) == 0, "errors": errors}
