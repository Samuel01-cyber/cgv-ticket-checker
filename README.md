# 🎟️ CGV Ticket Checker

Tự động kiểm tra trang phim CGV và gửi thông báo khi xuất hiện nút **Mua vé** qua Discord.

## 🚀 Deploy to Railway
Bấm nút dưới đây để deploy:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/<YOUR_USERNAME>/cgv-ticket-checker&envs=MOVIE_URL,DISCORD_WEBHOOK_URL,CHECK_INTERVAL)

## 🔧 Biến môi trường
- `MOVIE_URL` → Link phim CGV (ví dụ: `https://www.cgv.vn/default/demon-slayer-infinity-castle.html`)
- `DISCORD_WEBHOOK_URL` → Webhook Discord nhận thông báo
- `CHECK_INTERVAL` → Thời gian kiểm tra (giây, mặc định 60)

## 📦 Chạy local
```bash
pip install -r requirements.txt
playwright install chromium
python main.py
