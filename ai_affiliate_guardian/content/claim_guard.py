"""Claim Guard — ตรวจการอ้างสรรพคุณเกินจริง"""

FORBIDDEN_CLAIMS = [
    "รักษาโรค",
    "ลดน้ำหนักทันที",
    "รวยเร็ว",
    "การันตี",
    "100%",
    "ดีที่สุดในโลก",
    "ไม่มีผลข้างเคียง",
    "หายขาด",
    "ผลลัพธ์ทันที",
]


def check_claims(script_text):
    violations = []
    for claim in FORBIDDEN_CLAIMS:
        if claim in script_text:
            violations.append(claim)
    if violations:
        return False, f"พบคำต้องห้าม: {', '.join(violations)}"
    return True, "ไม่พบการอ้างเกินจริง"


def suggest_fix(violation):
    fixes = {
        "รักษาโรค": "ช่วยบรรเทาอาการ (ไม่ใช่การรักษา)",
        "ลดน้ำหนักทันที": "อาจช่วยควบคุมน้ำหนักเมื่อใช้ร่วมกับการออกกำลังกาย",
        "การันตี": "ตามนโยบายของร้าน",
        "100%": "ส่วนใหญ่",
        "ดีที่สุดในโลก": "เป็นที่นิยม",
    }
    return fixes.get(violation, f"ลบ '{violation}' และใช้คำที่เบากว่า")
