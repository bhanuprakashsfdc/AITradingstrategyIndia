# AI Trading Strategy

This project downloads historical stock data for Nasdaq-100 symbols and runs a backtest based on a specific trading strategy.

## Files

- `yahoo_data_downloader.py`: Downloads daily OHLCV data for symbols listed in `nasdaq100_symbols - Sheet1.csv` and saves them as CSV files in the `data/` directory.
- `backtest.py`: Loads the downloaded data, computes technical indicators, generates buy/sell signals, and executes a backtest. Results are saved in the `backtest_results/` directory.
- `requirements.txt`: Lists Python dependencies.
- `README.md`: This file.

## Installation

1. Clone or copy this repository to your local machine.
2. Ensure you have Python 3.8+ installed.
3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Download Data

Run the downloader to fetch historical data:

```bash
python yahoo_data_downloader.py
```

This will:
- Read symbols from `nasdaq100_symbols - Sheet1.csv` (you need to provide this file).
- Create a `data/` directory.
- Download daily data for each symbol from `START_DATE` (hardcoded as 2024-01-01) to today.
- Save each symbol's data as `{symbol}.csv` in the `data/` directory.

### Step 2: Run Backtest

After downloading data, run the backtest:

```bash
python backtest.py
```

This will:
- Load all CSV files from the `data/` directory.
- Calculate indicators (SMA50, SMA150, EMA220, 52-week high/low, dip condition).
- Generate signals based on the strategy.
- Execute a backtest with:
  - Initial capital: $100,000
  - Max position size: 10% of capital per trade
  - Stop loss: 15%
- Save results to the `backtest_results/` directory:
  - `trades.csv`: Detailed trade log.
  - `summary.csv`: Performance summary.
- Print performance metrics to the console.

## Configuration

You can adjust the following parameters in the scripts:

### In `yahoo_data_downloader.py`:
- `CSV_FILE`: Path to the symbols CSV file (default: `/Users/bhanu/Desktop/AI Trading/nasdaq100_symbols - Sheet1.csv`)
- `OUTPUT_DIR`: Directory to save downloaded data (default: `data`)
- `START_DATE`: Start date for historical data (default: `2024-01-01`)
- `END_DATE`: End date (default: today)

### In `backtest.py`:
- `DATA_DIR`: Directory containing downloaded data (default: `data`)
- `RESULTS_DIR`: Directory to save backtest results (default: `backtest_results`)
- `INITIAL_CAPITAL`: Starting capital (default: 100000)
- `MAX_POSITION_SIZE`: Max capital per position as fraction (default: 0.10)
- `STOP_LOSS`: Stop loss as fraction (default: 0.15)
- `LOOKBACK_52W`: Lookback period for 52-week high/low in days (default: 252)
- `DIP_LOOKBACK`: Lookback period for dip condition in days (default: 90)

## Pushing to GitHub

To push this code to a GitHub repository:

1. Initialize a git repository (if not already done):
   ```bash
   git init
   ```

2. Add files:
   ```bash
   git add .
   ```

3. Commit:
   ```bash
   git commit -m "Initial commit: AI trading strategy with data downloader and backtest"
   ```

4. Add remote origin (replace with your repo URL):
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   ```

5. Push:
   ```bash
   git push -u origin master
   ```

## Reverting Changes

If you need to revert to a previous state:

- To unstage changes:
  ```bash
  git reset HEAD <file>
  ```

- To discard local changes in a file:
  ```bash
  git checkout -- <file>
  ```

- To revert to a previous commit:
  ```bash
  git reset --hard <commit-hash>
  ```

- To revert the last commit while keeping changes in working directory:
  ```bash
  git reset --soft HEAD~1
  ```

## Notes

- You must provide `nasdaq100_symbols - Sheet1.csv` with a "Symbol" column containing ticker symbols.
- The downloader uses `yfinance` which may be subject to Yahoo Finance's terms of service.
- Backtest results are for educational purposes only and not financial advice.