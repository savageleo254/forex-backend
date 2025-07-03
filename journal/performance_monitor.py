import os
import json
from collections import defaultdict

JOURNAL_FILE = "logs/trade_journal.jsonl"

def compute_performance_metrics(window=200):
    """Compute recent performance metrics over a moving window."""
    if not os.path.exists(JOURNAL_FILE):
        return {}
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-window:]
    results = [json.loads(l) for l in lines if l.strip()]
    stats = defaultdict(int)
    pnl_total = 0
    max_drawdown = 0
    equity_curve = [0]
    for t in results:
        pnl = t["outcome"].get("pnl", 0)
        pnl_total += pnl
        equity_curve.append(equity_curve[-1] + pnl)
        if t["outcome"]["result"] == "win":
            stats["wins"] += 1
        elif t["outcome"]["result"] == "loss":
            stats["losses"] += 1
    stats["trades"] = len(results)
    stats["winrate"] = round(100 * stats["wins"] / stats["trades"], 2) if stats["trades"] else 0
    stats["pnl_total"] = pnl_total
    if len(equity_curve) > 1:
        peak = equity_curve[0]
        for eq in equity_curve:
            peak = max(peak, eq)
            drawdown = peak - eq
            max_drawdown = max(max_drawdown, drawdown)
    stats["max_drawdown"] = round(max_drawdown, 2)
    return dict(stats)

if __name__ == "__main__":
    print(compute_performance_metrics())