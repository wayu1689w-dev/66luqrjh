"""Video Performance Analyzer"""


def engagement_rate(views: int, likes: int, comments: int, shares: int) -> float:
    if views == 0:
        return 0.0
    return round((likes + comments + shares) / views * 100, 2)


def analyze_videos(videos: list[dict]) -> dict:
    if not videos:
        return {"total": 0, "avg_views": 0, "avg_engagement": 0, "top_video": None}
    total_views = sum(v.get("views", 0) for v in videos)
    total_engagement = sum(
        engagement_rate(v.get("views", 0), v.get("likes", 0),
                        v.get("comments", 0), v.get("shares", 0))
        for v in videos
    )
    top = max(videos, key=lambda v: v.get("views", 0))
    return {
        "total": len(videos),
        "total_views": total_views,
        "avg_views": round(total_views / len(videos), 1),
        "avg_engagement": round(total_engagement / len(videos), 2),
        "top_video": top.get("title", "unknown"),
    }
