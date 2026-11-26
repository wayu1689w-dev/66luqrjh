"""Channel Learning — เรียนรู้จากผลลัพธ์แต่ละช่อง"""


def learn_from_results(channel_id, experiments):
    channel_exps = [e for e in experiments if e.get("channel_id") == channel_id]
    if not channel_exps:
        return {"channel_id": channel_id, "lessons": [], "note": "ยังไม่มีการทดลอง"}
    lessons = []
    for exp in channel_exps:
        results = exp.get("results", {})
        if results:
            best = max(results.items(), key=lambda x: x[1].get("views", 0))
            lessons.append({
                "experiment": exp["name"],
                "best_variant": best[0],
                "best_views": best[1].get("views", 0),
            })
    return {"channel_id": channel_id, "lessons": lessons}
