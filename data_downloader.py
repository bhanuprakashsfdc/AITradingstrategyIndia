import os
import yfinance as yf
import pandas as pd

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

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
    "HDFCLIFE.NS", "TATACONSUM.NS", "IOC.NS", "M&M.NS", "NIFTYBEES.NS"
]

def download_data_batch(symbols, start="2010-01-01", end="2024-12-31"):
    # Download all symbols in one call (faster)
    print(f"Downloading {len(symbols)} symbols in batch...")
    data = yf.download(
        tickers=symbols,
        start=start,
        end=end,
        group_by='ticker',
        threads=True,
        progress=True
    )
    
    # Save each symbol's data
    for symbol in symbols:
        try:
            if symbol in data.columns.levels[0]:
                df = data[symbol].dropna()
                if not df.empty:
                    file_path = os.path.join(DATA_DIR, f"{symbol}.csv")
                    df.to_csv(file_path)
                    print(f"Saved {symbol}")
                else:
                    print(f"No data for {symbol}")
            else:
                print(f"Symbol not in results: {symbol}")
        except Exception as e:
            print(f"Error saving {symbol}: {e}")

def download_data_individual(symbols, start="2010-01-01", end="2024-12-31"):
    # Fallback: download one by one, skip existing
    for symbol in symbols:
        file_path = os.path.join(DATA_DIR, f"{symbol}.csv")
        if os.path.exists(file_path):
            print(f"✓ {symbol} already exists, skipping")
            continue
        try:
            print(f"Downloading {symbol}...")
            df = yf.download(symbol, start=start, end=end, progress=False)
            if df.empty:
                print(f"  No data for {symbol}")
                continue
            df.to_csv(file_path)
            print(f"  Saved {symbol}")
        except Exception as e:
            print(f"  Error downloading {symbol}: {e}")

if __name__ == "__main__":
    print(f"Total symbols: {len(NIFTY50_SYMBOLS)}")
    
    # Try batch download first (faster)
    try:
        download_data_batch(NIFTY50_SYMBOLS)
    except Exception as e:
        print(f"Batch download failed: {e}")
        print("Falling back to individual downloads...")
        download_data_individual(NIFTY50_SYMBOLS)
    
    print("\n✅ Download complete!")