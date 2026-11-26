"""Connection Manager — จัดการการเชื่อมต่อ ห้าม auto-connect"""


def request_connection(plugin_id, gateway, method="oauth"):
    return {
        "plugin_id": plugin_id,
        "gateway": gateway,
        "method": method,
        "state": "pending_approval",
        "note": "ต้องได้รับอนุมัติจากเจ้าของก่อนเชื่อมต่อ",
    }


def verify_connection(plugin_id, health_result):
    if health_result.get("status") == "ok":
        return {"plugin_id": plugin_id, "state": "connected", "healthy": True}
    return {
        "plugin_id": plugin_id,
        "state": "failed",
        "healthy": False,
        "error": health_result.get("error", "unknown"),
    }
