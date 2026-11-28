"""Plugin Validator — ตรวจสอบปลั๊กอินก่อนลงทะเบียน"""

ALLOWED_RISK_LEVELS = ("R1", "R2", "R3", "R4", "R5")
ALLOWED_CATEGORIES = (
    "ai", "analytics", "social", "ads", "ecommerce", "email",
    "productivity", "storage", "design", "video", "data", "crm",
    "security", "publishing", "transcription", "image", "research",
    "general",
)
MAX_CAPABILITIES = 20
MAX_NAME_LENGTH = 120


class PluginValidationError(Exception):
    pass


def validate_plugin(plugin_id: str, name: str, category: str = "general",
                    risk_level: str = "R1", capabilities: tuple | list = (),
                    requires_auth: bool = False, **_extra) -> dict:
    errors = []

    if not plugin_id or not isinstance(plugin_id, str):
        errors.append("plugin_id is required and must be a string")
    elif len(plugin_id) > 128:
        errors.append("plugin_id must be <= 128 characters")

    if not name or not isinstance(name, str):
        errors.append("name is required and must be a string")
    elif len(name) > MAX_NAME_LENGTH:
        errors.append(f"name must be <= {MAX_NAME_LENGTH} characters")

    if category not in ALLOWED_CATEGORIES:
        errors.append(f"category '{category}' not in allowed list")

    if risk_level not in ALLOWED_RISK_LEVELS:
        errors.append(f"risk_level '{risk_level}' not in {ALLOWED_RISK_LEVELS}")

    if len(capabilities) > MAX_CAPABILITIES:
        errors.append(f"max {MAX_CAPABILITIES} capabilities allowed")

    if risk_level in ("R4", "R5") and not requires_auth:
        errors.append("high-risk plugins (R4/R5) must require auth")

    return {"valid": len(errors) == 0, "errors": errors}


def check_duplicate(registry, plugin_id: str) -> bool:
    return registry.get(plugin_id) is not None


def validate_and_register(registry, plugin_id: str, name: str, **kwargs) -> dict:
    validation = validate_plugin(plugin_id, name, **kwargs)
    if not validation["valid"]:
        return {"ok": False, "errors": validation["errors"]}
    if check_duplicate(registry, plugin_id):
        return {"ok": False, "errors": ["duplicate plugin_id"]}
    return registry.register(plugin_id, name, **kwargs)
