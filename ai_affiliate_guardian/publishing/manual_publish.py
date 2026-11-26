"""Manual Publish — เผยแพร่ด้วยมือเท่านั้น ห้าม auto"""

from ..approval.approval_gate import is_approved
from datetime import datetime, timezone


def prepare_for_publish(content):
    content_id = content.get("id", "")
    if not is_approved(content_id, "content_publish"):
        return {
            "ready": False,
            "reason": "ยังไม่ได้รับอนุมัติ",
        }
    return {
        "ready": True,
        "content_id": content_id,
        "channel_id": content.get("channel_id"),
        "script": content.get("script"),
        "caption": content.get("caption"),
        "hashtags": content.get("hashtags"),
        "note": "พร้อมเผยแพร่ — ต้องกดเผยแพร่ด้วยมือ",
        "prepared_at": datetime.now(timezone.utc).isoformat(),
    }
