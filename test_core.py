import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from daily_sports_update import translate_to_chinese, fetch_rss_feeds, load_history, RSS_FEEDS

def test_translation():
    print("Testing translation...")
    text = "Hello, this is a test of the translation function."
    translated = translate_to_chinese(text)
    print(f"Original: {text}")
    print(f"Translated: {translated}")
    if not translated or translated == text:
        print("❌ Translation failed or returned original.")
    else:
        print("✅ Translation successful.")

def test_fetch():
    print("\nTesting feed fetching (subset)...")
    # Test just one feed to save time
    RSS_FEEDS['test'] = [("Stronger by Science", "https://www.strongerbyscience.com/feed/")]
    
    history = set()
    content, new_links = fetch_rss_feeds(7, history, disable_history=True)
    
    if content:
        print(f"✅ Fetched {len(content)} categories.")
        for cat, items in content.items():
             print(f"  Category: {cat}, Items: {len(items)}")
             if items:
                 print(f"  Sample: {items[0]['title']}")
    else:
         print("❌ Fetch failed or no items found.")

if __name__ == "__main__":
    test_translation()
    # test_fetch() # Uncomment to test fetching if needed, but translation is the likely culprit
