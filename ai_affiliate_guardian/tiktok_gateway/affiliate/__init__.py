"""TikTok Shop Affiliate Gateway"""


def get_status():
    return {
        "gateway": "tiktok_affiliate",
        "documented": True,
        "authorized": False,
        "connected": False,
        "capabilities": [
            "affiliate_link_management",
            "commission_tracking",
            "creator_collaboration",
            "affiliate_analytics",
        ],
    }
