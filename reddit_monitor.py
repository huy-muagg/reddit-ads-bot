import feedparser
import re
import urllib.parse
from prompts import TOOLS_INFO

class RedditMonitor:
    def __init__(self):
        # Scan RSS feeds of popular relevant subreddits including news/war topics
        self.subreddits = [
            "news", "worldnews", "geopolitics", "UkraineConflict", "Conflict", # For War/Conflict context
            "ContentCreators", "youtube", "Tiktokhelp", "podcasting", # For Subly context
            "SEO", "Marketing", "DigitalMarketing", "Entrepreneur", "GrowthHacking" # For RankClaw context
        ]

    def find_relevant_posts(self, limit=10):
        results = []
        try:
            # Create a multi-reddit RSS URL
            subs_joined = "+".join(self.subreddits)
            rss_url = f"https://www.reddit.com/r/{subs_joined}/new/.rss"
            
            # Parse the RSS feed
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:50]: # Scan a broader set of 50 posts
                title = entry.title
                link = entry.link
                content_raw = entry.get('summary', '')
                content = re.sub('<[^<]+>', '', content_raw) 
                
                full_text = (title + " " + content).lower()
                
                matched_tools = []
                for tool_id, info in TOOLS_INFO.items():
                    # Check if any keyword matches
                    if any(kw.lower() in full_text for kw in info["keywords"]):
                        matched_tools.append(tool_id)
                
                if matched_tools:
                    post_id = "unknown"
                    match = re.search(r'/comments/([^/]+)/', link)
                    if match:
                        post_id = match.group(1)

                    results.append({
                        "id": post_id,
                        "title": title,
                        "url": link,
                        "content": content[:500],
                        "matched_tools": matched_tools
                    })
                    
                    if len(results) >= limit:
                        break
            return results
        except Exception as e:
            print(f"Error fetching Reddit RSS: {e}")
            return []
