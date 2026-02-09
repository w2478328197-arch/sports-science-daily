import re
import urllib.request
import ssl

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

def check_links(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    links = re.findall(r'\((http[^)]+)\)', content)
    print(f"Found {len(links)} links.")
    
    fake_links = []
    
    for link in links:
        try:
            req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status != 200:
                    print(f"❌ {link} returned status {resp.status}")
                    fake_links.append(link)
                else:
                    print(f"✅ {link} is valid")
        except Exception as e:
            print(f"❌ {link} failed: {e}")
            fake_links.append(link)
            
    return fake_links

if __name__ == "__main__":
    report_path = "/Users/wangchen/Desktop/agent 资讯/2025_年度运动科学行业综述.md"
    fake_links = check_links(report_path)
    if fake_links:
        print(f"\nFound {len(fake_links)} broken/fake links.")
    else:
        print("\nAll links are valid.")
