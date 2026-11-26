"""Responsible Automation — กฎความรับผิดชอบ"""

RULES = [
    "ห้าม auto-publish โดยไม่มีคนอนุมัติ",
    "ห้ามใช้เงินโดยไม่มีคนยืนยัน",
    "ห้ามส่งข้อความโดยไม่มีคนตรวจ",
    "ห้ามลบข้อมูลโดยไม่มี backup",
    "ห้ามเลียนแบบเสียง/ใบหน้าคนอื่นโดยไม่มีความยินยอม",
    "ห้ามอ้างสรรพคุณเกินจริง",
    "ทุกการกระทำต้องมี audit log",
]


def check_responsible(action_type):
    forbidden_auto = ["publish", "spend", "message", "delete"]
    if action_type in forbidden_auto:
        return False, f"'{action_type}' ต้องมีคนอนุมัติ — ห้าม auto"
    return True, f"'{action_type}' อนุญาต"
