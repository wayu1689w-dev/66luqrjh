"""Plugin Auto-Discovery & Auto-Response System
ค้นหาปลั๊กอินอัตโนมัติ จับคู่งานกับปลั๊กอิน และตอบรับอัตโนมัติ
ใช้ร่วมกับ plugin_connector.py + v008 Security"""

from datetime import datetime, timezone


EXTENDED_REGISTRY = {
    "claude": {"name": "Claude", "cat": "ai_text", "risk": "R1", "status": "connected"},
    "chatgpt_work": {"name": "ChatGPT Work", "cat": "ai_text", "risk": "R1", "status": "connected"},
    "grokbot": {"name": "GrokBot", "cat": "ai_text", "risk": "R1", "status": "connected"},
    "gemini_ai": {"name": "Gemini AI", "cat": "ai_multimodal", "risk": "R2", "status": "connected"},
    "meta_ai": {"name": "Meta AI", "cat": "ai_multimodal", "risk": "R2", "status": "connected"},
    "notion": {"name": "Notion", "cat": "productivity", "risk": "R1", "status": "connected"},
    "google_drive": {"name": "Google Drive", "cat": "storage", "risk": "R1", "status": "connected"},
    "windsor_tiktok": {"name": "Windsor.ai TikTok", "cat": "analytics", "risk": "R2", "status": "connected"},
    "windsor_social": {"name": "Windsor.ai Social Media", "cat": "social_media", "risk": "R2", "status": "connected"},
    "metricool": {"name": "Metricool", "cat": "social_media", "risk": "R2", "status": "connected"},
    "tiktok_business": {"name": "TikTok for Business", "cat": "ads", "risk": "R4", "status": "connected"},
    "canva": {"name": "Canva", "cat": "design", "risk": "R2", "status": "disabled"},
    "figma": {"name": "Figma", "cat": "design", "risk": "R1", "status": "connected"},
    "wordpress": {"name": "WordPress", "cat": "publishing", "risk": "R3", "status": "not_installed"},
    "gmail": {"name": "Gmail", "cat": "communication", "risk": "R3", "status": "needs_reconnect"},
    "google_calendar": {"name": "Google Calendar", "cat": "calendar", "risk": "R2", "status": "needs_reconnect"},
    "outlook_calendar": {"name": "Outlook Calendar", "cat": "calendar", "risk": "R2", "status": "connected"},
    "dropbox": {"name": "Dropbox", "cat": "storage", "risk": "R1", "status": "connected"},
    "supermetrics": {"name": "Supermetrics", "cat": "analytics", "risk": "R2", "status": "connected"},
    "microsoft_365": {"name": "Microsoft 365", "cat": "productivity", "risk": "R2", "status": "connected"},
    "adwhispr": {"name": "AdWhispr Ads", "cat": "ads_research", "risk": "R2", "status": "connected"},
    "aftership": {"name": "AfterShip TikTok Shop", "cat": "commerce", "risk": "R3", "status": "connected"},
    "opusclip": {"name": "OpusClip AI Producer", "cat": "video", "risk": "R2", "status": "connected"},
    "airtable": {"name": "Airtable", "cat": "productivity", "risk": "R1", "status": "connected"},
    "shopify": {"name": "Shopify", "cat": "commerce", "risk": "R3", "status": "connected"},
    "google_docs": {"name": "Google Docs", "cat": "productivity", "risk": "R1", "status": "needs_reconnect"},
    "google_sheets": {"name": "Google Sheets", "cat": "productivity", "risk": "R1", "status": "needs_reconnect"},
    "google_slides": {"name": "Google Slides", "cat": "productivity", "risk": "R1", "status": "needs_reconnect"},
    "claude_academy": {"name": "Claude Academy", "cat": "learning", "risk": "R0", "status": "connected"},
    "configure_memory": {"name": "Configure Memory", "cat": "memory", "risk": "R1", "status": "connected"},
    "common_room": {"name": "Common Room", "cat": "gtm", "risk": "R2", "status": "connected"},
    "fourthwall": {"name": "Fourthwall", "cat": "commerce", "risk": "R3", "status": "connected"},
    "gemini_crypto": {"name": "Gemini Crypto", "cat": "finance", "risk": "R3", "status": "connected"},
    "jetpost": {"name": "Jetpost", "cat": "communication", "risk": "R2", "status": "connected"},
    "microsoft_learn": {"name": "Microsoft Learn", "cat": "learning", "risk": "R0", "status": "connected"},
    "otter_ai": {"name": "Otter.ai", "cat": "meeting", "risk": "R1", "status": "connected"},
    "vidiq": {"name": "vidIQ", "cat": "video", "risk": "R3", "status": "disabled"},
    # --- Security & Monitoring ---
    "malwarebytes": {"name": "Malwarebytes", "cat": "security", "risk": "R1", "status": "not_installed"},
    "pi_security": {"name": "Pi Security", "cat": "security", "risk": "R2", "status": "not_installed"},
    "datadog": {"name": "Datadog", "cat": "monitoring", "risk": "R2", "status": "not_installed"},
    "drata": {"name": "Drata", "cat": "compliance", "risk": "R2", "status": "not_installed"},
    "reco": {"name": "Reco SaaS Security", "cat": "security", "risk": "R2", "status": "not_installed"},
    "sprinto": {"name": "Sprinto", "cat": "compliance", "risk": "R2", "status": "not_installed"},
    "blockscout": {"name": "Blockscout", "cat": "blockchain", "risk": "R1", "status": "not_installed"},
    # --- Ads & Marketing ---
    "adspirer_ads": {"name": "Adspirer Ads", "cat": "ads", "risk": "R4", "status": "connect_incomplete"},
    "adspirer_retail": {"name": "Adspirer Retail Media", "cat": "ads", "risk": "R4", "status": "connect_incomplete"},
    "adspirer_social": {"name": "Adspirer Social Ads", "cat": "ads", "risk": "R4", "status": "connect_incomplete"},
    "adspirer_analytics": {"name": "Adspirer Marketing Analytics", "cat": "analytics", "risk": "R2", "status": "not_installed"},
    "motion_creative": {"name": "Motion Creative Analytics", "cat": "ads_research", "risk": "R2", "status": "not_installed"},
    "eulerian": {"name": "Eulerian Marketing Platform", "cat": "analytics", "risk": "R2", "status": "not_installed"},
    "campaign_monitor": {"name": "Campaign Monitor", "cat": "email_marketing", "risk": "R3", "status": "not_installed"},
    "mailchimp": {"name": "Intuit Mailchimp", "cat": "email_marketing", "risk": "R3", "status": "connect_incomplete"},
    "ordinal": {"name": "Ordinal LinkedIn", "cat": "social_media", "risk": "R2", "status": "not_installed"},
    # --- CRM ---
    "hubspot": {"name": "HubSpot", "cat": "crm", "risk": "R2", "status": "not_connected"},
    "affinity": {"name": "Affinity", "cat": "crm", "risk": "R2", "status": "connect_incomplete"},
    "zoho_crm": {"name": "Zoho CRM", "cat": "crm", "risk": "R2", "status": "not_installed"},
    "supersei": {"name": "Supersei CRM", "cat": "crm", "risk": "R2", "status": "not_installed"},
    "nutshell": {"name": "Nutshell CRM", "cat": "crm", "risk": "R2", "status": "not_installed"},
    # --- Project Management ---
    "asana": {"name": "Asana", "cat": "project_mgmt", "risk": "R2", "status": "not_connected"},
    "linear": {"name": "Linear", "cat": "project_mgmt", "risk": "R2", "status": "not_connected"},
    "atlassian": {"name": "Atlassian (Jira/Confluence)", "cat": "project_mgmt", "risk": "R2", "status": "connect_incomplete"},
    "hive": {"name": "Hive", "cat": "project_mgmt", "risk": "R2", "status": "not_installed"},
    # --- Design & Media ---
    "picsart": {"name": "Picsart Media Studio", "cat": "video", "risk": "R2", "status": "connect_incomplete"},
    "getty_images": {"name": "Getty Images", "cat": "media", "risk": "R2", "status": "not_installed"},
    "moda": {"name": "Moda Slides & Designs", "cat": "design", "risk": "R2", "status": "not_installed"},
    "beautiful_ai": {"name": "Beautiful.ai", "cat": "design", "risk": "R2", "status": "not_installed"},
    "orshot": {"name": "Orshot Video Automation", "cat": "video", "risk": "R2", "status": "not_installed"},
    "ayrshare": {"name": "Ayrshare Social API", "cat": "social_media", "risk": "R3", "status": "not_installed"},
    # --- Communication ---
    "slack": {"name": "Slack", "cat": "communication", "risk": "R3", "status": "connect_incomplete"},
    "webex": {"name": "Webex", "cat": "meeting", "risk": "R2", "status": "connect_incomplete"},
    "granola": {"name": "Granola", "cat": "meeting", "risk": "R1", "status": "not_connected"},
    "read_ai": {"name": "Read AI", "cat": "meeting", "risk": "R1", "status": "connect_incomplete"},
    # --- Analytics & Data ---
    "mixpanel": {"name": "Mixpanel", "cat": "analytics", "risk": "R2", "status": "connect_incomplete"},
    "omni_analytics": {"name": "Omni Analytics", "cat": "analytics", "risk": "R2", "status": "connect_incomplete"},
    "polar_analytics": {"name": "Polar Analytics", "cat": "analytics", "risk": "R2", "status": "connect_incomplete"},
    "zoho_analytics": {"name": "Zoho Analytics", "cat": "analytics", "risk": "R2", "status": "not_installed"},
    "adobe_cja": {"name": "Adobe Customer Journey", "cat": "analytics", "risk": "R2", "status": "not_installed"},
    # --- Commerce & Finance ---
    "sparxx": {"name": "spArxx.io Blockchain Timestamp", "cat": "blockchain", "risk": "R2", "status": "not_installed"},
    "crypto_com": {"name": "Crypto.com", "cat": "finance", "risk": "R3", "status": "not_installed"},
    "nansen": {"name": "Nansen Crypto Analytics", "cat": "finance", "risk": "R2", "status": "not_installed"},
    "coingecko": {"name": "CoinGecko", "cat": "finance", "risk": "R1", "status": "not_installed"},
    "plaid": {"name": "Plaid Developer", "cat": "finance", "risk": "R3", "status": "not_installed"},
    "quickbooks": {"name": "QuickBooks", "cat": "finance", "risk": "R3", "status": "not_installed"},
    "stripe": {"name": "Stripe", "cat": "finance", "risk": "R3", "status": "not_installed"},
    # --- Infrastructure & Dev ---
    "cloudflare": {"name": "Cloudflare", "cat": "infrastructure", "risk": "R3", "status": "not_installed"},
    "cloudbees": {"name": "CloudBees CI/CD", "cat": "infrastructure", "risk": "R3", "status": "not_installed"},
    "quicknode": {"name": "QuickNode Blockchain", "cat": "blockchain", "risk": "R3", "status": "not_installed"},
    "cdata": {"name": "CData Connect AI", "cat": "data_platform", "risk": "R2", "status": "not_installed"},
    "lovable": {"name": "Lovable", "cat": "development", "risk": "R2", "status": "disconnected"},
    "hostinger": {"name": "Hostinger", "cat": "infrastructure", "risk": "R3", "status": "not_installed"},
    # --- Website ---
    "b12_website": {"name": "B12 Website Generator", "cat": "website", "risk": "R2", "status": "not_installed"},
    "weinc": {"name": "WeInc Website", "cat": "website", "risk": "R2", "status": "not_installed"},
    # --- Document & Knowledge ---
    "scite": {"name": "Scite Research", "cat": "research", "risk": "R1", "status": "connect_incomplete"},
    "wisdom_ai": {"name": "WisdomAI", "cat": "knowledge", "risk": "R1", "status": "connect_incomplete"},
    "infobip": {"name": "Infobip Docs", "cat": "knowledge", "risk": "R0", "status": "not_installed"},
    "mastercard_dev": {"name": "Mastercard Developers", "cat": "knowledge", "risk": "R0", "status": "not_installed"},
    # --- Other ---
    "meridian": {"name": "Meridian AI", "cat": "deals", "risk": "R2", "status": "connect_incomplete"},
    "metaview": {"name": "Metaview Recruiting", "cat": "recruiting", "risk": "R2", "status": "connect_incomplete"},
    "gem": {"name": "Gem Recruiting", "cat": "recruiting", "risk": "R2", "status": "connect_incomplete"},
    "gainsight": {"name": "Gainsight", "cat": "customer_success", "risk": "R2", "status": "connect_incomplete"},
    "pliant": {"name": "Pliant Corporate Cards", "cat": "finance", "risk": "R3", "status": "connect_incomplete"},
    "ambiguous": {"name": "Ambiguous Workspace", "cat": "productivity", "risk": "R2", "status": "not_installed"},
    "intuit_dev": {"name": "Intuit Developer", "cat": "development", "risk": "R2", "status": "not_installed"},
    "theysaid": {"name": "Theysaid UX Testing", "cat": "testing", "risk": "R2", "status": "not_installed"},
    # --- SUEA Internal ---
    "suea_security": {"name": "เสือเจาะข้อมูล", "cat": "security_internal", "risk": "R1", "status": "active"},
    "suea_guardian": {"name": "AI Affiliate Guardian", "cat": "core", "risk": "R0", "status": "active"},
    "suea_framecut": {"name": "FrameCut Studio", "cat": "video_internal", "risk": "R1", "status": "active"},
    "suea_community": {"name": "SUEA Community Board", "cat": "community", "risk": "R1", "status": "active"},
}

