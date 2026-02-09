import requests
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

URLS = {
    "fitbit": "https://www.fitabase.com/research-library/",
    "whoop": "https://www.whoop.com/us/en/thelocker/category/science/",
    "oura": "https://ouraring.com/blog/science/",
    "garmin": "https://www.garmin.com/en-US/health/research-library/", 
    "polar": "https://www.polar.com/en/science/whitepapers",
    "apple": "https://www.apple.com/healthcare/docs/" # Specific docs page often lists whitepapers
}

os.makedirs("debug_html", exist_ok=True)

def fetch_and_save(name, url):
    print(f"Fetching {name} from {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            with open(f"debug_html/{name}.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"✅ Saved {name}.html ({len(response.text)} bytes)")
        else:
            print(f"❌ Failed {name}: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error {name}: {e}")

for name, url in URLS.items():
    fetch_and_save(name, url)
