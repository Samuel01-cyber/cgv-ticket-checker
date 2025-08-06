import os
import time
import requests
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

MOVIE_URL = os.getenv("MOVIE_URL", "https://www.cgv.vn/default/demon-slayer-infinity-castle.html")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))  # giây
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_message(message, image_path=None):
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as img:
                payload = {"content": message}
                files = {"file": img}
                r = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)
        else:
            payload = {"content": message}
            r = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print("[✅] Đã gửi thông báo Discord." if r.status_code in [200, 204] else f"[❌] Lỗi gửi Discord: {r.status_code}")
    except Exception as e:
        print(f"[❌] Lỗi gửi Discord: {e}")

def check_buy_ticket():
    print("🔍 Đang kiểm tra nút 'Mua vé'...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(MOVIE_URL)

    try:
        buy_buttons = driver.find_elements(By.XPATH, "//button[@title='Mua vé']")
        if buy_buttons:
            screenshot_path = "buy_ticket.png"
            driver.save_screenshot(screenshot_path)
            print("[🎉] ĐÃ CÓ NÚT MUA VÉ!")
            send_discord_message(
                f"🎬 **ĐÃ MỞ MUA VÉ**!\n🔗 {MOVIE_URL}",
                image_path=screenshot_path
            )
        else:
            print("[❌] Chưa có nút Mua vé.")
    except Exception as e:
        print(f"[❌] Lỗi khi tìm nút Mua vé: {e}")
    finally:
        driver.quit()

schedule.every(CHECK_INTERVAL).seconds.do(check_buy_ticket)

print(f"🚀 Đang theo dõi trang phim mỗi {CHECK_INTERVAL} giây...")
check_buy_ticket()

while True:
    schedule.run_pending()
    time.sleep(1)
