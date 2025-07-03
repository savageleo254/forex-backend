import os
import json
import requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN")  # Notion integration token
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
JOURNAL_FILE = "logs/trade_journal.jsonl"

def notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

def format_for_notion(entry):
    # Map your journal fields to Notion properties here
    props = {
        "Symbol": {"title": [{"text": {"content": entry["trade_context"].get("symbol", "")}}]},
        "Timestamp": {"rich_text": [{"text": {"content": entry.get("timestamp", "")}}]},
        "Result": {"select": {"name": entry["outcome"].get("result", "pending")}},
        "PnL": {"number": entry["outcome"].get("pnl", 0)},
        "Rationale": {"rich_text": [{"text": {"content": entry.get("rationale", "")}}]},
        # Add more fields as needed
    }
    return {"parent": {"database_id": NOTION_DATABASE_ID}, "properties": props}

def sync_journal_to_notion():
    if not os.path.exists(JOURNAL_FILE):
        print("No journal to sync.")
        return
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        entries = [json.loads(l) for l in f if l.strip()]
    for entry in entries:
        payload = format_for_notion(entry)
        url = "https://api.notion.com/v1/pages"
        response = requests.post(url, headers=notion_headers(), json=payload, timeout=20)
        if response.status_code == 200:
            print(f"Synced entry at {entry.get('timestamp')}")
        else:
            print(f"Failed to sync: {response.status_code} - {response.text}")

if __name__ == "__main__":
    sync_journal_to_notion()