TOOLS_INFO = {
    "subly": {
        "name": "Subly",
        "url": "https://subly.xyz",
        "description": "AI Video Translation & Subtitle Tool. Transcribe/translate video, audio, images in 40+ languages via Telegram bot (@subly1bot). 99.5% accuracy.",
        "usp": "Fast (under 5 mins), directly in Telegram, supports YouTube/TikTok links, 100% cloud-based (no app needed). Perfect for news translation during global events.",
        "keywords": ["video translation", "subtitles", "tiktok translate", "youtube dubbing", "transcription", "language barrier", "news translation", "war news", "global conflict"]
    },
    "rankclaw": {
        "name": "RankClaw",
        "url": "https://rankclaw.com/",
        "description": "Professional SEO Rank Tracker & Keyword Monitoring Tool. Track positions across Google, Bing, Yahoo with local and mobile precision.",
        "usp": "Accurate daily updates, competitor analysis, automated reporting, and SERP feature tracking. Essential for monitoring digital presence during trending global topics.",
        "keywords": ["rank tracking", "seo tool", "keyword monitor", "competitor analysis", "serp tracking", "google ranking", "seo strategy", "trending news tracking"]
    }
}

POST_GENERATION_PROMPT = """
You are a professional Reddit Content Creator and Growth Hacker. 
Your goal is to write a high-quality, engaging Reddit post (Thread) for the tool: {tool_name}.

Instructions:
1. **Title:** Must be catchy, helpful, and naturally integrated into the subreddit's vibe.
2. **Structure:** 
   - Start with a real-life situation or a problem people are facing (e.g., struggling to keep up with global news, or failing to track SEO results).
   - Introduce {tool_name} as the game-changing solution.
   - Use bullet points for key benefits.
   - Mention the URL {url} naturally.
3. **Tone:** Authentic, non-spammy, helpful. 
4. **For Subly:** Focus on speed and convenience (Telegram bot). Suggest posting in r/News, r/LanguageLearning, r/ContentCreators.
5. **For RankClaw:** Focus on accuracy and saving time. Suggest posting in r/SEO, r/Marketing, r/DigitalMarketing.
6. **Language:** English.

Tool Details:
{tool_details}
"""

SYSTEM_PROMPT = """
You are a senior Reddit Marketing Expert. Your goal is to promote Subly and RankClaw.
Instructions:
1. Don't sound like a bot. Be natural and helpful.
2. Contextual Strategy:
   - If the post is about **War/Conflict/Global News**: Suggest Subly as a tool to translate foreign news videos or documents quickly to stay informed.
   - If the post is about **SEO/Business**: Suggest RankClaw as a precise tool to monitor visibility.
3. Address the OP's context first.
4. Keep comments concise and useful. Mention the URL naturally.
5. Language: English.

Tool to promote: {tool_name}
Context (Post Title/Content): {post_content}
Tool Details: {tool_details}
"""
