import numpy as np

def detect_regime(prices, window=50):
    """
    Detects market regime: 'trend', 'range', 'volatile', or 'news'
    - prices: list or np.array of recent close prices
    - window: lookback for stats
    Returns: regime string
    """
    if len(prices) < window:
        return "unknown"
    returns = np.diff(prices[-window:]) / prices[-window:-1]
    volatility = np.std(returns)
    mean_return = np.mean(returns)
    # Simple heuristics
    if volatility > 0.02:
        return "volatile"
    if abs(mean_return) > 0.004:
        return "trend"
    if volatility < 0.007:
        return "range"
    # Optionally, check for external news regime flag
    return "normal"

def select_model_for_regime(regime):
    """
    Maps regime to model/config
    """
    if regime == "trend":
        return "trend_model"
    elif regime == "range":
        return "range_model"
    elif regime == "volatile":
        return "volatility_model"
    elif regime == "news":
        return "news_model"
    else:
        return "default_model"

# Example usage
if __name__ == "__main__":
    prices = np.random.normal(100, 0.5, 100).cumsum()
    regime = detect_regime(prices)
    model = select_model_for_regime(regime)
    print(f"Detected regime: {regime} -> Using model: {model}")