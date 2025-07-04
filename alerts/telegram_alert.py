# alerts/telegram_alerts.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("❌ TELEGRAM_TOKEN or CHAT_ID missing.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"🚨 TEST ALERT 🚨\n{message}",
        "parse_mode": "Markdown"
    }

    try:
        resp = requests.post(url, data=payload)
        if resp.status_code == 200:
            print("✅ Telegram test alert sent successfully.")
        else:
            print(f"❌ Failed. Status: {resp.status_code} → {resp.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    send_telegram_alert("This is a TEST ALERT from Savage Leo (Pro Veteran+++).")
