"""Content Identity — ตัวตนคอนเทนต์แต่ละชิ้น"""

import uuid
from datetime import datetime, timezone


def create_content_id(channel_id, product_id):
    return f"cnt_{channel_id}_{product_id}_{uuid.uuid4().hex[:8]}"


def create_content_record(channel_id, product_id, angle, script):
    return {
        "id": create_content_id(channel_id, product_id),
        "channel_id": channel_id,
        "product_id": product_id,
        "angle": angle,
        "script": script,
        "state": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "version": 1,
    }
