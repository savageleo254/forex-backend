import threading
from bot_engine.feed_normalizer import get_normalized_market_state
from bot_engine.signal_fusion import fuse_signals
from bot_engine.rule_engine import check_guardrails
from journal.trade_journaler import log_trade
from mt5_bridge.mt5_bridge_client import send_trade_command, wait_for_ack

SYMBOLS = ["XAUUSD", "EURUSD", "GBPJPY"]
STRATEGIES = ["default"] # Extendable: plug in more signal engines

def process_symbol(symbol, strategy="default"):
    # Example: run full loop for a symbol, can be extended per strategy
    print(f"[{symbol}] Starting strategy: {strategy}")
    # 1. Ingest data
    market_state = get_normalized_market_state(symbol)
    # 2. Run signal logic (stub: replace with your fusion/strategy logic)
    sentiment = {"score": 0.8, "urgency": "high", "direction": "bullish"}
    forecast = 0.7
    structure = {"confirmed": True, "type": "breakout", "sl_buffer": 0.3}
    fusion_decision = fuse_signals(sentiment, forecast, structure, market_state)
    news_context = {}  # Optionally pull from news module

    # 3. Guardrails
    allowed, reason = check_guardrails(market_state, fusion_decision, news_context)
    if not allowed or fusion_decision.get("decision") != "entry":
        print(f"[{symbol}] Trade blocked: {reason}")
        return

    # 4. Trade execution
    trade = {
        "symbol": symbol,
        "direction": fusion_decision["direction"].upper(),
        "volume": 0.1,  # Risk/size logic can be plugged in here
        "sl": fusion_decision["sl"],
        "tp": fusion_decision["tp"]
    }
    trade_id = send_trade_command(trade)
    ack = wait_for_ack(trade_id)

    # 5. Journal
    log_trade(
        trade_context={
            "symbol": symbol,
            "strategy": strategy,
            "fusion_inputs": {
                "sentiment": sentiment,
                "forecast": forecast,
                "structure": structure,
                "market_state": market_state
            }
        },
        execution_result={
            "trade_id": trade_id,
            "ack": ack,
            "entry_price": market_state["bid"] if fusion_decision["direction"] == "buy" else market_state["ask"]
        },
        outcome={"result": "pending"}
    )
    print(f"[{symbol}] Trade processed and journaled.")

def run_all_symbols():
    threads = []
    for symbol in SYMBOLS:
        t = threading.Thread(target=process_symbol, args=(symbol,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    run_all_symbols()