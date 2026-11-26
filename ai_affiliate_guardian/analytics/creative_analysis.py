"""Creative Analysis — วิเคราะห์มุมนำเสนอ"""


def angle_performance(angle, metrics_list):
    if not metrics_list:
        return {"angle": angle, "avg_views": 0, "note": "ยังไม่มีข้อมูล"}
    avg_views = sum(m.get("views", 0) for m in metrics_list) / len(metrics_list)
    avg_clicks = sum(m.get("clicks", 0) for m in metrics_list) / len(metrics_list)
    return {
        "angle": angle,
        "clip_count": len(metrics_list),
        "avg_views": round(avg_views),
        "avg_clicks": round(avg_clicks),
    }