TASK_PLUGIN_MAP = {
    "text": ["claude", "chatgpt_work", "grokbot", "gemini_ai", "meta_ai"],
    "image": ["gemini_ai", "meta_ai", "opusclip", "picsart", "figma"],
    "video": ["opusclip", "suea_framecut", "picsart", "orshot"],
    "audio": ["otter_ai", "opusclip"],
    "analytics": ["windsor_tiktok", "windsor_social", "supermetrics", "metricool", "adwhispr"],
    "ads": ["tiktok_business", "adwhispr", "adspirer_ads", "adspirer_social", "motion_creative"],
    "social_post": ["metricool", "windsor_social", "ayrshare", "ordinal"],
    "design": ["figma", "canva", "moda", "beautiful_ai"],
    "document": ["notion", "google_docs", "google_sheets", "airtable"],
    "storage": ["google_drive", "dropbox"],
    "commerce": ["shopify", "aftership", "fourthwall"],
    "email": ["gmail", "mailchimp", "campaign_monitor"],
    "calendar": ["google_calendar", "outlook_calendar"],
    "security": ["suea_security", "malwarebytes", "pi_security", "reco"],
    "blockchain": ["blockscout", "sparxx", "gemini_crypto", "coingecko"],
    "meeting": ["otter_ai", "webex", "granola", "read_ai"],
    "crm": ["hubspot", "zoho_crm", "supersei", "nutshell", "affinity"],
    "project": ["asana", "linear", "atlassian", "hive"],
    "learning": ["claude_academy", "microsoft_learn"],
    "research": ["scite", "claude_academy", "adwhispr"],
}

