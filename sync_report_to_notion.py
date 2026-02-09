import os
import requests
import json

# Manual .env loading
def load_env_manually(file_path=".env"):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

load_env_manually()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")


def parse_markdown_to_notion_blocks(markdown_text):
    """
    Simple Markdown parser for Notion blocks.
    """
    blocks = []
    lines = markdown_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
            })
        elif line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}
            })
        elif line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]}
            })
        elif line.startswith("> "):
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
            })
        elif line.startswith("- "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
            })
        elif line.startswith("---"):
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}
            })
    return blocks

def sync_to_notion(file_path, title):
    if not NOTION_TOKEN or not NOTION_PAGE_ID:
        print("❌ Missing Notion credentials in .env")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # 1. Create a new page
    create_url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"page_id": NOTION_PAGE_ID},
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        },
        "children": parse_markdown_to_notion_blocks(content)[:100] # Notion limit is 100 blocks per call
    }

    response = requests.post(create_url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"✅ Successfully synced to Notion: {title}")
        print(f"🔗 Page URL: {response.json().get('url')}")
    else:
        print(f"❌ Failed to sync to Notion: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    report_path = "/Users/wangchen/Desktop/agent 资讯/2025_年度运动科学行业综述.md"
    sync_to_notion(report_path, "2025 年度运动科学行业综述报告")
