# run_tests.py – returns exit‑code 0 if green
import importlib
def main() -> bool:
    try:
        import bot_engine.fusion_engine as fe
        # 1. quick smoke‑test
        sentiment = {'score': 0.8, 'urgency': 'high'}
        forecast  = 0.6
        structure = {'confirmed': True, 'type': 'breakout', 'sl_buffer': 0.3}
        mkt       = {'entry': 1.23, 'volatility': 0.05, 'spread': 0.1,
                     'median_spread': 0.1, 'median_volatility': 0.04}
        fe.fuse_signals(sentiment, forecast, structure, mkt)
        # 2. add more asserts here…
        return True
    except Exception as e:
        print("TEST FAILURE:", e)
        return False

if __name__ == "__main__":
    import sys;  sys.exit(0 if main() else 1)
