import os
import json
from datetime import datetime

JOURNAL_DIR = "logs"
JOURNAL_FILE = os.path.join(JOURNAL_DIR, "trade_journal.jsonl")

os.makedirs(JOURNAL_DIR, exist_ok=True)

def log_trade(trade_context: dict, execution_result: dict, outcome: dict):
    """
    Logs a trade including all signal inputs, execution details, and final outcome.
    Appends each entry as a JSON line for efficient streaming/review.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "trade_context": trade_context,           # All fusion/signal inputs and market state
        "execution_result": execution_result,     # Fill price, slippage, status, etc.
        "outcome": outcome                        # Win/loss, duration, P&L, etc.
    }
    with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# Example usage
if __name__ == "__main__":
    trade_context = {
        "symbol": "XAUUSD",
        "fusion_inputs": {
            "sentiment": {"score": 0.81, "urgency": "high"},
            "forecast": 0.72,
            "structure": {"confirmed": True, "type": "breakout"},
            "market_state": {"entry": 2363.1, "volatility": 0.21, "spread": 0.09}
        }
    }
    execution_result = {
        "status": "filled",
        "entry_price": 2363.12,
        "slippage": 0.02,
        "sl": 2359.0,
        "tp": 2372.5,
        "order_id": "1234567"
    }
    outcome = {
        "result": "win",
        "pnl": 90.00,
        "duration_sec": 340,
        "exit_reason": "tp_hit"
    }
    log_trade(trade_context, execution_result, outcome)
    print("Trade logged.")