
import daily_sports_update
import datetime
import sys

# Increase limits to capture a full month of data
daily_sports_update.ITEMS_PER_FEED = 50 
daily_sports_update.TRANSLATION_LIMIT = 5000

# Target only industry feeds
daily_sports_update.RSS_FEEDS = {
    "industry": daily_sports_update.INDUSTRY_FEEDS
}

print("🔎 Scanning last 30 days of wearable trends...")
print(f"Sources: {[name for name, _ in daily_sports_update.INDUSTRY_FEEDS]}")

# Fetch data
try:
    rss_data = daily_sports_update.fetch_rss_feeds(30)
except Exception as e:
    print(f"Error fetching feeds: {e}")
    sys.exit(1)

# Generate Markdown (passing empty list for pubmed data)
md = daily_sports_update.generate_markdown(rss_data, [])

# Save to file
filename = "wearables_last_30_days.md"
with open(filename, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"✅ Generated: {filename}")
print(f"Stats: Found {len(rss_data.get('industry', []))} relevant items.")
