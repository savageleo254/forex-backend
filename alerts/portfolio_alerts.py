import os
import requests

# --- Telegram Integration ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message: str, chat_id: str = None):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not set.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id or TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"Telegram send error: {e}")

# --- Slack Integration ---
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(message: str):
    if not SLACK_WEBHOOK_URL:
        print("Slack webhook URL not set.")
        return
    payload = {"text": message}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Slack send error: {e}")

# --- Discord Integration ---
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_alert(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL not set.")
        return
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Discord send error: {e}")

# --- Unified Alert Function ---
def send_portfolio_alert(message: str):
    send_telegram_alert(message)
    send_slack_alert(message)
    send_discord_alert(message)

# Example Usage:
if __name__ == "__main__":
    send_portfolio_alert("🚨 New trade opened: XAUUSD Long, size 0.3, SL/TP active.")
    send_portfolio_alert("⚠️ Max drawdown threshold breached! Risk-off triggered.")