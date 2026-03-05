#!/bin/bash

# Kiểm tra file .env
if [ ! -f .env ]; then
    echo "⚠️ Lỗi: File .env không tồn tại. Vui lòng copy từ .env.example và điền API Keys."
    exit 1
fi

echo "🚀 Đang khởi động Reddit Ads Bot..."
python3 main.py
