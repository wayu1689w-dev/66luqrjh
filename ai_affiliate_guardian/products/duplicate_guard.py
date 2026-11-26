"""Duplicate Guard — ป้องกันสินค้าซ้ำ"""


def check_duplicate(new_product, existing_products, check_fields=None):
    if check_fields is None:
        check_fields = ["product_name", "source_platform", "affiliate_link"]
    for existing in existing_products:
        match_count = 0
        for field in check_fields:
            if new_product.get(field) and new_product.get(field) == existing.get(field):
                match_count += 1
        if match_count >= 2:
            return True, existing.get("id", "unknown")
    return False, None
