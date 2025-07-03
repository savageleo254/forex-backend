from journal.performance_monitor import compute_performance_metrics

# Example config (tune as needed)
MAX_SYMBOL_RISK_PERCENT = 2.0
MAX_PORTFOLIO_RISK_PERCENT = 5.0
MIN_RISK_PER_TRADE = 0.1
MAX_ACTIVE_TRADES_PER_SYMBOL = 2
MAX_ACTIVE_TRADES_PORTFOLIO = 5

# Example: track active trades in-memory (persist in DB for prod)
active_trades = {}

def can_enter_trade(symbol, proposed_risk_pct, account_equity=10000):
    """
    Checks whether a new trade can be entered for a symbol and portfolio.
    Returns (bool, reason).
    """
    symbol_trades = active_trades.get(symbol, [])
    portfolio_trades = sum(len(v) for v in active_trades.values())
    total_risk = sum(t["risk_pct"] for trades in active_trades.values() for t in trades)

    if len(symbol_trades) >= MAX_ACTIVE_TRADES_PER_SYMBOL:
        return False, f"Max trades for {symbol} reached"
    if portfolio_trades >= MAX_ACTIVE_TRADES_PORTFOLIO:
        return False, "Max portfolio trades reached"
    if proposed_risk_pct < MIN_RISK_PER_TRADE:
        return False, "Risk too low"
    if proposed_risk_pct > MAX_SYMBOL_RISK_PERCENT:
        return False, "Risk per trade exceeds symbol max"
    if (total_risk + proposed_risk_pct) > MAX_PORTFOLIO_RISK_PERCENT:
        return False, "Portfolio risk cap exceeded"
    # Optionally: check for correlated positions and news regime
    return True, "OK"

def register_trade(symbol, trade_id, risk_pct):
    trade = {"trade_id": trade_id, "risk_pct": risk_pct}
    active_trades.setdefault(symbol, []).append(trade)

def close_trade(symbol, trade_id):
    if symbol in active_trades:
        active_trades[symbol] = [t for t in active_trades[symbol] if t["trade_id"] != trade_id]
        if not active_trades[symbol]:
            del active_trades[symbol]

# Example usage
if __name__ == "__main__":
    print(can_enter_trade("XAUUSD", 1.0))
    register_trade("XAUUSD", "TID001", 1.0)
    print(can_enter_trade("XAUUSD", 1.1))
    close_trade("XAUUSD", "TID001")