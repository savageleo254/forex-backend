# journal/llm_reviewer.py
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat-v3-0324:free"

def review_trade_and_log(trade):
    prompt = f"""You're a trade auditor. Review this trade:
- Symbol: {trade['symbol']}
- Action: {trade['action']}
- Score: {trade['fused_score']}
- Bias: {trade['smc_bias']}
- Forecast: {trade['forecast']}
- Sentiment: {trade['sentiment']}
- Timeframe: {trade['timeframe']}

Was this a high-conviction trade? Rate from 1–10 with short rationale.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)

    try:
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
    except:
        reply = "LLM ERROR: Failed to review."

    os.makedirs("journal", exist_ok=True)
    log_line = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": trade["symbol"],
        "score": trade["fused_score"],
        "action": trade["action"],
        "review": reply
    }

    with open("journal/llm_review_log.jsonl", "a") as f:
        f.write(json.dumps(log_line) + "\n")

    print("✅ LLM Review Logged.")
