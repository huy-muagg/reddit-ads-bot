import logging
import os
import asyncio
import json
import hashlib
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.request import HTTPXRequest
from dotenv import load_dotenv
from aiohttp import web

from reddit_monitor import RedditMonitor
from ai_generator import AIGenerator
from prompts import TOOLS_INFO

load_dotenv()

# Đường dẫn file lưu trữ
DATA_FILE = "processed_posts.json"

# Cấu hình log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

reddit = RedditMonitor()
ai = AIGenerator()

def load_processed_posts():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return set(data) if isinstance(data, list) else set()
        except Exception as e:
            logger.error(f"Lỗi tải dữ liệu cũ: {e}")
    return set()

def save_processed_posts(posts_set):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(list(posts_set), f)
    except Exception as e:
        logger.error(f"Lỗi lưu dữ liệu: {e}")

processed_posts = load_processed_posts()
post_cache = {}

def split_text(text, limit=4000):
    if not text: return []
    return [text[i:i+limit] for i in range(0, len(text), limit)]

# --- HEALTH CHECK SERVER FOR RENDER ---
async def handle_health_check(request):
    return web.Response(text="Reddit Ads Bot is Online!")

async def start_health_check_server():
    app = web.Application()
    app.add_routes([web.get('/', handle_health_check)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    logger.info(f"Khởi động Health Check Server tại cổng {port}")
    await site.start()

async def monitor_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not update.message or not update.message.text: return
    text = update.message.text
    
    if "reddit.com" in text:
        url_match = re.search(r'(https?://(?:www\.)?reddit\.com/r/[^/\s]+/comments/[^/\s]+(?:/[^/\s]*)?)', text)
        if url_match:
            url = url_match.group(1)
            url_id = hashlib.md5(url.encode()).hexdigest()[:8]
            post_cache[f"url_{url_id}"] = url
            keyboard = [[InlineKeyboardButton("🎥 Subly.xyz", callback_data=f"lnk_subly_{url_id}"),
                         InlineKeyboardButton("📈 RankClaw.com", callback_data=f"lnk_rankclaw_{url_id}")]]
            await update.message.reply_text(f"🔗 *Đã nhận link Reddit!*\nHuy muốn tạo comment cho công cụ nào?",
                                            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    ai_response = await ai.chat_with_ai(text)
    for part in split_text(ai_response):
        await update.message.reply_text(part)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("🚀 Reddit Marketing Bot (v4.1 - Cloud Ready)\n\n"
                                    "🕹️ Chức năng:\n"
                                    "• Dán link Reddit để tóm tắt và tạo cmt.\n"
                                    "• Nhắn tin bất kỳ để chat trực tiếp với AI.\n"
                                    "• /scan - Quét bài Reddit tự động.\n"
                                    "• /create_post - Soạn bài Thread mới.\n")
    current_jobs = context.job_queue.get_jobs_by_name(f"scan_{chat_id}")
    if not current_jobs:
        context.job_queue.run_repeating(auto_scan, interval=900, first=10, chat_id=chat_id, name=f"scan_{chat_id}")

async def create_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📝 Soạn cho Subly.xyz", callback_data="write_subly")],
                [InlineKeyboardButton("📈 Soạn cho RankClaw.com", callback_data="write_rankclaw")]]
    await update.message.reply_text("Chọn công cụ để soạn bài viết mới:", reply_markup=InlineKeyboardMarkup(keyboard))

async def auto_scan(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    posts = reddit.find_relevant_posts(limit=5)
    for post in posts:
        if post['id'] not in processed_posts:
            processed_posts.add(post['id'])
            post_cache[post['id']] = post
            tools_str = ", ".join([tid.upper() for tid in post['matched_tools']])
            text = f"🔥 MỚI ({tools_str}): {post['title']}\n[Xem trên Reddit]({post['url']})"
            keyboard = [[InlineKeyboardButton(f"🤖 Gợi ý cho {tid.upper()}", callback_data=f"gen_{post['id']}_{tid}")] for tid in post['matched_tools']]
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown', disable_web_page_preview=True)
    save_processed_posts(processed_posts)

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Đang quét bài viết mới...")
    class DummyJob:
        def __init__(self, chat_id): self.chat_id = chat_id
    context.job = DummyJob(update.effective_chat.id)
    await auto_scan(context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    
    if data[0] == "write":
        tool_id = "_".join(data[1:])
        await query.edit_message_text(f"⏳ Đang soạn bài viết cho {tool_id.upper()}...")
        content = await ai.generate_post(tool_id)
        gen_id = f"tr_{hashlib.md5(content[:50].encode()).hexdigest()[:8]}"
        post_cache[gen_id] = {"content": content, "tool": tool_id}
        keyboard = [[InlineKeyboardButton("🇻🇳 Dịch sang Tiếng Việt", callback_data=f"translate_{gen_id}")]]
        await query.message.reply_text(f"📝 BÀI VIẾT {tool_id.upper()}:\n\n{content}", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data[0] == "gen":
        pid, tid = data[1], data[2]
        post_info = post_cache.get(pid, {})
        details = reddit.fetch_post_details(post_info.get('url', ''))
        await query.edit_message_text(f"⏳ Đang tạo 4 gợi ý comment cho {tid.upper()}...")
        suggestions = await ai.generate_comment(tid, f"{post_info.get('title')}\n{post_info.get('content')}", details.get('top_comments', "None") if details else "None")
        for part in split_text(f"✅ GỢI Ý CHO {tid.upper()}\n\n{suggestions}"):
            await query.message.reply_text(part)
        
    elif data[0] == "lnk":
        tool_id, url_id = data[1], data[2]
        url = post_cache.get(f"url_{url_id}")
        if not url: return
        progress_msg = await query.edit_message_text(f"⏳ [███░░░░░░░] 30% - Đang đọc bài & comment...")
        details = reddit.fetch_post_details(url)
        if details:
            await progress_msg.edit_text(f"⏳ [██████░░░░] 60% - Đang tóm tắt & phân tích AI...")
            summary = await ai.generate_summary(details['title'], details['content'])
            await query.message.reply_text(f"📌 *THÔNG TIN BÀI VIẾT:*\n\n{summary}", parse_mode='Markdown')
            suggestions = await ai.generate_comment(tool_id, f"{details['title']}\n{details['content']}", details['top_comments'])
            await progress_msg.edit_text(f"✅ [██████████] 100% - Hoàn tất!")
            for part in split_text(f"✅ GỢI Ý CHO {tool_id.upper()}\n\n{suggestions}"):
                await query.message.reply_text(part)
        else:
            await query.edit_message_text("❌ Không thể lấy nội dung.")

    elif data[0] == "translate":
        gen_id = data[1]
        post_data = post_cache.get(gen_id)
        if post_data:
            translation = await ai.translate_text(post_data["content"])
            for part in split_text(f"🇻🇳 BẢN DỊCH:\n\n{translation}"):
                await query.message.reply_text(part)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Lỗi: {context.error}")

async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("LỖI: Thiếu TELEGRAM_BOT_TOKEN")
        return

    request_config = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0, http_version="1.1")
    application = ApplicationBuilder().token(token).request(request_config).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('scan', scan))
    application.add_handler(CommandHandler('create_post', create_post))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_messages))
    application.add_error_handler(error_handler)

    # Khởi động Health Check Server trước
    await start_health_check_server()

    # Khởi động Bot theo trình tự chuẩn
    async with application:
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        logger.info("Bot đã bắt đầu nhận tin nhắn (Polling)...")
        # Giữ ứng dụng chạy
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
