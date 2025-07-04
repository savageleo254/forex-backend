# trade_executor/mt5_order.py

import MetaTrader5 as mt5
from datetime import datetime

def send_order(symbol: str, volume: float, type: str, sl: float, tp: float, entry_type: str = "market"):
    """
    Places a buy/sell order using MetaTrader 5.
    :param symbol: str - e.g., 'XAUUSD'
    :param volume: float - e.g., 0.1
    :param type: str - 'buy' or 'sell'
    :param sl: float - stop loss price
    :param tp: float - take profit price
    :param entry_type: str - 'market' or 'limit'
    :return: None
    """
    action_type = mt5.ORDER_TYPE_BUY if type == "buy" else mt5.ORDER_TYPE_SELL
    
    price = mt5.symbol_info_tick(symbol).ask if action_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL if entry_type == "market" else mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": action_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 911911,
        "comment": f"SavageLeo-{type}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Order failed → Code: {result.retcode} | Msg: {result.comment}")
    else:
        print(f"✅ Order placed successfully → Ticket: {result.order}, Price: {price}")
