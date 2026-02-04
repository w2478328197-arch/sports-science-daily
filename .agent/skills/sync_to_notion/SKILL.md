---
name: Sync Markdown to Notion
description: Upload a local Markdown file to a Notion Page using MCP tools.
---

# Sync Markdown to Notion

This skill describes how to read a local Markdown file and upload its content to a specific Notion Page as child blocks.

## Prerequisites
1.  **Notion Access**: Ensure the Notion MCP server is active and authenticated.
2.  **Target Page**: You need the `page_id` of the Notion page where you want to add the content.
3.  **Source File**: The absolute path to the Markdown file you want to upload.

## Workflow

1.  **Read the Markdown File**:
    Use `view_file` to read the content of the markdown file.

2.  **Parse Markdown to Blocks**:
    *   The Notion API requires content to be in "Block" format (JSON objects), not raw Markdown text.
    *   You must convert the Markdown text into Notion Blocks.
    *   *Note*: Since you cannot easily run complex parsing logic in your head, it's best to use a helper script or specific MCP tool if available. If not, you can construct simple blocks (Paragraphs, Headings) manually for short content.
    *   **Better Approach**: Use the `daily_sports_update.py` script's internal logic if available, or ask the user to run a conversion script.

    *However, for this specific skill context (User Request), we will assume we use the `mcp_notion_API-patch-block-children` tool.*

3.  **Upload to Notion**:
    Use the `mcp_notion_API-patch-block-children` tool.
    *   `block_id`: The ID of the parent page.
    *   `children`: An array of block objects.

    **Example Block Structure**:
    ```json
    [
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": { "rich_text": [{ "type": "text", "text": { "content": "Section Title" } }] }
      },
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": { "rich_text": [{ "type": "text", "text": { "content": "This is a paragraph." } }] }
      }
    ]
    ```

## Python Helper (Recommended)

Since parsing Markdown to Notion Blocks is complex to do via tool calls alone, it is highly recommended to use the existing `daily_sports_update.py` script which already contains a `parse_markdown_to_notion_blocks` function.

**To run the sync manually:**
1.  Ensure `.env` contains `NOTION_TOKEN` and `NOTION_PAGE_ID`.
2.  Run the script: `python3 daily_sports_update.py` (which generates and syncs).
