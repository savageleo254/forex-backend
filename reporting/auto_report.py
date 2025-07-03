import os
import json
from datetime import datetime, timedelta

JOURNAL_FILE = "logs/trade_journal.jsonl"
REPORTS_DIR = "reports"

def load_trades(period_days=1):
    """Load trades from journal within the last [period_days] days."""
    if not os.path.exists(JOURNAL_FILE):
        return []
    cutoff = datetime.utcnow() - timedelta(days=period_days)
    trades = []
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            # Parse timestamp, fallback to including all if missing
            ts = entry.get("timestamp", None)
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    if dt >= cutoff:
                        trades.append(entry)
                except Exception:
                    trades.append(entry)
            else:
                trades.append(entry)
    return trades

def summarize_trades(trades):
    """Return summary stats for a list of trades."""
    stats = {
        "count": len(trades),
        "wins": 0,
        "losses": 0,
        "pnl": 0.0,
        "max_drawdown": 0.0,
        "by_config": {},
    }
    equity = [0]
    for t in trades:
        pnl = t.get("outcome", {}).get("pnl", 0)
        stats["pnl"] += pnl
        equity.append(equity[-1] + pnl)
        if t.get("outcome", {}).get("result") == "win":
            stats["wins"] += 1
        elif t.get("outcome", {}).get("result") == "loss":
            stats["losses"] += 1
        config = t.get("trade_context", {}).get("config", "default")
        stats["by_config"].setdefault(config, {"count": 0, "pnl": 0})
        stats["by_config"][config]["count"] += 1
        stats["by_config"][config]["pnl"] += pnl
    peak = equity[0]
    max_dd = 0
    for eq in equity:
        peak = max(peak, eq)
        max_dd = max(max_dd, peak - eq)
    stats["max_drawdown"] = round(max_dd, 2)
    stats["pnl"] = round(stats["pnl"], 2)
    return stats

def generate_md_report(trades, stats, period="Daily"):
    lines = [
        f"# {period} QuantOps Trading Report",
        f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}",
        "",
        f"**Total Trades:** {stats['count']}",
        f"**Wins:** {stats['wins']}",
        f"**Losses:** {stats['losses']}",
        f"**PnL:** {stats['pnl']}",
        f"**Max Drawdown:** {stats['max_drawdown']}",
        "",
        "## Strategy Breakdown",
    ]
    for cfg, s in stats["by_config"].items():
        lines.append(f"- **Config {cfg}:** {s['count']} trades, PnL: {round(s['pnl'],2)}")
    lines.append("")
    lines.append("## Recent Trades")
    for t in trades[-10:]:
        ts = t.get("timestamp", "n/a")
        sym = t.get("trade_context", {}).get("symbol", "")
        res = t.get("outcome", {}).get("result", "")
        pnl = t.get("outcome", {}).get("pnl", 0)
        rationale = t.get("rationale", "")
        lines.append(f"- {ts} | {sym} | {res} | PnL: {pnl} | Reason: {rationale[:60]}...")
    return "\n".join(lines)

def write_report(content, period="daily"):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    fname = os.path.join(REPORTS_DIR, f"{period}_report_{datetime.utcnow().strftime('%Y%m%d')}.md")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Report written to {fname}")
    return fname

if __name__ == "__main__":
    # Daily report
    trades = load_trades(period_days=1)
    stats = summarize_trades(trades)
    md_report = generate_md_report(trades, stats, period="Daily")
    write_report(md_report, period="daily")
    # Weekly report (optional)
    trades_w = load_trades(period_days=7)
    stats_w = summarize_trades(trades_w)
    md_report_w = generate_md_report(trades_w, stats_w, period="Weekly")
    write_report(md_report_w, period="weekly")