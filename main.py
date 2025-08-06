import os
import time
import requests
import schedule
from bs4 import BeautifulSoup

# ==== Cấu hình từ biến môi trường ====
MOVIE_URL = os.getenv("MOVIE_URL", "").strip()
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))  # giây
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

if not MOVIE_URL or not DISCORD_WEBHOOK_URL:
    print("❌ Cần thiết lập MOVIE_URL và DISCORD_WEBHOOK_URL trong biến môi trường!")
    exit(1)

# ==== Gửi tin nhắn Discord ====
def send_discord_message(message):
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
        if res.status_code == 204:
            print("[INFO] Đã gửi thông báo Discord.")
        else:
            print(f"[WARN] Gửi Discord thất bại ({res.status_code})")
    except Exception as e:
        print(f"[ERROR] Lỗi gửi Discord: {e}")

# ==== Hàm kiểm tra nút mua vé ====
def check_buy_ticket():
    print("🔍 Đang kiểm tra nút 'Mua vé'...")
    try:
        resp = requests.get(MOVIE_URL, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"⚠ Lỗi tải trang ({resp.status_code})")
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Tìm nút Mua vé
        buy_button = soup.find("button", string=lambda t: t and "Mua vé" in t)
        
        if buy_button:
            print("🎉 ĐÃ TÌM THẤY NÚT MUA VÉ!")
            send_discord_message(f"🎉 Vé đã mở! → {MOVIE_URL}")
        else:
            print("⏳ Chưa có vé.")
    except Exception as e:
        print(f"[ERROR] {e}")

# Lên lịch chạy
schedule.every(CHECK_INTERVAL).seconds.do(check_buy_ticket)

print(f"🚀 Bắt đầu theo dõi {MOVIE_URL} mỗi {CHECK_INTERVAL} giây...")
while True:
    schedule.run_pending()
    time.sleep(1)
