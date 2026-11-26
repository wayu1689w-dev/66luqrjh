"""Dashboard Summary — สรุปภาพรวมระบบ"""

from ..core.product_registry import list_products
from ..core.content_registry import _load as load_content
from ..core.channel_registry import get_active_channels
from ..performance.commission_ledger import total_by_state


def system_summary():
    products = list_products()
    content = load_content()
    channels = get_active_channels()
    money = total_by_state()

    return {
        "total_products": len(products),
        "products_by_state": _count_by_state(products),
        "total_content": len(content),
        "content_by_state": _count_by_state(content),
        "active_channels": len(channels),
        "channel_names": [ch["name"] for ch in channels],
        "money_summary": money,
    }


def _count_by_state(items):
    counts = {}
    for item in items:
        s = item.get("state", "unknown")
        counts[s] = counts.get(s, 0) + 1
    return counts
