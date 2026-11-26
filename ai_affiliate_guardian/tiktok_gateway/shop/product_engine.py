"""Product Engine — TikTok Shop Product API"""

SCOPES = ["product.read", "product.write"]
ENDPOINTS = [
    "GET /products",
    "GET /products/{product_id}",
    "POST /products",
    "PUT /products/{product_id}",
    "POST /products/{product_id}/prices",
    "POST /products/search",
]


def get_status():
    return {
        "engine": "product",
        "documented": True,
        "scopes": SCOPES,
        "endpoints": len(ENDPOINTS),
        "authorized": False,
        "connected": False,
    }
