"""Version Control — ติดตามเวอร์ชันสื่อ"""

from datetime import datetime, timezone


def create_version(content_id, version_number, changes=""):
    return {
        "content_id": content_id,
        "version": version_number,
        "changes": changes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def bump_version(current_version):
    return current_version + 1
