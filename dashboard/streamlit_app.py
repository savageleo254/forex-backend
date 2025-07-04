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

def load_alerts(log_file="logs/alerts.log", max_lines=50):
    if not os.path.exists(log_file):
        return []
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()[-max_lines:]
    return [line.strip() for line in lines]

def main():
    st.set_page_config(page_title="QuantOps Dashboard", layout="wide")
    st.title("📊 QuantOps Trading Dashboard")

    # Live Alerts Panel
    st.subheader("🚨 Live Alerts")
    alerts = load_alerts()
    if alerts:
        for alert in alerts[-10:][::-1]:
            st.info(alert)
    else:
        st.write("No alerts found.")

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

    # Config Switcher
    st.subheader("Config Switcher")
    configs = sorted(df['config'].dropna().unique().tolist())
    if not configs:
        configs = ["trend_model", "range_model", "volatility_model", "news_model"]
    current = st.selectbox("Switch Trading Config", configs)
    if st.button("Apply Config"):
        # Here, integrate with backend to update config if needed
        st.success(f"Config switched to: {current}")

    # Config breakdown
    st.subheader("By Config")
    st.bar_chart(df.groupby("config")["pnl"].sum())

    # Risk & Drawdown Monitor
    st.subheader("Risk & Drawdown Monitor")
    # Calculate max drawdown
    equity = df_sorted['equity'].values
    if len(equity) > 0:
        running_max = pd.Series(equity).cummax()
        drawdown = running_max - equity
        max_drawdown = drawdown.max()
    else:
        max_drawdown = 0.0
    st.metric("Max Drawdown", f"{max_drawdown:.2f}")
    risk_limit = st.number_input("Set Drawdown Risk-Off Limit", min_value=0.0, step=0.01, value=float(max_drawdown))
    if max_drawdown > risk_limit:
        st.error("⚠️ Drawdown exceeds limit! Risk-off recommended.")

    # Upload/Download & Data Export
    st.subheader("Upload/Download")
    uploaded = st.file_uploader("Upload new config", type=["json", "yaml"])
    if uploaded:
        st.write("Uploaded file:", uploaded.name)
        # Save or parse config as needed

    # Download latest report if exists
    report_dir = "reports"
    if os.path.isdir(report_dir):
        report_files = sorted(
            [f for f in os.listdir(report_dir) if f.startswith("daily_report") and f.endswith(".md")],
            reverse=True
        )
        if report_files:
            report_path = os.path.join(report_dir, report_files[0])
            with open(report_path, "rb") as f:
                st.download_button("Download Latest Report", f, file_name=report_files[0])

if __name__ == "__main__":
    main()