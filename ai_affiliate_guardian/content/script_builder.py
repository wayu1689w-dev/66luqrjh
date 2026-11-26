"""Script Builder — สร้างสคริปต์ตามช่องและสินค้า"""


def build_script(product, channel_guidelines):
    channel = channel_guidelines.get("channel", "")
    tone = channel_guidelines.get("tone", "")
    rules = channel_guidelines.get("rules", [])
    name = product.get("product_name", "สินค้า")
    price = product.get("price", "ไม่ทราบ")
    return {
        "channel": channel,
        "product": name,
        "sections": {
            "hook": f"[HOOK 3 วิ] เคยลอง {name} ยัง?",
            "body": f"[BODY] รีวิว {name} ราคา {price} บาท — {tone}",
            "cta": f"[CTA] ลิงก์ในโปรไฟล์ กดเลย!",
        },
        "tone": tone,
        "rules_applied": rules,
        "state": "draft",
    }
