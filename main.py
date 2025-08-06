import os
import time
import requests
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

MOVIE_URL = os.getenv("MOVIE_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_message(message):
    requests.post(DISCORD_WEBHOOK_URL, data={"content": message})
    print("[INFO] Sent Discord message.")

def check_buy_ticket():
    print("🔍 Checking buy button...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(MOVIE_URL)
    time.sleep(3)
    try:
        buy_button = driver.find_element(By.XPATH, "//button[contains(text(),'Mua vé')]")
        if buy_button and buy_button.is_enabled():
            send_discord_message("🎉 Vé đã mở! → " + MOVIE_URL)
    except Exception:
        print("⏳ Chưa thấy nút Mua vé.")
    finally:
        driver.quit()

schedule.every(CHECK_INTERVAL).seconds.do(check_buy_ticket)
print(f"🚀 Monitoring {MOVIE_URL} every {CHECK_INTERVAL}s...")
while True:
    schedule.run_pending()
    time.sleep(1)
