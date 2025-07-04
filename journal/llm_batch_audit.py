# journal/llm_batch_audit.py
import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

JOURNAL_FILE = "logs/trade_journal.jsonl"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat-v3-0324:free"

def load_last_trades(n=5):
    if not os.path.exists(JOURNAL_FILE):
        return []
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-n:]
    return [json.loads(l) for l in lines if l.strip()]

def review_trades_via_openrouter(n=5):
    trades = load_last_trades(n)
    if not trades:
        return "⚠️ No trades found in journal."
    prompt = f"""
Review the following {len(trades)} trades (JSON formatted):
1. Summarize strengths and what works well.
2. List recurring issues or mistakes.
3. Provide 3 actionable recommendations to improve results.

Trades:
{json.dumps(trades, indent=2)}
"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1024
    }
    response = requests.post(url, headers=headers, json=data, timeout=60)
    if response.ok:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"OpenRouter API error: {response.status_code} - {response.text}"

# ✅ Telegram sync
from alerts.telegram_alerts import send_telegram_alert

def push_to_telegram(summary: str):
    msg = f"📊 *LLM Batch Audit Summary*\n\n{summary[:3800]}"
    try:
        send_telegram_alert(msg)
    except Exception as e:
        print(f"⚠️ Telegram push failed: {e}")

# ✅ Optional Notion sync
try:
    from journal.notion_sync import push_batch_audit_to_notion
    NOTION_ENABLED = True
except ImportError:
    NOTION_ENABLED = False

def log_to_file(summary: str):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    os.makedirs("logs", exist_ok=True)
    path = f"logs/llm_batch_audit_{ts}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"✅ Audit log saved to: {path}")

# === EXECUTE ===
if __name__ == "__main__":
    summary = review_trades_via_openrouter(5)
    print(summary)

    log_to_file(summary)
    push_to_telegram(summary)
    if NOTION_ENABLED:
        push_batch_audit_to_notion(summary)
