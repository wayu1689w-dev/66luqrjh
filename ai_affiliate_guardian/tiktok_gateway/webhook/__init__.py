"""TikTok Shop Webhook Gateway"""


WEBHOOK_EVENTS = [
    "order.status_change",
    "product.status_change",
    "fulfillment.status_change",
    "return.status_change",
    "promotion.status_change",
]


def get_status():
    return {
        "gateway": "tiktok_webhook",
        "documented": True,
        "authorized": False,
        "connected": False,
        "events": WEBHOOK_EVENTS,
    }
