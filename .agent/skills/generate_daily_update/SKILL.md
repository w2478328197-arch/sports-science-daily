---
name: Generate Daily Sports Update
description: Runs the sports science crawler to generate a daily report, sync to Notion, and prevent duplicate content.
---

# Generate Daily Sports Update

This skill runs the `daily_sports_update.py` script to fetch the latest sports science research and wearable tech news. It automatically handles deduplication, so you can run it frequently without worrying about seeing the same content twice.

## Instructions

1.  **Run the update**:
    Use the `run_command` tool to execute the python script.

    ```bash
    python3 "/Users/wangchen/Desktop/agent 资讯/daily_sports_update.py" --days 2
    ```

    -   `--days N`: (Optional) Number of days to look back (default is 2). If you haven't run it in a while, increase this (e.g., `--days 7` or `--days 30`).
    -   `--no-history`: (Optional) Use this ONLY if you want to force re-fetching of already seen items (e.g., for debugging).

2.  **Output**:
    -   The script will generate a Markdown file: `YYYY-MM-DD_运动科学日报.md`
    -   It will automatically sync the content to the Notion page configured in `.env`.
    -   It will update `processed_history.json` to mark items as seen.

3.  **No New Content?**:
    -   If the script prints "🎉 没有发现新内容", it means all found items in the lookback period have already been processed. You can try increasing `--days`.

## Troubleshooting

-   **Notion Sync Fail**: Check `.env` for `NOTION_TOKEN` and `NOTION_PAGE_ID`.
-   **No content found**: Ensure `requirements.txt` dependencies are installed (`pip3 install -r requirements.txt`).
