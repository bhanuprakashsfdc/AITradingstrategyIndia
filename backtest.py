import os
import pandas as pd
import numpy as np

# -----------------------------
# CONFIG
# -----------------------------
DATA_DIR = "data"
RESULTS_DIR = "backtest_results"
BENCHMARK = "NIFTYBEES.NS"
INITIAL_CAPITAL = 100000
TOP_N = 5
STOP_LOSS = 0.15

# -----------------------------
# LOAD DATA
# -----------------------------
def load_data():
    data = {}

    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv"):
            # Skip rows 1 and 2 which contain ticker metadata and a spurious "Date" row
            df = pd.read_csv(os.path.join(DATA_DIR, file), skiprows=[1, 2])
            # Rename the first column (unnamed in CSV) to "Date"
            df.rename(columns={df.columns[0]: "Date"}, inplace=True)
            df["Date"] = pd.to_datetime(df["Date"])
            df.set_index("Date", inplace=True)
            df = df.sort_index()

            symbol = file.replace(".csv", "")
            data[symbol] = df

    return data

# -----------------------------
# MONTHLY RETURNS
# -----------------------------
def compute_monthly_returns(data):
    monthly_prices = {}

    for symbol, df in data.items():
        monthly_prices[symbol] = df["Close"].resample("ME").last()

    monthly_df = pd.DataFrame(monthly_prices)
    monthly_returns = monthly_df.pct_change()

    return monthly_df, monthly_returns

# -----------------------------
# BACKTEST
# -----------------------------
def backtest(data):
    monthly_prices, monthly_returns = compute_monthly_returns(data)

    if BENCHMARK not in monthly_returns.columns:
        raise ValueError(f"{BENCHMARK} data not found in data folder")

    benchmark_returns = monthly_returns[BENCHMARK]
    dates = monthly_returns.index

    capital = INITIAL_CAPITAL
    history = []
    trades = []  # <-- Track individual trades

    for i in range(1, len(dates) - 1):
        date = dates[i]

        if pd.isna(benchmark_returns.loc[date]):
            continue

        # Relative Strength
        rs = monthly_returns.loc[date] - benchmark_returns.loc[date]
        rs = rs.drop(BENCHMARK, errors="ignore")
        top_stocks = rs.sort_values(ascending=False).head(TOP_N).index.tolist()

        next_date = dates[i + 1]
        allocation = capital / TOP_N
        new_capital = 0

        for stock in top_stocks:
            df = data[stock]

            try:
                # Entry: last trading day on or before month-end 'date'
                entry_candidates = df.index[df.index <= date]
                if len(entry_candidates) == 0:
                    continue
                entry_date = entry_candidates[-1]
                entry_price = df.loc[entry_date, "Close"]

                # Exit: last trading day on or before next month-end
                exit_candidates = df.index[df.index <= next_date]
                if len(exit_candidates) == 0:
                    continue
                exit_date = exit_candidates[-1]

                # Stop loss check: days between entry+1 and exit_date inclusive
                period_data = df.loc[entry_date:exit_date]
                if len(period_data) > 1:
                    period_data = period_data.iloc[1:]  # exclude entry day

                stop_price = entry_price * (1 - STOP_LOSS)
                exit_price = None
                hit_stop = False

                for idx, row in period_data.iterrows():
                    if row["Low"] <= stop_price:
                        exit_price = stop_price
                        hit_stop = True
                        break

                if exit_price is None:
                    exit_price = df.loc[exit_date, "Close"]

                ret = (exit_price - entry_price) / entry_price
                new_capital += allocation * (1 + ret)

                # Record trade
                trades.append({
                    "Entry Date": entry_date,
                    "Exit Date": exit_date,
                    "Stock": stock,
                    "Entry Price": round(entry_price, 4),
                    "Exit Price": round(exit_price, 4),
                    "Allocation": round(allocation, 2),
                    "Return": round(ret, 6),
                    "P&L": round(allocation * ret, 2),
                    "Stop Hit": hit_stop,
                    "Holding Days": (exit_date - entry_date).days
                })

            except Exception:
                continue

        capital = new_capital

        history.append({
            "Date": next_date,
            "Portfolio Value": capital
        })

    portfolio_df = pd.DataFrame(history).set_index("Date")

    # Benchmark performance
    benchmark_prices = data[BENCHMARK]["Close"].resample("ME").last()
    benchmark_curve = (benchmark_prices / benchmark_prices.iloc[0]) * INITIAL_CAPITAL

    return portfolio_df, benchmark_curve, trades

# -----------------------------
# PERFORMANCE METRICS
# -----------------------------
def performance_metrics(portfolio_df):
    returns = portfolio_df["Portfolio Value"].pct_change().dropna()

    total_return = portfolio_df["Portfolio Value"].iloc[-1] / INITIAL_CAPITAL - 1
    years = len(portfolio_df) / 12
    cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    sharpe = (returns.mean() / returns.std()) * np.sqrt(12) if returns.std() != 0 else 0

    drawdown = (portfolio_df["Portfolio Value"] / portfolio_df["Portfolio Value"].cummax()) - 1
    max_dd = drawdown.min()

    print("\n📊 PERFORMANCE")
    print(f"CAGR: {cagr:.2%}")
    print(f"Total Return: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_dd:.2%}")

    return {
        "CAGR": cagr,
        "Total Return": total_return,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd,
        "Final Value": portfolio_df["Portfolio Value"].iloc[-1],
        "Years": years
    }

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    # Ensure results directory exists
    os.makedirs(RESULTS_DIR, exist_ok=True)

    data = load_data()
    print(f"Loaded {len(data)} symbols")

    portfolio_df, benchmark_df, trades = backtest(data)

    print("\nLast few portfolio values:")
    print(portfolio_df.tail())

    # Save outputs to backtest_results/
    portfolio_df.to_csv(os.path.join(RESULTS_DIR, "portfolio_performance.csv"))
    benchmark_df.to_csv(os.path.join(RESULTS_DIR, "benchmark_performance.csv"))

    # Save trades
    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        trades_df.to_csv(os.path.join(RESULTS_DIR, "trades.csv"), index=False)
        print(f"\n✅ Saved {len(trades_df)} trades to {RESULTS_DIR}/trades.csv")
    else:
        print("\n⚠️  No trades were executed")

    # Metrics and summary
    metrics = performance_metrics(portfolio_df)

    summary_df = pd.DataFrame([{
        "Initial Capital": INITIAL_CAPITAL,
        "Final Capital": round(metrics["Final Value"], 2),
        "Total PnL": round(metrics["Final Value"] - INITIAL_CAPITAL, 2),
        "Total Return %": round(metrics["Total Return"] * 100, 2),
        "CAGR": round(metrics["CAGR"] * 100, 2),
        "Sharpe Ratio": round(metrics["Sharpe Ratio"], 2),
        "Max Drawdown": round(metrics["Max Drawdown"] * 100, 2),
        "Years": round(metrics["Years"], 2)
    }])
    summary_df.to_csv(os.path.join(RESULTS_DIR, "summary.csv"), index=False)
    print(f"✅ Results saved to {RESULTS_DIR}/")

    print("\n✅ Backtest completed!")