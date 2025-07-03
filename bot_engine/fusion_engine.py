"""
Signal Fusion & Decision Logic Engine
Institutional-grade trade trigger logic for QuantOps EA.
- Fuses LLM sentiment, forecast, and technical/structure context
- Applies professional-grade multi-factor filters and dynamic risk scaling
- Outputs trade intent, entry/SL/TP, and risk size
"""

from typing import Dict, Any
import numpy as np
import time

# Thresholds and weights (can be loaded from config/env)
SENTIMENT_THRESHOLD = 0.65
SENTIMENT_URGENCY_MIN = 'medium'  # 'low' < 'medium' < 'high'
FORECAST_MIN_AGREEMENT = 0.5      # e.g. probability/confidence
STRUCTURE_CONFIRMATION_REQUIRED = True
WEIGHTS = {'sentiment': 0.4, 'forecast': 0.3, 'structure': 0.3}

RISK_BASE = 1.0      # % of equity, can be scaled
RISK_MAX = 2.0
RISK_MIN = 0.25

def urgency_rank(urgency: str) -> int:
    ranks = {'low': 0, 'medium': 1, 'high': 2}
    return ranks.get(urgency.lower(), 0)

def compute_trade_confidence(sentiment_score, forecast_score, structure_score):
    # Weighted sum (can be replaced with ML model output)
    return (
        WEIGHTS['sentiment'] * abs(sentiment_score) +
        WEIGHTS['forecast'] * forecast_score +
        WEIGHTS['structure'] * structure_score
    )

def decide_entry_type(structure, urgency):
    # If structure is breakout and urgency is high, use market order; else, limit order near zone
    if structure.get('type') == 'breakout' and urgency == 'high':
        return 'market'
    return 'limit'

def calculate_sl_tp(entry, direction, structure, volatility, rr=2.0):
    # SL: below/above structure + vol buffer. TP: based on R:R and forecast bias
    if direction == 'buy':
        sl = entry - (structure.get('sl_buffer', 0.0) + volatility)
        tp = entry + (abs(entry - sl) * rr)
    else:
        sl = entry + (structure.get('sl_buffer', 0.0) + volatility)
        tp = entry - (abs(entry - sl) * rr)
    return round(sl, 3), round(tp, 3)

def fuse_signals(
    sentiment: Dict[str, Any],
    forecast: float,
    structure: Dict[str, Any],
    market_state: Dict[str, Any],
    equity: float = 10000.0,  # can be dynamic
) -> Dict[str, Any]:
    """
    Main fusion engine.

    Inputs:
    - sentiment: {'score': float, 'urgency': str, 'direction': str}
    - forecast: float (directional confidence, e.g. 0.0–1.0, sign for direction)
    - structure: {'confirmed': bool, 'type': 'breakout'|'zone', 'sl_buffer': float, ...}
    - market_state: {'entry': float, 'volatility': float, 'spread': float, ...}
    - equity: account size

    Returns: dict with decision, risk, entry_type, sl, tp, etc.
    """

    # 1. Pre-decision sanity checks
    if market_state['spread'] > 1.5 * market_state.get('median_spread', 1.0):
        return {'decision': 'block', 'reason': 'Spread too high'}

    if market_state.get('data_age', 0) > 20:  # seconds
        return {'decision': 'block', 'reason': 'Data too old'}

    if market_state.get('volatility', 1.0) > 3 * market_state.get('median_volatility', 1.0):
        return {'decision': 'block', 'reason': 'Volatility spike'}

    # 2. Bias confirmation
    sentiment_ok = abs(sentiment['score']) >= SENTIMENT_THRESHOLD and urgency_rank(sentiment['urgency']) >= urgency_rank(SENTIMENT_URGENCY_MIN)
    forecast_ok = abs(forecast) >= FORECAST_MIN_AGREEMENT and np.sign(forecast) == np.sign(sentiment['score'])
    structure_ok = structure.get('confirmed', False)

    if not (sentiment_ok and forecast_ok and structure_ok):
        return {
            'decision': 'no_entry',
            'sentiment_ok': sentiment_ok,
            'forecast_ok': forecast_ok,
            'structure_ok': structure_ok,
            'reason': 'Bias not confirmed'
        }

    # 3. Compute total confidence and risk
    structure_score = 1.0 if structure_ok else 0.0
    trade_confidence = compute_trade_confidence(sentiment['score'], abs(forecast), structure_score)
    if trade_confidence > 0.8:
        risk_pct = min(RISK_MAX, RISK_BASE * 1.5)
    elif trade_confidence > 0.6:
        risk_pct = max(RISK_MIN, RISK_BASE * 0.75)
    else:
        return {'decision': 'no_entry', 'reason': 'Low confidence'}

    # 4. Decide entry type
    entry_type = decide_entry_type(structure, sentiment['urgency'])

    # 5. Calculate SL/TP
    entry = market_state['entry']
    direction = 'buy' if sentiment['score'] > 0 else 'sell'
    volatility = market_state.get('volatility', 1.0)
    sl, tp = calculate_sl_tp(entry, direction, structure, volatility)

    # 6. Final output
    return {
        'decision': 'entry',
        'entry_type': entry_type,
        'direction': direction,
        'entry': entry,
        'sl': sl,
        'tp': tp,
        'risk_pct': risk_pct,
        'confidence': round(trade_confidence, 3),
        'timestamp': time.time(),
        'meta': {
            'sentiment': sentiment,
            'forecast': forecast,
            'structure': structure,
            'market_state': market_state
        }
    }

# Example usage (can be moved to tests/)
if __name__ == "__main__":
    sentiment = {'score': 0.82, 'urgency': 'high', 'direction': 'bullish'}
    forecast = 0.7
    structure = {'confirmed': True, 'type': 'breakout', 'sl_buffer': 0.5}
    market_state = {'entry': 1.234, 'volatility': 0.05, 'spread': 0.12, 'median_spread': 0.1, 'data_age': 4, 'median_volatility': 0.04}
    result = fuse_signals(sentiment, forecast, structure, market_state)
    print(result)