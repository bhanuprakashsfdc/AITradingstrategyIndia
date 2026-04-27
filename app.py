import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Nifty 50 Momentum Dashboard", layout="wide")

NIFTY50_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "ITC.NS", "LT.NS", "SBIN.NS", "HINDUNILVR.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
    "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "POWERGRID.NS",
    "NTPC.NS", "ONGC.NS", "COALINDIA.NS", "BAJFINANCE.NS",
    "BAJAJFINSV.NS", "INDUSINDBK.NS", "ADANIENT.NS", "ADANIPORTS.NS",
    "JSWSTEEL.NS", "TATASTEEL.NS", "GRASIM.NS", "HINDALCO.NS",
    "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS",
    "EICHERMOT.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "BPCL.NS",
    "BRITANNIA.NS", "SHREECEM.NS", "UPL.NS", "SBILIFE.NS",
    "HDFCLIFE.NS", "TATACONSUM.NS", "IOC.NS", "M&M.NS"
]

BENCHMARK = "NIFTYBEES.NS"

# -----------------------------
# UTIL FUNCTIONS
# -----------------------------
def get_prev_month_end():
    today = datetime.today()
    first_day = today.replace(day=1)
    return first_day - timedelta(days=1)

@st.cache_data(ttl=300)
def fetch_data(symbols):
    all_symbols = symbols + [BENCHMARK]
    df = yf.download(all_symbols, period="3mo", interval="1d", group_by="ticker", auto_adjust=True)
    return df

def build_dashboard():
    data = fetch_data(NIFTY50_SYMBOLS)
    prev_month_end = get_prev_month_end()

    results = []

    # Benchmark
    bench_df = data[BENCHMARK].dropna()
    bench_prev = bench_df.loc[:prev_month_end].iloc[-1]["Close"]
    bench_current = bench_df.iloc[-1]["Close"]
    bench_return = (bench_current - bench_prev) / bench_prev

    # Stocks
    for symbol in NIFTY50_SYMBOLS:
        try:
            df = data[symbol].dropna()

            prev_price = df.loc[:prev_month_end].iloc[-1]["Close"]
            current_price = df.iloc[-1]["Close"]

            stock_return = (current_price - prev_price) / prev_price
            rs = stock_return - bench_return

            results.append({
                "Symbol": symbol,
                "Prev Price": prev_price,
                "Current Price": current_price,
                "Return %": stock_return * 100,
                "RS %": rs * 100
            })

        except Exception:
            continue

    df = pd.DataFrame(results)
    df = df.sort_values(by="RS %", ascending=False)
    df["Rank"] = range(1, len(df) + 1)

    return df, bench_return * 100

# -----------------------------
# UI
# -----------------------------
st.title("📊 Nifty 50 Momentum Dashboard")

st.caption("Strategy: Current Price vs Previous Month-End | Ranked by Relative Strength vs NIFTYBEES")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Load data
df, bench_ret = build_dashboard()

# -----------------------------
# METRICS
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Benchmark Return (NIFTYBEES)", f"{bench_ret:.2f}%")
col2.metric("Top Stock", df.iloc[0]["Symbol"])
col3.metric("Top RS", f"{df.iloc[0]['RS %']:.2f}%")

# -----------------------------
# TOP 5
# -----------------------------
st.subheader("🔥 Top 5 Momentum Stocks")
st.dataframe(df.head(5), width='stretch')

# -----------------------------
# FULL TABLE
# -----------------------------
st.subheader("📋 Full Ranking")
st.dataframe(df.style.format({
    "Prev Price": "{:.2f}",
    "Current Price": "{:.2f}",
    "Return %": "{:.2f}",
    "RS %": "{:.2f}"
    }).background_gradient(subset=["RS %"], cmap="RdYlGn"), width='stretch')

# -----------------------------
# DOWNLOAD
# -----------------------------
st.download_button(
    "📥 Download CSV",
    df.to_csv(index=False),
    file_name="nifty50_momentum_dashboard.csv"
)

# -----------------------------
# FOOTER
# -----------------------------
st.caption("⚠️ Uses same-time close logic (lookahead bias). For research only.")