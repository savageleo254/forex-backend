import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {resp.text}")

if __name__ == "__main__":
    send_telegram_message("🚨 This is a test alert from your Forex backend!")