"""Measurement Workflow — วัดผลหลังเผยแพร่"""


def run_measurement(content_id, channel_id, raw_metrics):
    return {
        "content_id": content_id,
        "channel_id": channel_id,
        "metrics": raw_metrics,
        "note": "ข้อมูลจาก Windsor/TikTok — ต้องตรวจสอบก่อนใช้",
        "action": "record_and_compare",
    }
