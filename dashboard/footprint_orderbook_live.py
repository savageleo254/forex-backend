import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import os

st.set_page_config(page_title="Forex Footprint - Live OrderBook", layout="wide")
st.title("📉 Forex Footprint (Order Book, Live Data)")

st.markdown("""
- Fetches live order book data from `/v3/market/orderBook`
- Shows footprint chart (buy/sell volumes at price levels)
- Auto-refreshes every 5 seconds
""")

API_URL = "http://localhost:8080/v3/market/orderBook"  # Change if needed

# Read token from environment variable
API_TOKEN = os.environ.get("API_TOKEN", "")

st_autorefresh(interval=5000, key="orderbook_autorefresh")

def fetch_orderbook():
    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    try:
        r = requests.get(API_URL, headers=headers, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching order book: {e}")
        return None

orderbook = fetch_orderbook()

if not orderbook:
    st.info("Waiting for order book data...")
else:
    timestamp = orderbook.get("timestamp", datetime.utcnow().isoformat())
    bids = orderbook.get("bids", [])
    asks = orderbook.get("asks", [])

    records = []
    for bid in bids:
        records.append({
            "time": timestamp,
            "price": bid["price"],
            "buy_volume": bid["volume"],
            "sell_volume": 0
        })
    for ask in asks:
        records.append({
            "time": timestamp,
            "price": ask["price"],
            "buy_volume": 0,
            "sell_volume": ask["volume"]
        })

    df = pd.DataFrame(records)
    df['time'] = pd.to_datetime(df['time'])
    df['price'] = df['price'].astype(float)
    df['buy_volume'] = df['buy_volume'].astype(float)
    df['sell_volume'] = df['sell_volume'].astype(float)

    side = st.radio("Show", ["Buy Volume", "Sell Volume", "Delta (Buy - Sell)"], horizontal=True)
    if side == "Buy Volume":
        volume_matrix = df.pivot_table(index="price", columns="time", values="buy_volume", fill_value=0)
        color_title = "Buy Volume"
    elif side == "Sell Volume":
        volume_matrix = df.pivot_table(index="price", columns="time", values="sell_volume", fill_value=0)
        color_title = "Sell Volume"
    else:
        df['delta'] = df['buy_volume'] - df['sell_volume']
        volume_matrix = df.pivot_table(index="price", columns="time", values="delta", fill_value=0)
        color_title = "Delta (Buy - Sell)"

    volume_matrix = volume_matrix.sort_index(ascending=False)  # Highest price at top

    fig = go.Figure(
        data=go.Heatmap(
            z=volume_matrix.values,
            x=[t.strftime("%H:%M:%S") for t in volume_matrix.columns],
            y=[f"{p:.5f}" for p in volume_matrix.index],
            colorscale="RdYlGn" if side == "Delta (Buy - Sell)" else "Blues",
            colorbar=dict(title=color_title),
            hoverongaps=False,
            hovertemplate="Time: %{x}<br>Price: %{y}<br>" + color_title + ": %{z}<extra></extra>"
        )
    )
    fig.update_layout(
        height=600,
        xaxis_title="Time",
        yaxis_title="Price",
        yaxis_autorange="reversed",
        margin=dict(t=40, b=40, l=80, r=40)
    )
    st.plotly_chart(fig, use_container_width=True)