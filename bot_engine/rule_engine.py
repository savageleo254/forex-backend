def check_guardrails(market_state, fusion_decision, news_context):
    """
    Returns (bool, reason): Should trading proceed?
    """
    # 1. Hard block on high-impact news
    if news_context.get("impact") == "high" and abs(news_context.get("minutes_to_event", 999)) < 15:
        return False, "High-impact news window"

    # 2. Spread spike
    if market_state["spread"] > 1.5 * market_state.get("median_spread", 0.1):
        return False, "Spread spike"

    # 3. Volatility regime check
    if market_state.get("volatility", 0) > 3 * market_state.get("median_volatility", 1.0):
        return False, "Extreme volatility regime"

    # 4. Sentiment/structure divergence
    if abs(fusion_decision["meta"]["sentiment"]["score"]) < 0.65:
        return False, "Weak sentiment"

    # 5. Adaptive: risk-off after drawdown
    from journal.performance_monitor import compute_performance_metrics
    perf = compute_performance_metrics()
    if perf.get("max_drawdown", 0) > 3 * perf.get("pnl_total", 1):
        return False, "Drawdown risk-off"

    return True, "OK"

# Example use in pre-trade:
# allowed, reason = check_guardrails(market_state, fusion_decision, news_context)
# if not allowed:
#     send_telegram_message(f"Trade blocked: {reason}")