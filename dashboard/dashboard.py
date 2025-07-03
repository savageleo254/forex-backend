import streamlit as st
import pandas as pd
import json
import os

st.title("QuantOps AI Live Dashboard")

log_path = os.path.join("logs", "trade_journal.jsonl")

if os.path.exists(log_path):
    with open(log_path) as f:
        lines = f.readlines()
    data = [json.loads(line) for line in lines if line.strip()]
    df = pd.DataFrame(data)
    st.write("Recent Trades", df.tail(10))
    st.write("Performance", pd.DataFrame([{
        "Winrate": sum(1 for x in data[-100:] if x["outcome"]["result"]=="win") / max(1, len(data[-100:])),
        "Total PnL": sum(x["outcome"].get("pnl", 0) for x in data[-100:])
    }]))
else:
    st.warning("No trade journal yet. Start trading to populate data.")