import json
import os
import streamlit as st
import pandas as pd
from datetime import datetime

JOURNAL_FILE = "logs/trade_journal.jsonl"

def load_journal():
    if not os.path.exists(JOURNAL_FILE):
        return []
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def preprocess_trades(trades):
    rows = []
    for t in trades:
        row = {
            "timestamp": t.get("timestamp", ""),
            "symbol": t.get("trade_context", {}).get("symbol", ""),
            "side": t.get("trade_context", {}).get("side", ""),
            "config": t.get("trade_context", {}).get("config", ""),
            "result": t.get("outcome", {}).get("result", ""),
            "pnl": t.get("outcome", {}).get("pnl", 0),
            "rationale": t.get("rationale", ""),
        }
        rows.append(row)
    return pd.DataFrame(rows)

def main():
    st.set_page_config(page_title="QuantOps Dashboard", layout="wide")
    st.title("📊 QuantOps Trading Dashboard")

    trades = load_journal()
    if not trades:
        st.warning("No trades found in journal.")
        return

    df = preprocess_trades(trades)

    # Summary stats
    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", len(df))
    col2.metric("Total PnL", round(df['pnl'].sum(), 2))
    col3.metric("Win Rate (%)", round(100 * (df['result'] == 'win').sum() / max(1,len(df)), 2))
    col4.metric("Configs Used", df['config'].nunique())

    # PnL over time
    st.subheader("Equity Curve")
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df_sorted = df.sort_values("timestamp")
    df_sorted['equity'] = df_sorted['pnl'].cumsum()
    st.line_chart(df_sorted.set_index("timestamp")['equity'])

    # Trades Table
    st.subheader("Trades Table (Last 50)")
    st.dataframe(df_sorted.tail(50).reset_index(drop=True), use_container_width=True)

    # Rationale inspection
    st.subheader("LLM Rationales")
    idx = st.slider("Select trade index", 0, len(df_sorted)-1, len(df_sorted)-1)
    st.write(f"**Trade {idx} | {df_sorted.iloc[idx]['symbol']} | {df_sorted.iloc[idx]['timestamp']}**")
    st.write(df_sorted.iloc[idx]['rationale'])

    # Config breakdown
    st.subheader("By Config")
    st.bar_chart(df.groupby("config")["pnl"].sum())

    # Extension: Add upload, download, or live broker integration here

if __name__ == "__main__":
    main()