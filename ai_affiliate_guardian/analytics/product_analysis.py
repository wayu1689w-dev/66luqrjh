"""Product Analysis — วิเคราะห์สินค้า"""


def product_performance(product_id, metrics_list, commissions):
    total_views = sum(m.get("views", 0) for m in metrics_list)
    total_revenue = sum(c.get("amount", 0) for c in commissions if c.get("state") in ("confirmed", "paid"))
    return {
        "product_id": product_id,
        "total_views": total_views,
        "total_revenue": total_revenue,
        "roi_note": "ต้องคำนวณหลังมีข้อมูลจริง",
    }
