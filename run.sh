#!/bin/bash

# Di chuyển vào thư mục dự án
cd "$(dirname "$0")"

# Kiểm tra file .env
if [ ! -f .env ]; then
    echo "⚠️ Lỗi: File .env không tồn tại. Vui lòng copy từ .env.example và điền API Keys."
    exit 1
fi

# Kiểm tra môi trường ảo
if [ -d ".venv" ]; then
    echo "📦 Đang kích hoạt môi trường ảo..."
    source .venv/bin/activate
fi

echo "🚀 Đang khởi động Reddit Marketing Bot (v2)..."
python3 main.py
