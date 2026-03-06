import feedparser
import re
import urllib.parse
import logging
from prompts import TOOLS_INFO

logger = logging.getLogger(__name__)

class RedditMonitor:
    def __init__(self):
        # Scan RSS feeds of popular relevant subreddits
        self.subreddits = [
            "news", "worldnews", "geopolitics", "UkraineConflict", "Conflict", 
            "WarInUkraine", "InternationalNews", "Palestine",
            "ContentCreators", "youtube", "Tiktokhelp", "podcasting", 
            "LanguageLearning", "Translation", "EnglishLearning",
            "SEO", "Marketing", "DigitalMarketing", "Entrepreneur", "GrowthHacking",
            "AffiliateMarketing", "SocialMediaMarketing",
            "SaaS", "SideProject", "SmallBusiness", "Cryptocurrency", "Bitcoin", "investing"
        ]

    def find_relevant_posts(self, limit=10):
        results = []
        try:
            group_size = 5
            for i in range(0, len(self.subreddits), group_size):
                group = self.subreddits[i:i + group_size]
                subs_joined = "+".join(group)
                rss_url = f"https://www.reddit.com/r/{subs_joined}/new/.rss?limit=50"
                
                logger.info(f"Đang quét nhóm subreddit: {subs_joined}")
                agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                feed = feedparser.parse(rss_url, agent=agent)
                
                for entry in feed.entries:
                    title = entry.title
                    link = entry.link
                    content_raw = entry.get('summary', '')
                    content = re.sub('<[^<]+>', '', content_raw) 
                    
                    full_text = (title + " " + content).lower()
                    matched_tools = [tid for tid, info in TOOLS_INFO.items() if any(kw.lower() in full_text for kw in info["keywords"])]
                    
                    if matched_tools:
                        match = re.search(r'/comments/([^/]+)/', link)
                        post_id = match.group(1) if match else "unknown"

                        results.append({
                            "id": post_id,
                            "title": title,
                            "url": link,
                            "content": content[:1000],
                            "matched_tools": matched_tools
                        })
                        
                        if len(results) >= limit: break
                if len(results) >= limit: break
            return results
        except Exception as e:
            logger.error(f"Error fetching Reddit RSS: {e}")
            return []

    def fetch_post_details(self, url):
        """Lấy nội dung bài viết và các comment hàng đầu."""
        try:
            if not url.endswith(".rss"):
                rss_url = url.rstrip("/") + ".rss"
            else:
                rss_url = url
            
            agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            feed = feedparser.parse(rss_url, agent=agent)
            
            if not feed.entries: return None
                
            # Entry đầu tiên thường là bài viết gốc
            post_entry = feed.entries[0]
            title = post_entry.title
            content = re.sub('<[^<]+>', '', post_entry.get('summary', ''))
            
            # Các entry tiếp theo là các comment
            top_comments = []
            for entry in feed.entries[1:6]: # Lấy 5 comment đầu
                comment_text = re.sub('<[^<]+>', '', entry.get('summary', ''))
                if comment_text:
                    top_comments.append(comment_text[:300]) # Giới hạn độ dài mỗi comment
            
            return {
                "title": title,
                "url": url,
                "content": content,
                "top_comments": "\n---\n".join(top_comments)
            }
        except Exception as e:
            logger.error(f"Error fetching post details: {e}")
            return None
