import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Forex Footprint Chart", layout="wide")
st.title("📉 Forex Footprint (Order Flow) Chart")

st.markdown("""
This chart shows buy/sell volumes at each price for each time interval (aka order flow/footprint chart).
- **Upload your CSV**: Columns required - `time`, `price`, `buy_volume`, `sell_volume`
- Hover for exact values. Use the selector to choose which side to view.
""")

uploaded = st.file_uploader("Upload footprint CSV", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
    # Ensure correct dtypes
    df['time'] = pd.to_datetime(df['time'])
    df['price'] = df['price'].astype(float)
    df['buy_volume'] = df['buy_volume'].astype(float)
    df['sell_volume'] = df['sell_volume'].astype(float)
else:
    # Generate sample data for demo
    times = pd.date_range("2024-07-01 12:00", periods=10, freq="T")
    prices = np.arange(1.0700, 1.0730, 0.0005)
    data = []
    rng = np.random.default_rng(42)
    for t in times:
        for p in prices:
            data.append({
                "time": t,
                "price": round(p, 5),
                "buy_volume": rng.integers(0, 30),
                "sell_volume": rng.integers(0, 30)
            })
    df = pd.DataFrame(data)

# Pivot to get matrix: rows = price, columns = time, values = buy/sell volume
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

# Sort for display
volume_matrix = volume_matrix.sort_index(ascending=False)  # Highest price at top

fig = go.Figure(
    data=go.Heatmap(
        z=volume_matrix.values,
        x=[t.strftime("%H:%M") for t in volume_matrix.columns],
        y=[f"{p:.5f}" for p in volume_matrix.index],
        colorscale="RdYlGn" if side == "Delta (Buy - Sell)" else "Blues",
        colorbar=dict(title=color_title),
        hoverongaps=False,
        hovertemplate="Time: %{x}<br>Price: %{y}<br>"+color_title+": %{z}<extra></extra>"
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

st.caption("Tip: Upload your own data for real markets. This demo uses random data if no CSV is uploaded.")