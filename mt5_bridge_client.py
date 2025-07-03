import json
import os
import time
from typing import Dict

TRADE_COMMAND_DIR = "C:/AI_System/trade_commands"
TRADE_ACK_DIR = "C:/AI_System/trade_acks"

os.makedirs(TRADE_COMMAND_DIR, exist_ok=True)
os.makedirs(TRADE_ACK_DIR, exist_ok=True)

def send_trade_command(trade: Dict):
    """
    Send trade command to MT5 via file bridge.
    """
    trade_id = f"{trade['symbol']}_{int(time.time()*1000)}"
    trade['trade_id'] = trade_id
    trade['timestamp'] = time.time()
    fname = os.path.join(TRADE_COMMAND_DIR, f"{trade_id}.json")
    tmp_fname = fname + ".tmp"
    with open(tmp_fname, "w") as f:
        json.dump(trade, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_fname, fname)
    print(f"Trade command written: {fname}")
    return trade_id

def wait_for_ack(trade_id, timeout=10):
    """
    Wait for acknowledgment from MT5 EA.
    """
    ack_file = os.path.join(TRADE_ACK_DIR, f"{trade_id}.json")
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(ack_file):
            with open(ack_file) as f:
                ack = json.load(f)
            os.remove(ack_file)
            return ack
        time.sleep(0.2)
    return {"status": "timeout", "trade_id": trade_id}

# Example usage
if __name__ == "__main__":
    trade = {
        "symbol": "XAUUSD",
        "direction": "BUY",
        "volume": 0.1,
        "sl": 2350.0,
        "tp": 2370.0
    }
    trade_id = send_trade_command(trade)
    ack = wait_for_ack(trade_id)
    print("MT5 EA Response:", ack)