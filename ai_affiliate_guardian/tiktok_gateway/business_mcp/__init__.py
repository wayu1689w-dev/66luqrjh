"""TikTok Business MCP Gateway — Progressive Disclosure แนะนำ"""

DISCLOSURE_STRATEGY = "progressive"

CORE_TOOLS_COUNT = 40
FULL_TOOLS_COUNT = 400


def get_status():
    return {
        "gateway": "tiktok_business_mcp",
        "documented": True,
        "authorized": False,
        "connected": False,
        "strategy": DISCLOSURE_STRATEGY,
        "core_tools": CORE_TOOLS_COUNT,
        "full_tools": FULL_TOOLS_COUNT,
        "note": "Progressive Disclosure — 40 core tools ก่อน, discover เพิ่มเมื่อจำเป็น",
        "safety": {
            "ads_write": "REQUIRES_HUMAN_APPROVAL",
            "budget_change": "REQUIRES_EVIDENCE_POLICY_APPROVAL",
            "campaign_create": "REQUIRES_HUMAN_APPROVAL",
            "audience_change": "REQUIRES_HUMAN_APPROVAL",
        },
    }
