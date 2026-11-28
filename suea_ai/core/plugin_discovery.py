"""Plugin Auto-Discovery — ค้นหาปลั๊กอินที่รองรับจาก catalog"""

from datetime import datetime, timezone, timedelta

TZ_BKK = timezone(timedelta(hours=7))

TASK_PLUGIN_MAP = {
    "text_generation": ["claude", "openai", "gemini", "grok", "meta_ai"],
    "image_generation": ["openai_dalle", "gemini_imagen", "canva"],
    "video_editing": ["opusclip", "framecut"],
    "analytics": ["windsor", "metricool", "supermetrics", "google_analytics"],
    "ads_management": ["tiktok_ads", "meta_ads", "google_ads"],
    "social_media": ["metricool", "tiktok_organic", "instagram", "facebook_organic", "youtube"],
    "affiliate": ["tiktok_shop", "aftership"],
    "email": ["gmail", "outlook"],
    "calendar": ["google_calendar", "outlook_calendar"],
    "storage": ["google_drive", "dropbox", "notion"],
    "design": ["canva", "figma"],
    "crm": ["hubspot", "salesforce"],
    "ecommerce": ["shopify", "tiktok_shop", "amazon"],
    "code": ["claude", "openai", "gemini"],
    "research": ["claude", "gemini", "grok", "perplexity"],
    "transcription": ["whisper", "otter"],
    "translation": ["claude", "openai", "gemini"],
    "data_pipeline": ["windsor", "supermetrics", "google_sheets"],
    "security": ["malwarebytes", "blockscout"],
    "publishing": ["wordpress", "metricool"],
}

PLUGIN_CATALOG = {
    "claude": {"name": "Claude (Anthropic)", "type": "ai", "free_tier": True},
    "openai": {"name": "OpenAI GPT", "type": "ai", "free_tier": False},
    "gemini": {"name": "Google Gemini", "type": "ai", "free_tier": True},
    "grok": {"name": "GrokBot (xAI)", "type": "ai", "free_tier": True},
    "meta_ai": {"name": "Meta AI", "type": "ai", "free_tier": True},
    "windsor": {"name": "Windsor.ai", "type": "analytics", "free_tier": True},
    "metricool": {"name": "Metricool", "type": "social", "free_tier": True},
    "tiktok_ads": {"name": "TikTok Ads Manager", "type": "ads", "free_tier": True},
    "tiktok_organic": {"name": "TikTok Organic", "type": "social", "free_tier": True},
    "tiktok_shop": {"name": "TikTok Shop", "type": "ecommerce", "free_tier": True},
    "instagram": {"name": "Instagram", "type": "social", "free_tier": True},
    "facebook_organic": {"name": "Facebook Organic", "type": "social", "free_tier": True},
    "youtube": {"name": "YouTube", "type": "social", "free_tier": True},
    "google_drive": {"name": "Google Drive", "type": "storage", "free_tier": True},
    "google_sheets": {"name": "Google Sheets", "type": "data", "free_tier": True},
    "google_calendar": {"name": "Google Calendar", "type": "productivity", "free_tier": True},
    "google_analytics": {"name": "Google Analytics 4", "type": "analytics", "free_tier": True},
    "gmail": {"name": "Gmail", "type": "email", "free_tier": True},
    "notion": {"name": "Notion", "type": "productivity", "free_tier": True},
    "dropbox": {"name": "Dropbox", "type": "storage", "free_tier": True},
    "canva": {"name": "Canva", "type": "design", "free_tier": True},
    "figma": {"name": "Figma", "type": "design", "free_tier": True},
    "opusclip": {"name": "OpusClip", "type": "video", "free_tier": True},
    "framecut": {"name": "FrameCut Studio", "type": "video", "free_tier": True},
    "aftership": {"name": "AfterShip Channels", "type": "ecommerce", "free_tier": True},
    "shopify": {"name": "Shopify", "type": "ecommerce", "free_tier": False},
    "hubspot": {"name": "HubSpot", "type": "crm", "free_tier": True},
    "salesforce": {"name": "Salesforce", "type": "crm", "free_tier": False},
    "supermetrics": {"name": "Supermetrics", "type": "analytics", "free_tier": False},
    "wordpress": {"name": "WordPress", "type": "publishing", "free_tier": True},
    "malwarebytes": {"name": "Malwarebytes", "type": "security", "free_tier": True},
    "blockscout": {"name": "Blockscout", "type": "security", "free_tier": True},
    "whisper": {"name": "OpenAI Whisper", "type": "transcription", "free_tier": False},
    "otter": {"name": "Otter.ai", "type": "transcription", "free_tier": True},
    "perplexity": {"name": "Perplexity", "type": "research", "free_tier": True},
    "outlook": {"name": "Microsoft Outlook", "type": "email", "free_tier": True},
    "outlook_calendar": {"name": "Outlook Calendar", "type": "productivity", "free_tier": True},
    "meta_ads": {"name": "Meta Ads", "type": "ads", "free_tier": True},
    "google_ads": {"name": "Google Ads", "type": "ads", "free_tier": True},
    "amazon": {"name": "Amazon Seller", "type": "ecommerce", "free_tier": False},
    "openai_dalle": {"name": "DALL-E", "type": "image", "free_tier": False},
    "gemini_imagen": {"name": "Gemini Imagen", "type": "image", "free_tier": True},
    "linkedin_organic": {"name": "LinkedIn Organic", "type": "social", "free_tier": True},
    "linkedin_ads": {"name": "LinkedIn Ads", "type": "ads", "free_tier": False},
    "threads": {"name": "Threads", "type": "social", "free_tier": True},
    "airtable": {"name": "Airtable", "type": "data", "free_tier": True},
}


def discover_for_task(task_type: str) -> list:
    plugin_ids = TASK_PLUGIN_MAP.get(task_type, [])
    results = []
    for pid in plugin_ids:
        info = PLUGIN_CATALOG.get(pid)
        if info:
            results.append({"plugin_id": pid, **info})
    return results


def discover_free_only() -> list:
    return [
        {"plugin_id": pid, **info}
        for pid, info in PLUGIN_CATALOG.items()
        if info.get("free_tier")
    ]


def search_catalog(query: str) -> list:
    q = query.lower()
    return [
        {"plugin_id": pid, **info}
        for pid, info in PLUGIN_CATALOG.items()
        if q in pid or q in info["name"].lower() or q in info["type"]
    ]


def get_all_task_types() -> list:
    return sorted(TASK_PLUGIN_MAP.keys())


def get_catalog_stats() -> dict:
    by_type: dict[str, int] = {}
    free_count = 0
    for info in PLUGIN_CATALOG.values():
        by_type[info["type"]] = by_type.get(info["type"], 0) + 1
        if info.get("free_tier"):
            free_count += 1
    return {
        "total": len(PLUGIN_CATALOG),
        "free_tier": free_count,
        "paid_only": len(PLUGIN_CATALOG) - free_count,
        "task_types": len(TASK_PLUGIN_MAP),
        "by_type": by_type,
    }
