import pandas as pd

class AdvancedOBFVG:
    def __init__(self, min_body_ratio=0.6, fvg_gap_thresh=0.5):
        self.min_body_ratio = min_body_ratio
        self.fvg_gap_thresh = fvg_gap_thresh

    def detect_multi_tf_ob(self, data_dict, direction="bullish"):
        """
        Multi-timeframe Order Block (OB) detection.
        data_dict: {"M1": df1, "M5": df5, ...} (keys = timeframe labels, values = OHLC DataFrames)
        Returns: list of dicts with 'timeframe', 'index', 'ob_type', 'price'
        """
        ob_results = []
        for tf, df in data_dict.items():
            ob_idx = self.find_last_ob(df, bullish=(direction=="bullish"))
            if ob_idx is not None:
                ob_type = "bullish" if direction=="bullish" else "bearish"
                ob_price = df['low'].iloc[ob_idx] if direction=="bullish" else df['high'].iloc[ob_idx]
                ob_results.append({
                    "timeframe": tf,
                    "index": ob_idx,
                    "ob_type": ob_type,
                    "price": ob_price
                })
        return ob_results

    def find_last_ob(self, df: pd.DataFrame, bullish=True):
        """
        Find last Order Block (OB) index in a single timeframe.
        """
        candle_body = (df['close'] - df['open']).abs()
        candle_range = (df['high'] - df['low'])
        body_ratio = candle_body / candle_range
        if bullish:
            direction_check = df['close'] < df['open']
        else:
            direction_check = df['close'] > df['open']
        candidates = df[direction_check & (body_ratio > self.min_body_ratio)]
        if not candidates.empty:
            return candidates.index[-1]
        return None

    def detect_multi_tf_fvg(self, data_dict, entry_idx_dict, direction="buy"):
        """
        Multi-timeframe Fair Value Gap (FVG) detection.
        data_dict: {"M1": df1, "M5": df5, ...}
        entry_idx_dict: {"M1": idx1, "M5": idx5, ...}
        Returns: list of dicts with 'timeframe', 'index', 'gap_type', 'price'
        """
        fvg_results = []
        for tf, df in data_dict.items():
            entry_idx = entry_idx_dict.get(tf, 0)
            fvg_idx = self.find_nearest_fvg(df, entry_idx, direction)
            if fvg_idx is not None:
                gap_type = "up" if direction == "buy" else "down"
                price = df['high'].iloc[fvg_idx] if direction == "buy" else df['low'].iloc[fvg_idx]
                fvg_results.append({
                    "timeframe": tf,
                    "index": fvg_idx,
                    "gap_type": gap_type,
                    "price": price
                })
        return fvg_results

    def find_nearest_fvg(self, df: pd.DataFrame, entry_idx: int, direction: str):
        """
        Find nearest FVG after entry in a single timeframe.
        """
        atr = (df['high'] - df['low']).rolling(window=14).mean()
        if direction == 'buy':
            for i in range(entry_idx + 1, len(df) - 1):
                gap = df['low'].iloc[i] - df['high'].iloc[i - 1]
                if gap > self.fvg_gap_thresh * atr.iloc[i]:
                    return i
        else:
            for i in range(entry_idx + 1, len(df) - 1):
                gap = df['low'].iloc[i - 1] - df['high'].iloc[i]
                if gap > self.fvg_gap_thresh * atr.iloc[i]:
                    return i
        return None

    def consolidate_multi_tf_signals(self, ob_results, fvg_results):
        """
        Consolidate detected OBs and FVGs from multiple timeframes.
        Prioritize higher timeframes if conflict.
        """
        consolidated = {
            "main_ob": None,
            "main_fvg": None,
            "all_obs": ob_results,
            "all_fvgs": fvg_results,
        }
        if ob_results:
            # Highest timeframe OB
            consolidated["main_ob"] = max(ob_results, key=lambda x: x['timeframe'])
        if fvg_results:
            # Highest timeframe FVG
            consolidated["main_fvg"] = max(fvg_results, key=lambda x: x['timeframe'])
        return consolidated