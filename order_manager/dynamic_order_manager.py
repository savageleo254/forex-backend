import pandas as pd

class DynamicOrderManager:
    def __init__(self, atr_period=14, risk_pct=1.0):
        self.atr_period = atr_period
        self.risk_pct = risk_pct  # Risk % per trade (basis for SL/TP sizing)

    def calculate_atr(self, df: pd.DataFrame):
        """
        Calculate the Average True Range (ATR) for dynamic SL/TP.
        Expects columns: 'high', 'low', 'close'
        """
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=self.atr_period).mean()
        return atr

    def dynamic_sl_tp(self, df: pd.DataFrame, entry_idx: int, 
                      sl_mult=1.5, tp_mult=2.5):
        """
        Calculate dynamic Stop Loss (SL) and Take Profit (TP) based on ATR.
        :param df: DataFrame with OHLC data
        :param entry_idx: Index of entry candle
        :param sl_mult: Multiplier for SL
        :param tp_mult: Multiplier for TP
        :return: (stop_loss, take_profit)
        """
        atr = self.calculate_atr(df)
        entry_price = df['close'].iloc[entry_idx]
        current_atr = atr.iloc[entry_idx]
        stop_loss = entry_price - sl_mult * current_atr
        take_profit = entry_price + tp_mult * current_atr
        return stop_loss, take_profit

    def trailing_sl(self, current_price, entry_price, atr, trail_mult=1.0):
        """
        Trailing stop logic based on ATR.
        """
        trail_stop = max(entry_price, current_price - trail_mult * atr)
        return trail_stop

    # TODO: Add OB/FVG-based logic and regime-adaptive sizing here.