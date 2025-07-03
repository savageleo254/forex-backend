from MetaTrader5 import initialize, copy_rates_from_pos, symbol_info_tick
import pandas as pd

def get_normalized_market_state(symbol, timeframe='M1', count=50):
    initialize()
    import MetaTrader5 as mt5
    df = pd.DataFrame(copy_rates_from_pos(symbol, getattr(mt5, timeframe), 0, count))
    tick = symbol_info_tick(symbol)
    normalized = {
        "symbol": symbol,
        "bid": tick.bid,
        "ask": tick.ask,
        "spread": round(tick.ask - tick.bid, 5),
        "ohlc": df.iloc[-1][['open', 'high', 'low', 'close']].to_dict(),
        "volume": df.iloc[-1]['tick_volume'],
        "timestamp": str(df.iloc[-1]['time'])
    }
    return normalized

if __name__ == "__main__":
    print(get_normalized_market_state("XAUUSD"))