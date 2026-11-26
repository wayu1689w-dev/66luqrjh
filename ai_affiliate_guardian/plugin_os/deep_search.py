"""Deep Search — ค้นลึกที่สุดเท่าที่สิทธิ์อนุญาต"""

SEARCH_LAYERS = [
    "public",
    "official",
    "authorized_apis",
    "authorized_mcp",
    "authorized_account_data",
    "STOP_AT_PERMISSION_BOUNDARY",
]

FORBIDDEN = [
    "permission_bypass",
    "authentication_bypass",
    "unauthorized_account_access",
    "private_data_scraping",
]


def search(query, max_layer="authorized_account_data", permissions=None):
    permissions = permissions or []
    accessible_layers = []
    for layer in SEARCH_LAYERS:
        if layer == "STOP_AT_PERMISSION_BOUNDARY":
            break
        if layer in ("public", "official"):
            accessible_layers.append(layer)
        elif layer in permissions:
            accessible_layers.append(layer)
        else:
            break
    return {
        "query": query,
        "searched_layers": accessible_layers,
        "stopped_at": accessible_layers[-1] if accessible_layers else "none",
        "note": "หยุดที่ขอบเขตสิทธิ์ — ไม่ bypass",
    }


def validate_search_action(action):
    if action in FORBIDDEN:
        return False, f"ห้าม: {action}"
    return True, "อนุญาต"
