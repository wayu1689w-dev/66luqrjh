"""Channel Analysis — วิเคราะห์ผลรายช่อง"""


def summarize_channel(channel_id, metrics_list):
    if not metrics_list:
        return {"channel_id": channel_id, "total_views": 0, "total_clicks": 0, "note": "ยังไม่มีข้อมูล"}
    total_views = sum(m.get("views", 0) for m in metrics_list)
    total_clicks = sum(m.get("clicks", 0) for m in metrics_list)
    total_conversions = sum(m.get("conversions", 0) for m in metrics_list)
    ctr = (total_clicks / total_views * 100) if total_views > 0 else 0
    return {
        "channel_id": channel_id,
        "total_views": total_views,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "ctr_percent": round(ctr, 2),
        "clip_count": len(metrics_list),
    }
