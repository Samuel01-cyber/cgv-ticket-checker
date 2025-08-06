import os
import time
import requests
import schedule
from playwright.sync_api import sync_playwright

# ==== Cấu hình ====
MOVIE_URL = os.getenv("MOVIE_URL", "").strip()
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
BROWSERLESS_KEY = os.getenv("BROWSERLESS_KEY", "").strip()  # API key Browserless

if not MOVIE_URL or not DISCORD_WEBHOOK_URL or not BROWSERLESS_KEY:
    print("❌ Thiếu MOVIE_URL, DISCORD_WEBHOOK_URL hoặc BROWSERLESS_KEY!")
    exit(1)

BROWSERLESS_URL = f"wss://chrome.browserless.io/playwright?token={BROWSERLESS_KEY}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

def send_discord_message(message):
    """Gửi thông báo đến Discord"""
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, data={"content": message})
        if res.status_code == 204:
            print("[INFO] Đã gửi thông báo Discord.")
        else:
            print(f"[WARN] Gửi Discord thất bại ({res.status_code})")
    except Exception as e:
        print(f"[ERROR] Lỗi gửi Discord: {e}")

def check_buy_ticket():
    print(f"🔍 Đang kiểm tra {MOVIE_URL}...")

    try:
        with sync_playwright() as p:
            # Kết nối tới Browserless.io
            browser = p.chromium.connect_over_cdp(BROWSERLESS_URL)
            context = browser.new_context(user_agent=HEADERS["User-Agent"])
            page = context.new_page()

            # Chặn tài nguyên không cần thiết
            page.route("**/*", lambda route, request: route.abort()
                       if request.resource_type in ["image", "font", "stylesheet"]
                       else route.continue_())

            page.goto(MOVIE_URL, wait_until="domcontentloaded", timeout=30000)

            if page.locator("button:has-text('Mua vé')").count() > 0:
                print("✅ Phát hiện nút Mua vé!")
                send_discord_message(f"🎉 Vé đã mở! → {MOVIE_URL}")
            else:
                print("⏳ Chưa thấy nút Mua vé.")

            browser.close()
    except Exception as e:
        print(f"[ERROR] Lỗi kiểm tra: {e}")

# Lịch chạy
schedule.every(CHECK_INTERVAL).seconds.do(check_buy_ticket)
print(f"🚀 Bắt đầu theo dõi {MOVIE_URL} mỗi {CHECK_INTERVAL} giây...")

while True:
    schedule.run_pending()
    time.sleep(1)
