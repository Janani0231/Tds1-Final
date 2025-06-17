import os
import json
from playwright.sync_api import sync_playwright, TimeoutError
from bs4 import BeautifulSoup

# === CONFIG ===
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
AUTH_STATE_FILE = "auth.json"

def scrape_specific_thread(playwright, thread_id):
    """Scrape a specific discourse thread by ID"""
    print(f"🔍 Scraping thread ID: {thread_id}")
    
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(storage_state=AUTH_STATE_FILE)
    page = context.new_page()

    # Try to get thread info first to get the slug
    thread_info_url = f"{BASE_URL}/t/{thread_id}.json"
    
    try:
        page.goto(thread_info_url)
        thread_data = json.loads(page.inner_text("pre"))
        
        # Clean all post content using BeautifulSoup
        for post in thread_data.get("post_stream", {}).get("posts", []):
            if "cooked" in post:
                post["cooked"] = BeautifulSoup(post["cooked"], "html.parser").get_text()

        # Create filename using title slug and ID
        title = thread_data.get("title", "unknown")
        slug = thread_data.get("slug", title.lower().replace(" ", "-"))
        filename = f"{slug}_{thread_id}.json"
        
        # Save to downloaded_threads directory
        os.makedirs("downloaded_threads", exist_ok=True)
        filepath = os.path.join("downloaded_threads", filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(thread_data, f, indent=2)
        
        print(f"✅ Saved thread to: {filepath}")
        print(f"📝 Thread title: {title}")
        print(f"💬 Posts in thread: {len(thread_data.get('post_stream', {}).get('posts', []))}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Error scraping thread {thread_id}: {e}")
        return None
    finally:
        browser.close()

def main():
    # Check if auth file exists
    if not os.path.exists(AUTH_STATE_FILE):
        print("❌ No auth.json found. Please run scrape_discourse.py first to authenticate.")
        return
    
    with sync_playwright() as p:
        # Scrape the specific thread we need
        thread_id = 155939
        filepath = scrape_specific_thread(p, thread_id)
        
        if filepath:
            print(f"\n🎉 Successfully scraped thread {thread_id}")
            print(f"📁 File saved at: {filepath}")
            print("\n📋 Next steps:")
            print("1. Run the preprocessing script to add this thread to your knowledge base")
            print("2. Restart your API server")
            print("3. Re-run the promptfoo evaluation")
        else:
            print(f"\n💥 Failed to scrape thread {thread_id}")

if __name__ == "__main__":
    main() 