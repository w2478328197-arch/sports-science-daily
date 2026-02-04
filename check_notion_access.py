import os
import json
import urllib.request
import ssl

# Fix SSL on Mac
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Load token from environment
TOKEN = os.environ.get("NOTION_TOKEN", "")


def check_access():
    print(f"🕵️‍♂️ 正在测试 Token: {TOKEN[:6]}...{TOKEN[-4:]}")
    
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Filter for Pages only
    data = {
        "filter": {"value": "page", "property": "object"},
        "page_size": 5
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            results = result.get("results", [])
            print(f"✅ Token 有效！")
            
            if not results:
                print("⚠️ 但是... 我没有找到任何可以访问的页面。")
                print("👉 原因：你可能需要在 Notion 页面里点击右上角 '...' -> 'Connections' -> 添加你的机器人。")
            else:
                print(f"🎉 发现 {len(results)} 个页面：")
                for page in results:
                    title = "无标题"
                    # Try to find title
                    props = page.get("properties", {})
                    for key, val in props.items():
                        if val.get("id") == "title":
                            t_list = val.get("title", [])
                            if t_list: title = t_list[0].get("text", {}).get("content", "无标题")
                    
                    print(f"  - [{title}] ID: {page['id']}")
                    print(f"    链接: {page['url']}")
                    
                # Print the ID of the first one for easy copying
                print(f"\n💡 建议使用第一个页面 ID: {results[0]['id']}")
                
    except urllib.error.HTTPError as e:
        print(f"❌ 连接失败: {e.code}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    check_access()
