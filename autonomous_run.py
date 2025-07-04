# autonomous_run.py
"""
Savage Leo – Full Autonomous Mode Controller
Executes signal generation, alerting, journaling, and LLM review in one pass using live MT5 data.
"""

import os, json
from datetime import datetime, timezone
from dotenv import load_dotenv
import MetaTrader5 as mt5

from bot_engine.fusion_engine import fuse_signals
from alerts.telegram_alerts import send_telegram_alert
from journal.logger import log_fusion_result
from journal.llm_reviewer import review_trade_and_log

# === ENV ===
load_dotenv()

# === INIT MT5 ===
if not mt5.initialize():
    print("❌ MT5 initialization failed:", mt5.last_error())
    exit()

symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M5

# === LIVE PRICE DATA ===
tick = mt5.symbol_info_tick(symbol)
if tick is None:
    print("❌ Failed to fetch tick data")
    exit()

entry_price = tick.ask
spread = tick.ask - tick.bid

# === SIMULATED SMC/AI SIGNALS (to be upgraded) ===
sentiment = {"score": 0.85, "urgency": "high", "direction": "bullish"}
forecast = 0.72
structure = {"confirmed": True, "type": "breakout", "sl_buffer": 0.4}

# === MARKET STATE ===
market_state = {
    "entry": entry_price,
    "volatility": spread * 1.1,  # crude estimate for volatility
    "spread": spread,
    "median_spread": 0.09,
    "data_age": 0,
    "median_volatility": 0.1
}

# === FOLDER STRUCTURE CHECK ===
os.makedirs("signal", exist_ok=True)
os.makedirs("journal", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# === RUN DECISION ENGINE ===
fusion_result = fuse_signals(sentiment, forecast, structure, market_state)

# === DECISION HANDLING ===
if fusion_result and fusion_result.get("decision") == "entry":
    signal = {
        "symbol": symbol,
        "timeframe": "M5",
        "entry": fusion_result["entry"],
        "direction": fusion_result["direction"],
        "entry_type": fusion_result["entry_type"],
        "sl": fusion_result["sl"],
        "tp": fusion_result["tp"],
        "risk_pct": fusion_result["risk_pct"],
        "confidence": fusion_result["confidence"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    with open("signal/entry_signal.json", "w", encoding="utf-8") as f:
        json.dump(signal, f, indent=2)
    print("✅ Signal written to signal/entry_signal.json")

    log_fusion_result(signal)

    send_telegram_alert(
        f"🚨 *New Trade Signal*\nSymbol: {symbol}\n"
        f"Action: {fusion_result['direction'].upper()}\n"
        f"Confidence: {fusion_result['confidence']}\n"
        f"Risk: {fusion_result['risk_pct']}%\n"
        f"SL: {fusion_result['sl']} | TP: {fusion_result['tp']}"
    )

    signal["fused_score"] = fusion_result["confidence"]
    signal["forecast"] = forecast
    signal["sentiment"] = sentiment["score"]
    signal["smc_bias"] = sentiment["direction"]
    signal["action"] = signal["direction"].upper()
    review_trade_and_log(signal)

    # ✅ EXECUTE TRADE
    from trade_executor.mt5_order import send_order
    send_order(
        symbol=symbol,
        volume=0.1,
        type=signal["direction"],
        sl=signal["sl"],
        tp=signal["tp"],
        entry_type=signal["entry_type"]
    )

else:
    reason = fusion_result.get("reason", "No valid signal") if fusion_result else "❌ fusion_result is None (signal engine may have failed)"
    print(f"⚠️ No trade taken → {reason}")
    with open("logs/autonomous_skipped.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()} – {reason}\n")

# === CLEANUP ===
mt5.shutdown()
