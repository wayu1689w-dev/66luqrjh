PLUGINS = [
    "Google Drive", "AI Color Picker", "Goodie AI",
    "Windsor.ai", "Windsor.ai TikTok Ads", "Metricool",
    "Notion", "Gmail", "Canva", "Outlook Calendar",
    "Product Design", "Figma", "Google Calendar",
    "WordPress", "SharePoint", "Dropbox",
    "ChatGPT Ads Manager", "GeminiLaunch",
    "GitHub Copilot", "Cursor", "DeepSeek",
    "Gemini AI", "Google AI Studio", "GrokBot",
    "Meta AI", "ChatGPT Work", "Claude",
    "OpusClip AI Producer", "TikTok for Business",
    "Supermetrics", "Microsoft 365",
    "AdWhispr Ads", "Google Docs",
    "Google Sheets", "Google Slides",
    "Airtable", "Shopify",
]


def run_all(task):
    for p in PLUGINS:
        print(f"@{p} พร้อมทำงานร่วม: {task}")
    return f"ทั้งหมด {len(PLUGINS)} ปลั๊กอิน พร้อมทำงานร่วม"
