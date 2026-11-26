"""Channel Registry — จัดการ 4 ช่อง TikTok แยกกันสมบูรณ์"""

import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "channels.yaml"


def load_channels():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_channel(channel_id):
    data = load_channels()
    for ch in data["channels"]:
        if ch["id"] == channel_id:
            return ch
    return None


def get_active_channels():
    data = load_channels()
    return [ch for ch in data["channels"] if ch["status"] == "ACTIVE"]


def get_channel_by_slug(slug):
    data = load_channels()
    for ch in data["channels"]:
        if ch["slug"] == slug:
            return ch
    return None


def validate_isolation(channel_id_a, channel_id_b, action):
    data = load_channels()
    rules = data.get("isolation_rules", {})
    if action == "share_content" and rules.get("cross_channel_content") == "FORBIDDEN":
        return False, "ห้ามแชร์คอนเทนต์ข้ามช่อง"
    if action == "share_script" and rules.get("shared_script") == "FORBIDDEN":
        return False, "ห้ามใช้สคริปต์ร่วมกัน"
    if action == "share_metrics" and rules.get("shared_metrics") == "FORBIDDEN":
        return False, "ห้ามรวมสถิติข้ามช่อง"
    return True, "อนุญาต"
