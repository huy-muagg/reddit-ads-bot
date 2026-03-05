import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

from reddit_monitor import RedditMonitor
from ai_generator import AIGenerator
from prompts import TOOLS_INFO

load_dotenv()

# Cấu hình log chi tiết hơn
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

reddit = RedditMonitor()
ai = AIGenerator()
processed_posts = set()
post_cache = {}

async def monitor_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Hàm này sẽ in ra mọi tin nhắn bot nhận được
    user = update.effective_user
    text = update.message.text
    logger.info(f">>> NHẬN TIN NHẮN TỪ {user.first_name} (ID: {user.id}): {text}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logger.info(f"Lệnh /start từ Chat ID: {chat_id}")
    await update.message.reply_text(
        "🚀 Reddit Marketing Bot (Đã Reset)\n\n"
        "1. /scan - Tìm bài viết Reddit.\n"
        "2. /create_post - Soạn bài Thread mới (Subly/RankClaw).\n"
    )
    # Xóa job cũ nếu có và tạo mới
    current_jobs = context.job_queue.get_jobs_by_name(f"scan_{chat_id}")
    for job in current_jobs: job.schedule_removal()
    context.job_queue.run_repeating(auto_scan, interval=900, first=10, chat_id=chat_id, name=f"scan_{chat_id}")

async def create_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Soạn bài cho Subly.xyz", callback_data="write_subly")],
        [InlineKeyboardButton("📈 Soạn bài cho RankClaw.com", callback_data="write_rankclaw")]
    ]
    await update.message.reply_text("Chọn công cụ:", reply_markup=InlineKeyboardMarkup(keyboard))

async def auto_scan(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    logger.info(f"Đang tự động quét cho {chat_id}...")
    posts = reddit.find_relevant_posts(limit=3)
    for post in posts:
        if post['id'] not in processed_posts:
            processed_posts.add(post['id'])
            post_cache[post['id']] = post
            text = f"📢 *MỚI:* {post['title']}\n[Xem bài]({post['url']})"
            keyboard = [[InlineKeyboardButton(f"Soạn cmt {tid.upper()}", callback_data=f"gen_{post['id']}_{tid}")] for tid in post['matched_tools']]
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Đang quét thủ công...")
    await auto_scan(context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    if data[0] == "write":
        tool_id = "_".join(data[1:])
        await query.edit_message_text(f"Đang soạn bài cho {tool_id}...")
        content = await ai.generate_post(tool_id)
        await query.edit_message_text(f"📝 *BÀI VIẾT {tool_id.upper()}:*\n\n```\n{content}\n```", parse_mode='Markdown')
    elif data[0] == "gen":
        pid, tid = data[1], data[2]
        comment = await ai.generate_comment(tid, post_cache.get(pid, {}).get('title', ''))
        await query.edit_message_text(f"🤖 *CMT {tid.upper()}:*\n\n`{comment}`", parse_mode='Markdown')

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = ApplicationBuilder().token(token).build()
    
    # Thêm monitor để theo dõi mọi tin nhắn
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), monitor_messages))
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('scan', scan))
    application.add_handler(CommandHandler('create_post', create_post))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("BOT ĐANG CHẠY... HÃY THỬ NHẮN TIN TRÊN TELEGRAM!")
    application.run_polling(drop_pending_updates=True)
