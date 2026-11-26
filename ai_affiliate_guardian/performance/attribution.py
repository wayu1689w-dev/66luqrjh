"""Attribution — ระบุที่มาของ conversion"""


def attribute_conversion(conversion, content_id, channel_id):
    return {
        "conversion_id": conversion.get("id", ""),
        "content_id": content_id,
        "channel_id": channel_id,
        "source": conversion.get("source", "unknown"),
        "value": conversion.get("value", 0),
        "note": "ต้องตรวจสอบกับ TikTok Shop / affiliate dashboard",
    }
