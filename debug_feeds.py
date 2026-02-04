import feedparser
import datetime
from datetime import timezone
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

BLOGGER_FEEDS = [
    ("Stronger by Science (Nuckols)", "https://www.strongerbyscience.com/feed/"),
    ("Look Great Naked (Schoenfeld)", "http://www.lookgreatnaked.com/blog/feed/"),
    ("Mysportscience (Jeukendrup)", "https://www.mysportscience.com/blog-feed.xml"),
    ("Peter Attia (Longevity)", "https://peterattiadrive.libsyn.com/rss"),
    ("The Barbell Physio", "https://thebarbellphysio.com/feed/"),
    ("Renaissance Periodization (Dr. Mike)", "https://www.youtube.com/feeds/videos.xml?channel_id=UCfQgV2Cq6-A4G27T-u0-gXg"),
    ("Jeff Nippard (Science Explained)", "https://www.youtube.com/feeds/videos.xml?channel_id=UC68TLK0mAEzUyHx5x5k_h1Q"),
    ("Andy Galpin (Human Performance)", "https://www.youtube.com/feeds/videos.xml?channel_id=UCe3R2e3zYxWwIhMKV36Qhkw"),
    ("Andrew Huberman (Podcast)", "https://feeds.megaphone.fm/hubermanlab"),
]

INDUSTRY_FEEDS = [
    ("Wareable (Wearables)", "https://www.wareable.com/rss"),
    ("DC Rainmaker (Product Reviews)", "https://www.dcrainmaker.com/feed"),
    ("Gadgets & Wearables", "https://gadgetsandwearables.com/feed/"),
    ("SportTechie (Sports Tech)", "https://www.sporttechie.com/feed/"),
    ("Sports Technology Blog", "http://sportstechnologyblog.com/feed/"),
]

def check_feed(name, url):
    print(f"Checking: {name}")
    try:
        feed = feedparser.parse(url)
        if hasattr(feed, 'bozo_exception') and feed.bozo_exception:
            print(f"  ❌ BOZO Error: {feed.bozo_exception}")
        
        entry_count = len(feed.entries)
        print(f"  Entries: {entry_count}")
        
        if entry_count > 0:
            e = feed.entries[0]
            date_struct = getattr(e, 'published_parsed', None) or getattr(e, 'updated_parsed', None)
            if date_struct:
                dt = datetime.datetime(*date_struct[:6], tzinfo=timezone.utc)
                print(f"  Latest Post: {dt.strftime('%Y-%m-%d')}")
            else:
                print(f"  ❌ Latest Post: NO DATE FOUND (Keys: {e.keys()})")
        else:
            print("  ⚠️ Empty Feed")
            
    except Exception as e:
        print(f"  ❌ Connection Error: {e}")
    print("-" * 20)

print("=== BLOGGERS ===")
for name, url in BLOGGER_FEEDS:
    check_feed(name, url)

print("\n=== INDUSTRY ===")
for name, url in INDUSTRY_FEEDS:
    check_feed(name, url)
