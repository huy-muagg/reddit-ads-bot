# 🤖 Reddit Ads Bot - Subly & RankClaw Edition

Hệ thống tự động theo dõi Reddit, phân tích bài viết và soạn nội dung quảng bá bằng AI Gemini.

## 🌟 Tính năng chính
- **Tự động quét Reddit (RSS Mode):** Theo dõi các thảo luận mới nhất về SEO, Marketing và tin tức thế giới (War/Conflict) mà không cần API Reddit (An toàn 100%).
- **AI Content Generator:** Sử dụng Google Gemini AI để soạn các bài viết (Thread) và bình luận (Comment) cực kỳ hấp dẫn, tự nhiên.
- **Telegram Control:** Điều khiển toàn bộ chiến dịch Marketing ngay trên điện thoại qua Bot Telegram.
- **Hỗ trợ Đa công cụ:** Đã cấu hình sẵn cho **Subly.xyz** (Dịch video AI) và **RankClaw.com** (SEO Tracker).

## 🚀 Hướng dẫn cài đặt nhanh
1. **Clone dự án:**
   ```bash
   git clone https://github.com/huy-muagg/reddit-ads-bot.git
   cd reddit-ads-bot
   ```
2. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```
3. **Cấu hình API:**
   Copy file `.env.example` thành `.env` và điền:
   - `TELEGRAM_BOT_TOKEN` (Lấy từ @BotFather)
   - `GEMINI_API_KEY` (Lấy từ Google AI Studio)

4. **Khởi chạy:**
   ```bash
   ./run.sh
   ```

## 🛠 Cách sử dụng
- `/start`: Bắt đầu và kích hoạt chế độ tự động quét (15 phút/lần).
- `/create_post`: Yêu cầu AI soạn một bài viết Reddit (Thread) mới cực hay để bạn tự đăng.
- `/scan`: Quét thủ công ngay lập tức để tìm bài viết đi bình luận.

## 🛡 Bảo mật
File `.env` chứa các khóa API đã được đưa vào `.gitignore` để đảm bảo không bị lộ lên GitHub.

---
*Dự án được phát triển cho mục đích Marketing tự động và hiệu quả trên Reddit.*
