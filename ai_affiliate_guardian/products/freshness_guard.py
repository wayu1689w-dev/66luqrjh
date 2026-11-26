"""Freshness Guard — ตรวจสินค้าเก่าที่ไม่ได้อัปเดต"""

from datetime import datetime, timezone, timedelta


def check_freshness(product, max_days=30):
    updated = product.get("updated_at") or product.get("created_at")
    if not updated:
        return False, "ไม่มีวันที่อัปเดต"
    if isinstance(updated, str):
        updated = datetime.fromisoformat(updated)
    age = datetime.now(timezone.utc) - updated.replace(tzinfo=timezone.utc)
    if age > timedelta(days=max_days):
        return False, f"เก่า {age.days} วัน (เกิน {max_days} วัน)"
    return True, f"อัปเดตล่าสุด {age.days} วันที่แล้ว"


def flag_stale_products(products, max_days=30):
    stale = []
    for p in products:
        fresh, reason = check_freshness(p, max_days)
        if not fresh:
            stale.append({"product": p, "reason": reason})
    return stale
