"""Fact QC — ตรวจข้อเท็จจริง ราคา สรรพคุณ"""


def check_price_match(script_price, source_price):
    if script_price is None or source_price is None:
        return False, "ไม่มีราคาให้เปรียบเทียบ"
    if abs(script_price - source_price) > 1:
        return False, f"ราคาไม่ตรง: สคริปต์ {script_price} vs แหล่ง {source_price}"
    return True, "ราคาตรงกัน"


def check_claim_evidence(claim, evidence_level):
    if evidence_level == "unknown":
        return False, f"'{claim}' ยังไม่มีหลักฐาน"
    if evidence_level == "estimate":
        return False, f"'{claim}' เป็นการประมาณ ไม่ใช่ข้อเท็จจริง"
    return True, f"'{claim}' มีหลักฐานระดับ {evidence_level}"
