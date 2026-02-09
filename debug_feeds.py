
import feedparser
import ssl

# SSL Hack
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

TARGET_FEEDS = [
    ("Fitbit (Google Blog)", "https://blog.google/products/fitbit/rss/"),
    ("Garmin Blog", "https://www.garmin.com/en-US/blog/feed/"),
    ("Whoop Podcast (Recovery Science)", "https://feeds.buzzsprout.com/230442.rss"),
    ("Oura Engineering", "https://ouraring.wpengine.com/category/meet-oura/feed/"), 
    ("Oura Pulse", "https://ouraring.com/blog/feed/"),
    ("Apple Newsroom (Health)", "https://www.apple.com/newsroom/rss-feed.rss"),
]

def debug_feeds():
    print("🚀 Debugging Target Feeds (No Filtering)...\n")
    
    for name, url in TARGET_FEEDS:
        print(f"📡 Fetching: {name}...")
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"    ⚠️ BOZO Error: {feed.bozo_exception}")
            
            if not feed.entries:
                print("    ❌ No entries found.")
                continue
                
            print(f"    ✅ Found {len(feed.entries)} entries. Top 5:")
            for i, entry in enumerate(feed.entries[:5]):
                title = entry.get('title', 'No Title')
                link = entry.get('link', 'No Link')
                print(f"       {i+1}. {title} ({link})")
            print("-" * 40)
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            print("-" * 40)

if __name__ == "__main__":
    debug_feeds()
