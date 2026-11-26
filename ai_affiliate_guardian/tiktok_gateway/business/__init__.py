"""TikTok Business API Gateway"""


def get_status():
    return {
        "gateway": "tiktok_business_api",
        "documented": True,
        "authorized": False,
        "connected": False,
        "capabilities": [
            "campaign_management",
            "ad_management",
            "audience_management",
            "reporting",
            "creative_management",
        ],
    }
