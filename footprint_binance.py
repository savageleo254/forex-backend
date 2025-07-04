import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="BTCUSDT Binance Footprint", layout="wide")
st.title("📉 BTCUSDT Binance Footprint Chart (Live)")

st.markdown("""
- Fetches most recent 1000 aggregated trades from Binance.
- Shows footprint chart (buy/sell volumes at price levels).
- Auto-refreshes every 5 seconds.
""")

st_autorefresh(interval=5000, key="binance_footprint_autorefresh")

API_URL = "https://api.binance.com/api/v3/aggTrades?symbol=BTCUSDT&limit=1000"

def fetch_binance_aggtrades():
    try:
        r = requests.get(API_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching Binance trades: {e}")
        return []

agg_trades = fetch_binance_aggtrades()

if not agg_trades:
    st.info("Waiting for Binance data...")
else:
    # Parse into DataFrame
    df = pd.DataFrame(agg_trades)
    # Price and volume as float
    df['p'] = df['p'].astype(float)  # price
    df['q'] = df['q'].astype(float)  # quantity
    df['T'] = pd.to_datetime(df['T'], unit='ms')  # trade time
    df['side'] = np.where(df['m'], 'sell', 'buy')  # 'm' is True if buyer is the market maker (i.e. sell)

    # Choose price bucket size (for footprint rows)
    bucket_size = st.select_slider("Price Bucket Size (USD)", options=[1, 2, 5, 10, 20, 50, 100], value=10)
    df['price_bucket'] = (df['p'] // bucket_size) * bucket_size

    # Aggregate volume by bucket and side
    buy_df = df[df['side']=='buy'].groupby('price_bucket')['q'].sum().reset_index(name='buy_volume')
    sell_df = df[df['side']=='sell'].groupby('price_bucket')['q'].sum().reset_index(name='sell_volume')
    merged = pd.merge(buy_df, sell_df, on='price_bucket', how='outer').fillna(0)
    merged['delta'] = merged['buy_volume'] - merged['sell_volume']

    # Sort for heatmap
    merged = merged.sort_values('price_bucket', ascending=False)

    # Prepare for chart
    side = st.radio("Show", ["Buy Volume", "Sell Volume", "Delta (Buy - Sell)"], horizontal=True)
    z = merged['buy_volume'] if side == "Buy Volume" else merged['sell_volume'] if side == "Sell Volume" else merged['delta']
    colorscale = "Blues" if side != "Delta (Buy - Sell)" else "RdYlGn"
    color_title = side

    fig = go.Figure(
        data=go.Heatmap(
            z=[z.values],  # 2D array (1 row)
            x=[f"{int(p)}" for p in merged['price_bucket']],
            y=[side],
            colorscale=colorscale,
            colorbar=dict(title=color_title),
            hoverongaps=False,
            hovertemplate="Price: %{x}<br>" + color_title + ": %{z}<extra></extra>"
        )
    )
    fig.update_layout(
        height=300,
        xaxis_title="Price (bucketed)",
        yaxis_title="",
        margin=dict(t=40, b=40, l=80, r=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Data updates every 5 seconds from live Binance aggTrades endpoint.")