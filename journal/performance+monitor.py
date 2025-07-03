import os
import json
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openai/gpt-4o"
JOURNAL_FILE = "logs/trade_journal.jsonl"

def generate_trade_rationale(trade_context):
    """
    Uses OpenRouter LLM to generate a natural-language rationale for a trade.
    """
    prompt = f"""
    As a professional trading assistant, analyze the following trade context and generate a clear, concise rationale explaining:
    - Why this trade was considered (signals, structure, sentiment, forecast)
    - Main risk factors
    - Confidence level and what would invalidate the setup

    Trade context:
    {json.dumps(trade_context, indent=2)}
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 512
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    if resp.ok:
        reply = resp.json()["choices"][0]["message"]["content"]
        return reply.strip()
    else:
        return f"LLM error: {resp.status_code} - {resp.text}"

def annotate_journal_with_rationale():
    """
    Reads journal, generates rationale for entries missing 'rationale', and updates them.
    """
    if not os.path.exists(JOURNAL_FILE):
        print("No journal to annotate.")
        return
    updated = False
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    for entry in lines:
        if "rationale" not in entry:
            trade_context = entry.get("trade_context", {})
            rationale = generate_trade_rationale(trade_context)
            entry["rationale"] = rationale
            updated = True
    if updated:
        with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
            for entry in lines:
                f.write(json.dumps(entry) + "\n")
        print("Journal updated with rationales.")
    else:
        print("No new rationales needed.")

if __name__ == "__main__":
    annotate_journal_with_rationale()