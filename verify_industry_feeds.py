import urllib.request
import feedparser
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

CANDIDATE_FEEDS = [
    ("Fitbit (Google Blog)", "https://blog.google/products/fitbit/rss/"),
    ("Whoop (Buzzsprout)", "https://feeds.buzzsprout.com/712316.rss"),
    ("Suunto Journal (Test 1)", "https://www.suunto.com/en-gb/journal/rss/"),
    ("Suunto Journal (Test 2)", "https://www.suunto.com/en-us/feed/all-sports/"),
    ("COROS Stories (Main)", "https://coros.com/stories/feed/"),
    ("Huawei Central", "https://www.huaweicentral.com/feed/"),
    ("Xiaomi Time", "https://xiaomitime.com/feed/"),
    ("Apple Newsroom", "https://www.apple.com/newsroom/rss-feed.rss"),
    ("Garmin Blog", "https://www.garmin.com/en-US/blog/feed/"),
    ("Oura Ring", "https://ouraring.com/blog/feed/"),
    ("Polar", "https://www.polar.com/blog/feed/"),
    ("Zepp Health (Huarmi) BusinessWire", "https://feed.businesswire.com/rss/home/?rss=G1QFDERJXkJeGVtYXw=="),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Testing {len(CANDIDATE_FEEDS)} feeds...")
print("-" * 60)

for name, url in CANDIDATE_FEEDS:
    print(f"Testing: {name}")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = response.read()
            feed = feedparser.parse(data)
            
            if feed.bozo and feed.bozo_exception:
                print(f"  ⚠️  BOZO: {feed.bozo_exception}")
            
            if len(feed.entries) > 0:
                print(f"  ✅ SUCCESS! Found {len(feed.entries)} entries.")
                print(f"     Latest: {feed.entries[0].title}")
            else:
                 print(f"  ❌ EMPTY: No entries found.")
                 
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    print("-" * 60)
