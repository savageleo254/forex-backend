import os
import json
from journal.performance_monitor import compute_performance_metrics
from collections import defaultdict

JOURNAL_FILE = "logs/trade_journal.jsonl"
CONFIGS = [
    {"name": "A", "params": {"sentiment_weight": 0.3, "sl_buffer": 0.5, "tp_rr": 2.0}},
    {"name": "B", "params": {"sentiment_weight": 0.5, "sl_buffer": 0.3, "tp_rr": 1.5}},
    # Add more configs as needed
]

def tag_trades_by_config():
    if not os.path.exists(JOURNAL_FILE):
        return defaultdict(list)
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    by_config = defaultdict(list)
    for entry in lines:
        config = entry.get("trade_context", {}).get("config", "A")
        by_config[config].append(entry)
    return by_config

def compare_configs():
    by_config = tag_trades_by_config()
    results = {}
    for config, trades in by_config.items():
        stats = {
            "trades": len(trades),
            "winrate": 0,
            "pnl_total": 0,
            "max_drawdown": 0
        }
        pnl_total = 0
        wins = 0
        losses = 0
        equity_curve = [0]
        for t in trades:
            pnl = t["outcome"].get("pnl", 0)
            pnl_total += pnl
            equity_curve.append(equity_curve[-1] + pnl)
            if t["outcome"]["result"] == "win":
                wins += 1
            elif t["outcome"]["result"] == "loss":
                losses += 1
        stats["winrate"] = round(100 * wins / max(1, len(trades)), 2)
        stats["pnl_total"] = pnl_total
        peak = equity_curve[0]
        max_drawdown = 0
        for eq in equity_curve:
            peak = max(peak, eq)
            drawdown = peak - eq
            max_drawdown = max(max_drawdown, drawdown)
        stats["max_drawdown"] = round(max_drawdown, 2)
        results[config] = stats
    return results

if __name__ == "__main__":
    results = compare_configs()
    print(json.dumps(results, indent=2))