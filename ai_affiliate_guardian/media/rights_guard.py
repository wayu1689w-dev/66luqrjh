"""Rights Guard — ตรวจลิขสิทธิ์สื่อ"""


def check_rights(asset):
    rights = asset.get("metadata", {}).get("rights", "unknown")
    if rights == "unknown":
        return False, "ไม่ทราบสิทธิ์ — ห้ามใช้จนกว่าจะยืนยัน"
    if rights == "owned":
        return True, "เป็นเจ้าของ"
    if rights == "licensed":
        return True, "มีลิขสิทธิ์ใช้งาน"
    if rights == "public_domain":
        return True, "สาธารณะ"
    return False, f"สถานะลิขสิทธิ์: {rights} — ตรวจสอบก่อนใช้"
