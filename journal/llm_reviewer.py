import os
import json
import requests

JOURNAL_FILE = "logs/trade_journal.jsonl"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Set in .env

def load_last_trades(n=5):
    if not os.path.exists(JOURNAL_FILE):
        return []
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-n:]
    return [json.loads(l) for l in lines if l.strip()]

def review_trades_via_openrouter(n=5, model="openai/gpt-4o"):
    trades = load_last_trades(n)
    if not trades:
        return "No trades found in journal."
    prompt = f"""
    Review the following {len(trades)} trades (full context in JSON).
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
        "model": model,
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

if __name__ == "__main__":
    print(review_trades_via_openrouter(5))