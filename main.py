import sys
if sys.version_info >= (3, 13):
    raise RuntimeError("❌ Savage Leo does not support Python 3.13+. Downgrade to 3.11.")
# main.py – Real-Time Autonomous Trade Signal Generator
import os
import json
from datetime import datetime
from dotenv import load_dotenv

from bot_engine.fusion_engine import fuse_signals
from alerts.telegram_alerts import send_telegram_alert
from journal.logger import log_fusion_result
from journal.llm_reviewer import review_trade_and_log

# Load environment
load_dotenv()

# === SIMULATED MARKET INPUTS (replace with live feed later) ===
symbol = "XAUUSD"
timeframe = "M5"
entry_price = 2363.75
volatility = 0.12
spread = 0.15
median_spread = 0.1
median_volatility = 0.1

# === STUBBED SIGNAL COMPONENTS ===
sentiment = {
    "score": 0.85,
    "urgency": "high",
    "direction": "bullish"
}

forecast = 0.72  # From Prophet/Informer

structure = {
    "confirmed": True,
    "type": "breakout",
    "sl_buffer": 0.5
}

market_state = {
    "entry": entry_price,
    "volatility": volatility,
    "spread": spread,
    "median_spread": median_spread,
    "median_volatility": median_volatility,
    "data_age": 2
}

# === RUN FUSION DECISION ===
fusion_result = fuse_signals(sentiment, forecast, structure, market_state)

# === HANDLE DECISION LOGIC ===
os.makedirs("signal", exist_ok=True)
signal_path = "signal/entry_signal.json"
journal_path = "journal/trade_log.jsonl"
review_path = "journal/llm_review_log.jsonl"

if fusion_result["decision"] == "entry":
    # ✅ Write trade intent to signal file
    signal_payload = {
        "symbol": symbol,
        "timeframe": timeframe,
        "entry": fusion_result["entry"],
        "direction": fusion_result["direction"],
        "entry_type": fusion_result["entry_type"],
        "sl": fusion_result["sl"],
        "tp": fusion_result["tp"],
        "risk_pct": fusion_result["risk_pct"],
        "confidence": fusion_result["confidence"],
        "timestamp": datetime.utcnow().isoformat()
    }

    with open(signal_path, "w") as f:
        json.dump(signal_payload, f, indent=2)

    print(f"✅ Trade signal written to {signal_path}")

    # ✅ Log trade to journal
    log_fusion_result(signal_payload)

    # ✅ Send Telegram alert
    send_telegram_alert(
        f"🚨 *Trade Signal*\nSymbol: {symbol}\nAction: {fusion_result['direction'].upper()}\n"
        f"Confidence: {fusion_result['confidence']}\nRisk: {fusion_result['risk_pct']}%\nSL: {fusion_result['sl']} TP: {fusion_result['tp']}"
    )

    # ✅ Run LLM Reviewer
    review_trade_and_log(signal_payload)

else:
    print(f"⚠️ No trade taken: {fusion_result.get('reason', 'Unknown reason')}")
    # Optional: write reason to logs
