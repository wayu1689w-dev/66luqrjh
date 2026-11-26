"""Affiliate QC — ตรวจลิงก์ affiliate"""


def check_affiliate_link(link):
    if not link:
        return False, "ไม่มีลิงก์ affiliate"
    if not link.startswith("http"):
        return False, "ลิงก์ไม่ถูกรูปแบบ"
    return True, "ลิงก์พร้อม (ต้องตรวจ live อีกครั้ง)"


def check_commission(commission_rate, confirmed=False):
    if commission_rate is None:
        return False, "ไม่ทราบอัตราค่าคอมมิชชั่น"
    if not confirmed:
        return False, f"ค่าคอม {commission_rate}% — ยังไม่ยืนยัน"
    return True, f"ค่าคอม {commission_rate}% — ยืนยันแล้ว"
