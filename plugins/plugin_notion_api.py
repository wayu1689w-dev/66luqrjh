import os
from uuid import UUID

import requests

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"


def headers():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise RuntimeError("กรุณาตั้งค่า NOTION_TOKEN ใน environment")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": VERSION,
        "Content-Type": "application/json",
    }


def api(method, path, **kwargs):
    response = requests.request(
        method, f"{API}/{path.lstrip('/')}", headers=headers(), timeout=30, **kwargs
    )
    response.raise_for_status()
    return response.json()


def read_blocks(block_id: str) -> list[str]:
    parts = []
    cursor = None

    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor

        result = api("GET", f"blocks/{block_id}/children", params=params)

        for block in result.get("results", []):
            kind = block.get("type", "")
            rich_text = block.get(kind, {}).get("rich_text", [])
            text = "".join(item.get("plain_text", "") for item in rich_text)

            if text:
                parts.append(text)

            if block.get("has_children"):
                parts.extend(read_blocks(block["id"]))

        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")

    return parts


def read_notion_page(page_id: str) -> dict:
    page_id = str(UUID(page_id))
    page = api("GET", f"pages/{page_id}")
    return {"page": page, "text": "\n".join(read_blocks(page_id))}


def remember_page(page_id: str, memory_title: str, memory_note: str) -> dict:
    database_id = os.environ.get("NOTION_MEMORY_DATABASE_ID")
    if not database_id:
        raise RuntimeError(
            "กรุณาตั้งค่า NOTION_MEMORY_DATABASE_ID ใน environment"
        )

    page_id = str(UUID(page_id))
    source = api("GET", f"pages/{page_id}")
    source_url = source.get("url", "")

    return api(
        "POST",
        "pages",
        json={
            "parent": {"database_id": str(UUID(database_id))},
            "properties": {
                "Title": {
                    "title": [{"text": {"content": memory_title[:2000]}}]
                },
                "Type": {"select": {"name": "Notes"}},
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": memory_note[:2000]}}
                        ]
                    },
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": f"Source: {source_url}"},
                            }
                        ]
                    },
                },
            ],
        },
    )
