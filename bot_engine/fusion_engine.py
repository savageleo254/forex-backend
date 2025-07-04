"""
Signal Fusion & Decision Logic Engine
Institutional-grade trade trigger logic for QuantOps AI stack.
"""

from typing import Dict, Any
import numpy as np
import time

# === CONFIGURABLE CONSTANTS ===
SENTIMENT_THRESHOLD = 0.65
SENTIMENT_URGENCY_MIN = 'medium'  # low < medium < high
FORECAST_MIN_AGREEMENT = 0.5

STRUCTURE_CONFIRMATION_REQUIRED = True
WEIGHTS = {'sentiment': 0.4, 'forecast': 0.3, 'structure': 0.3}

RISK_BASE = 1.0      # % of equity
RISK_MAX = 2.0
RISK_MIN = 0.25

# === HELPERS ===

def urgency_rank(urgency: str) -> int:
    return {'low': 0, 'medium': 1, 'high': 2}.get(urgency.lower(), 0)

def compute_trade_confidence(sentiment_score, forecast_score, structure_score):
    return (
        WEIGHTS['sentiment'] * abs(sentiment_score) +
        WEIGHTS['forecast'] * forecast_score +
        WEIGHTS['structure'] * structure_score
    )

def decide_entry_type(structure, urgency):
    if structure.get('type') == 'breakout' and urgency.lower() == 'high':
        return 'market'
    return 'limit'

def calculate_sl_tp(entry, direction, structure, volatility, rr=2.0):
    buffer = structure.get('sl_buffer', 0.0) + volatility
    if direction == 'buy':
        sl = entry - buffer
        tp = entry + (abs(entry - sl) * rr)
    else:
        sl = entry + buffer
        tp = entry - (abs(entry - sl) * rr)
    return round(sl, 3), round(tp, 3)

# === CORE FUSION ENGINE ===

def fuse_signals(
    sentiment: Dict[str, Any],
    forecast: float,
    structure: Dict[str, Any],
    market_state: Dict[str, Any],
    equity: float = 10000.0
) -> Dict[str, Any]:
    """
    Fuse multiple trading signals into a final trade intent decision.

    Inputs:
    - sentiment: {'score': float, 'urgency': str, 'direction': str}
    - forecast: float (directional confidence: -1.0 to 1.0)
    - structure: {'confirmed': bool, 'type': str, 'sl_buffer': float}
    - market_state: {'entry': float, 'volatility': float, 'spread': float, 'median_spread': float, 'data_age': int}

    Returns: trade intent dict
    """

    # === PRE-TRADE BLOCKERS ===
    if market_state['spread'] > 1.5 * market_state.get('median_spread', 1.0):
        return {'decision': 'block', 'reason': 'Spread too high'}
    if market_state.get('data_age', 0) > 20:
        return {'decision': 'block', 'reason': 'Market data too stale'}
    if market_state.get('volatility', 1.0) > 3 * market_state.get('median_volatility', 1.0):
        return {'decision': 'block', 'reason': 'Volatility spike'}

    # === BIAS CONFIRMATION ===
    sentiment_ok = abs(sentiment['score']) >= SENTIMENT_THRESHOLD and \
                   urgency_rank(sentiment['urgency']) >= urgency_rank(SENTIMENT_URGENCY_MIN)
    forecast_ok = abs(forecast) >= FORECAST_MIN_AGREEMENT and \
                  np.sign(forecast) == np.sign(sentiment['score'])
    structure_ok = structure.get('confirmed', False)

    if not (sentiment_ok and forecast_ok and structure_ok):
        return {
            'decision': 'no_entry',
            'sentiment_ok': sentiment_ok,
            'forecast_ok': forecast_ok,
            'structure_ok': structure_ok,
            'reason': 'Bias not confirmed'
        }

    # === CONFIDENCE CALCULATION ===
    structure_score = 1.0 if structure_ok else 0.0
    confidence = compute_trade_confidence(sentiment['score'], abs(forecast), structure_score)

    # === RISK SCALING ===
    if confidence >= 0.8:
        risk_pct = min(RISK_MAX, RISK_BASE * 1.5)
    elif confidence >= 0.6:
        risk_pct = max(RISK_MIN, RISK_BASE * 0.75)
    else:
        return {'decision': 'no_entry', 'reason': 'Confidence too low'}

    # === ENTRY SETUP ===
    entry_type = decide_entry_t_
