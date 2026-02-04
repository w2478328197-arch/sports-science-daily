import feedparser
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

url = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCfQgV2Cq6-A4G27T-u0-gXg'
print(f"Parsing: {url}")
feed = feedparser.parse(url)
print(f"Status: {getattr(feed, 'status', 'N/A')}")
print(f"Entries: {len(feed.entries)}")
if feed.entries:
    print(f"Latest: {feed.entries[0].title}")
else:
    print(f"Bozo: {feed.bozo}")
    if feed.bozo:
        print(f"Bozo Exception: {feed.bozo_exception}")
