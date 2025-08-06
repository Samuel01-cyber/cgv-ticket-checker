import os
import time
import requests
import schedule
from playwright.sync_api import sync_playwright

MOVIE_URL = os.getenv("MOVIE_URL", "").strip()
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

if not MOVIE_URL or not DISCORD_WEBHOOK_URL:
    print("❌ Lỗi: Cần thiết lập MOVIE_URL và DISCORD_WEBHOOK_URL trong biến môi trường!")
    exit(1)

def send_discord_message(message):
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, data={"content": message})
        if res.status_code == 204:
            print("[INFO] Đã gửi thông báo Discord.")
        else:
            print(f"[WARN] Gửi Discord thất bại ({res.status_code})")
    except Exception as e:
        print(f"[ERROR] Lỗi gửi Discord: {e}")

def check_buy_ticket():
    print("🔍 Đang kiểm tra nút 'Mua vé'...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--ignore-certificate-errors"]
        )
        page = browser.new_page()
        
        # Chỉ chờ DOM load + tăng timeout lên 120 giây
        page.goto(MOVIE_URL, wait_until="domcontentloaded", timeout=120000)

        if page.locator("button:has-text('Mua vé')").count() > 0:
            send_discord_message(f"🎉 Vé đã mở! → {MOVIE_URL}")
        else:
            print("⏳ Chưa thấy nút Mua vé.")

        browser.close()

schedule.every(CHECK_INTERVAL).seconds.do(check_buy_ticket)
print(f"🚀 Bắt đầu theo dõi {MOVIE_URL} mỗi {CHECK_INTERVAL} giây...")

while True:
    schedule.run_pending()
    time.sleep(1)

