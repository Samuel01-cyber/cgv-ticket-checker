import os
import time
import requests
import schedule
import random

MOVIE_URL = os.getenv("MOVIE_URL", "").strip()
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

# Danh sách proxy Việt Nam miễn phí (HTTP/HTTPS)
VN_PROXIES = [
    "http://27.71.228.32",
    "http://171.248.217.110",
    "http://27.79.183.77",
    "http://116.107.189.227",
    "http://123.58.199.232"
]

if not MOVIE_URL or not DISCORD_WEBHOOK_URL:
    print("❌ Cần thiết lập MOVIE_URL và DISCORD_WEBHOOK_URL!")
    exit(1)

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
    print("🔍 Đang kiểm tra nút 'Mua vé'...")

    # Chọn ngẫu nhiên 1 proxy Việt Nam
    proxy = random.choice(VN_PROXIES)
    proxies = {
        "http": proxy,
        "https": proxy
    }
    print(f"[INFO] Đang dùng proxy: {proxy}")

    for attempt in range(3):  # thử tối đa 3 lần
        try:
            res = requests.get(MOVIE_URL, headers=HEADERS, proxies=proxies, timeout=60)
            if "Mua vé" in res.text:
                send_discord_message(f"🎉 Vé đã mở! → {MOVIE_URL}")
            else:
                print("⏳ Chưa thấy nút Mua vé.")
            return
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Lỗi khi tải trang (lần {attempt+1}): {e}")
            if attempt < 2:
                print("[INFO] Thử lại...")
                time.sleep(3)
    print("[FAIL] Hết số lần thử, bỏ qua lần này.")

# Lịch chạy
schedule.every(CHECK_INTERVAL).seconds.do(check_buy_ticket)
print(f"🚀 Bắt đầu theo dõi {MOVIE_URL} mỗi {CHECK_INTERVAL} giây...")

while True:
    schedule.run_pending()
    time.sleep(1)

