import pandas as pd
from order_manager.dynamic_order_manager import DynamicOrderManager
from order_manager.advanced_ob_fvg import AdvancedOBFVG
from technical_analysis.structure_analyzer import TechnicalAnalyzer, StructureState

class ContextAwareOrderManager:
    def __init__(self, atr_period=14, risk_pct=1.0, min_body_ratio=0.6, fvg_gap_thresh=0.5):
        self.dynamic_manager = DynamicOrderManager(atr_period=atr_period, risk_pct=risk_pct)
        self.advanced_ob_fvg = AdvancedOBFVG(min_body_ratio=min_body_ratio, fvg_gap_thresh=fvg_gap_thresh)
        self.tech_analyzer = TechnicalAnalyzer()

    def compute_contextual_sl_tp(
        self, data_dict, entry_idx_dict, direction, context_df_key="M5"
    ):
        """
        Integrate multi-timeframe OB/FVG and technical analysis for SL/TP.
        :param data_dict: dict of {tf: pd.DataFrame} (OHLCV per timeframe)
        :param entry_idx_dict: dict of {tf: int} (entry index per timeframe)
        :param direction: 'buy' or 'sell'
        :param context_df_key: key for main context timeframe (default "M5")
        :return: (stop_loss, take_profit, context_signals)
        """
        # 1. Multi-TF OB and FVG detection
        ob_signals = self.advanced_ob_fvg.detect_multi_tf_ob(data_dict, direction="bullish" if direction == "buy" else "bearish")
        fvg_signals = self.advanced_ob_fvg.detect_multi_tf_fvg(data_dict, entry_idx_dict, direction=direction)

        context_consolidated = self.advanced_ob_fvg.consolidate_multi_tf_signals(ob_signals, fvg_signals)

        # 2. Technical structure analysis (use context_df_key, e.g. "M5")
        structure_state = None
        if context_df_key in data_dict:
            df_context = data_dict[context_df_key]
            structure_state = self.tech_analyzer.detect_market_structure(df_context)

        # 3. Context-aware SL/TP logic (priority: OB > FVG > ATR/static)
        main_ob = context_consolidated["main_ob"]
        main_fvg = context_consolidated["main_fvg"]
        entry_idx = entry_idx_dict.get(context_df_key, 0)
        df_context = data_dict[context_df_key]

        if main_ob:
            # Use OB-based SL/TP
            if direction == "buy":
                sl = main_ob["price"]
                tp = df_context['close'].iloc[entry_idx] + 2 * self.dynamic_manager.calculate_atr(df_context).iloc[entry_idx]
            else:
                sl = main_ob["price"]
                tp = df_context['close'].iloc[entry_idx] - 2 * self.dynamic_manager.calculate_atr(df_context).iloc[entry_idx]
        elif main_fvg:
            # Use FVG-based SL/TP
            if direction == "buy":
                sl = df_context['close'].iloc[entry_idx] - 1.5 * self.dynamic_manager.calculate_atr(df_context).iloc[entry_idx]
                tp = main_fvg["price"]
            else:
                sl = df_context['close'].iloc[entry_idx] + 1.5 * self.dynamic_manager.calculate_atr(df_context).iloc[entry_idx]
                tp = main_fvg["price"]
        else:
            # Default to ATR-based
            sl, tp = self.dynamic_manager.dynamic_sl_tp(df_context, entry_idx)

        # 4. Package context signals for transparency/logging
        context_signals = {
            "structure_state": structure_state.to_dict() if structure_state else None,
            "multi_tf_ob": ob_signals,
            "multi_tf_fvg": fvg_signals,
            "main_ob": main_ob,
            "main_fvg": main_fvg
        }

        return sl, tp, context_signals