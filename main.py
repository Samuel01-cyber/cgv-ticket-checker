import os
import time
import requests
import schedule
from playwright.sync_api import sync_playwright

MOVIE_URL = os.getenv("MOVIE_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_message(message):
    try:
        requests.post(DISCORD_WEBHOOK_URL, data={"content": message})
        print("[INFO] Sent Discord message.")
    except Exception as e:
        print(f"[ERROR] Discord send failed: {e}")

def check_buy_ticket():
    print("🔍 Checking buy button...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(MOVIE_URL, timeout=60000)

        # Kiểm tra nút Mua vé
        if page.locator("button:has-text('Mua vé')").count() > 0:
            send_discord_message(f"🎉 Vé đã mở! → {MOVIE_URL}")
        else:
            print("⏳ Chưa thấy nút Mua vé.")

        browser.close()

schedule.every(CHECK_INTERVAL).seconds.do(check_buy_ticket)
print(f"🚀 Monitoring {MOVIE_URL} every {CHECK_INTERVAL}s...")
while True:
    schedule.run_pending()
    time.sleep(1)
