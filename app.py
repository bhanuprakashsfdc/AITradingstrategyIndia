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

@st.cache_data(ttl=300)
def load_summary():
    try:
        df = pd.read_csv('backtest_results/summary.csv')
        return df.iloc[0].to_dict()
    except FileNotFoundError:
        return None

@st.cache_data(ttl=300)
def load_trades():
    try:
        df = pd.read_csv('backtest_results/trades.csv')
        # Convert Return to percentage and format
        df['Return %'] = (df['Return'] * 100).round(2)
        # Drop raw Return column to avoid confusion
        df = df.drop(columns=['Return'])
        return df
    except FileNotFoundError:
        return pd.DataFrame()

# -----------------------------
# UI
# -----------------------------
st.title("📊 Nifty 50 Momentum Dashboard")

st.caption("Strategy: Current Price vs Previous Month-End | Ranked by Relative Strength vs NIFTYBEES")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Create tabs
tab1, tab2 = st.tabs(["📈 Dashboard", "📑 Trades"])

with tab1:
    # Load data
    df, bench_ret = build_dashboard()

    # METRICS
    col1, col2, col3 = st.columns(3)
    col1.metric("Benchmark Return (NIFTYBEES)", f"{bench_ret:.2f}%")
    col2.metric("Top Stock", df.iloc[0]["Symbol"])
    col3.metric("Top RS", f"{df.iloc[0]['RS %']:.2f}%")

    # TOP 5
    st.subheader("🔥 Top 5 Momentum Stocks")
    st.dataframe(df.head(5), width='stretch')

    # FULL TABLE
    st.subheader("📋 Full Ranking")
    st.dataframe(df.style.format({
        "Prev Price": "{:.2f}",
        "Current Price": "{:.2f}",
        "Return %": "{:.2f}",
        "RS %": "{:.2f}"
        }).background_gradient(subset=["RS %"], cmap="RdYlGn"), width='stretch')

    # DOWNLOAD
    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False),
        file_name="nifty50_momentum_dashboard.csv"
    )

    st.caption("⚠️ Uses same-time close logic (lookahead bias). For research only.")

with tab2:
    trades_df = load_trades()
    summary_data = load_summary()
    
    if summary_data is None:
        st.warning("No summary data found. Please run the backtest first.")
    else:
        # Display summary metrics from portfolio performance
        st.subheader("📊 Trading Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Invested", f"₹{summary_data['Initial Capital']:,.2f}")
        col2.metric("Current Worth", f"₹{summary_data['Final Capital']:,.2f}")
        col3.metric("Total Profit", f"₹{summary_data['Total PnL']:,.2f}")
        col4.metric("Profit %", f"{summary_data['Total Return %']:.2f}%")
        col5.metric("CAGR", f"{summary_data['CAGR']:.2f}%")
    
    if trades_df.empty:
        st.warning("No trades data found.")
    else:
        st.subheader("📑 All Trades")
        styled_trades = trades_df.style.format({
            "Entry Price": "{:.2f}",
            "Exit Price": "{:.2f}",
            "Allocation": "{:,.2f}",
            "P&L": "{:,.2f}",
            "Return %": "{:.2f}%"
        }).background_gradient(subset=["Return %"], cmap="RdYlGn")
        st.dataframe(styled_trades, width='stretch')

        st.download_button(
            "📥 Download Trades CSV",
            trades_df.to_csv(index=False),
            file_name="trades.csv"
        )