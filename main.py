import os
import time
import requests
import schedule
from playwright.sync_api import sync_playwright

MOVIE_URL = os.getenv("MOVIE_URL", "").strip()
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

# Kiểm tra biến môi trường
if not MOVIE_URL or not DISCORD_WEBHOOK_URL:
    print("❌ Lỗi: Cần thiết lập MOVIE_URL và DISCORD_WEBHOOK_URL trong biến môi trường!")
    exit(1)

def send_discord_message(message):
    """Gửi thông báo đến Discord Webhook"""
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, data={"content": message})
        if res.status_code == 204:
            print("[INFO] Đã gửi thông báo Discord.")
        else:
            print(f"[WARN] Gửi Discord thất bại ({res.status_code}) → {res.text}")
    except Exception as e:
        print(f"[ERROR] Lỗi gửi Discord: {e}")

def check_buy_ticket():
    """Hàm kiểm tra nút Mua vé"""
    print("🔍 Đang kiểm tra nút 'Mua vé'...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, args=["--ignore-certificate-errors"]
            )
            context = browser.new_context(user_agent=HEADERS["User-Agent"])
            page = context.new_page()

            # Chặn tải tài nguyên không cần thiết
            page.route(
                "**/*",
                lambda route, request: route.abort()
                if request.resource_type in ["image", "font", "stylesheet"]
                else route.continue_(),
            )

            try:
                print(f"[INFO] Mở trang {MOVIE_URL}")
                page.goto(
                    MOVIE_URL, wait_until="domcontentloaded", timeout=30000
                )  # 30 giây
            except Exception as e:
                print(f"⚠ Load trang quá lâu hoặc lỗi: {e}")
                browser.close()
                return

            if page.locator("button:has-text('Mua vé')").count() > 0:
                print("✅ Phát hiện nút Mua vé!")
                send_discord_message(f"🎉 Vé đã mở! → {MOVIE_URL}")
            else:
                print("⏳ Chưa thấy nút Mua vé.")

            browser.close()
    except Exception as e:
        print(f"[ERROR] Lỗi trong quá trình kiểm tra: {e}")

# Lên lịch
schedule.every(CHECK_INTERVAL).seconds.do(check_buy_ticket)
print(f"🚀 Bắt đầu theo dõi {MOVIE_URL} mỗi {CHECK_INTERVAL} giây...")

# Vòng lặp chính
while True:
    schedule.run_pending()
    time.sleep(1)
