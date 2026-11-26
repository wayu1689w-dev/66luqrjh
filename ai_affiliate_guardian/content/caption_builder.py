"""Caption Builder — สร้างแคปชั่นตามช่อง"""


def build_caption(product, channel_name, style="short"):
    name = product.get("product_name", "สินค้า")
    price = product.get("price", "")
    price_text = f" {price} บาท" if price else ""
    if style == "short":
        return f"{name}{price_text} 🔥 ลิงก์ในโปรไฟล์"
    return f"ลอง {name}{price_text} แล้วจะรู้ว่าดียังไง ✨ ลิงก์ในโปรไฟล์ #{channel_name.replace(' ', '')}"