CATEGORIES = sorted(set(v["cat"] for v in EXTENDED_REGISTRY.values()))


def total_count() -> int:
    return len(EXTENDED_REGISTRY)


def count_by_status() -> dict:
    counts: dict[str, int] = {}
    for info in EXTENDED_REGISTRY.values():
        s = info["status"]
        counts[s] = counts.get(s, 0) + 1
    return counts


def search(query: str) -> list[dict]:
    q = query.lower()
    return [
        {"key": k, **v}
        for k, v in EXTENDED_REGISTRY.items()
        if q in k or q in v["name"].lower() or q in v["cat"]
    ]


def search_by_task(task_type: str) -> list[dict]:
    keys = TASK_PLUGIN_MAP.get(task_type, [])
    results = []
    for k in keys:
        info = EXTENDED_REGISTRY.get(k)
        if info:
            results.append({"key": k, **info})
    return results


def list_by_status(status: str) -> list[dict]:
    return [
        {"key": k, **v}
        for k, v in EXTENDED_REGISTRY.items()
        if v["status"] == status
    ]


def list_by_category(category: str) -> list[dict]:
    return [
        {"key": k, **v}
        for k, v in EXTENDED_REGISTRY.items()
        if v["cat"] == category
    ]


def auto_match(task_description: str) -> list[dict]:
    desc = task_description.lower()
    keyword_map = {
        "text": ["เขียน", "สรุป", "แปล", "วิเคราะห์", "text", "write", "summarize"],
        "image": ["รูป", "ภาพ", "image", "photo"],
        "design": ["ออกแบบ", "กราฟิก", "design", "graphic", "layout", "mockup"],
        "video": ["วิดีโอ", "คลิป", "video", "clip", "edit"],
        "audio": ["เสียง", "audio", "voice", "transcript"],
        "analytics": ["วิเคราะห์", "สถิติ", "analytics", "report", "data"],
        "ads": ["โฆษณา", "แอด", "ads", "campaign", "ad"],
        "social_post": ["โพสต์", "post", "social", "schedule"],
        "document": ["เอกสาร", "โน้ต", "doc", "note", "sheet"],
        "storage": ["ไฟล์", "file", "upload", "download", "drive"],
        "commerce": ["สินค้า", "ร้าน", "shop", "product", "order"],
        "email": ["อีเมล", "email", "mail"],
        "calendar": ["นัดหมาย", "ปฏิทิน", "calendar", "event", "meeting"],
        "security": ["ความปลอดภัย", "security", "malware", "scan", "protect"],
        "blockchain": ["บล็อกเชน", "blockchain", "crypto", "token"],
        "meeting": ["ประชุม", "meeting", "transcript"],
        "crm": ["ลูกค้า", "customer", "crm", "lead", "contact"],
        "project": ["โปรเจค", "project", "task", "issue", "sprint"],
        "learning": ["เรียน", "learn", "course", "tutorial"],
        "research": ["วิจัย", "research", "paper", "study"],
    }

    matched_tasks = []
    for task_type, keywords in keyword_map.items():
        if any(kw in desc for kw in keywords):
            matched_tasks.append(task_type)

    if not matched_tasks:
        return []

    results = []
    seen = set()
    for task_type in matched_tasks:
        for plugin in search_by_task(task_type):
            if plugin["key"] not in seen:
                seen.add(plugin["key"])
                plugin["matched_task"] = task_type
                results.append(plugin)

    return results


def auto_respond(task_description: str) -> dict:
    matches = auto_match(task_description)

    available = [m for m in matches if m["status"] in ("connected", "active")]
    needs_setup = [m for m in matches if m["status"] not in ("connected", "active", "disabled")]
    disabled = [m for m in matches if m["status"] == "disabled"]

    best = available[0] if available else None

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": task_description,
        "recommended": best,
        "available": available,
        "needs_setup": needs_setup,
        "disabled": disabled,
        "total_matched": len(matches),
    }


def health_summary() -> dict:
    status_counts = count_by_status()
    return {
        "total_plugins": total_count(),
        "categories": len(CATEGORIES),
        "status": status_counts,
        "connected": status_counts.get("connected", 0),
        "active_internal": status_counts.get("active", 0),
        "needs_reconnect": status_counts.get("needs_reconnect", 0),
        "not_installed": status_counts.get("not_installed", 0),
        "disabled": status_counts.get("disabled", 0),
        "task_types": len(TASK_PLUGIN_MAP),
    }
