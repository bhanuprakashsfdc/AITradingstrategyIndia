import os
import yfinance as yf

# Create data folder
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Hardcoded Nifty 50 symbols (Yahoo format)
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
    "HDFCLIFE.NS", "TATACONSUM.NS", "IOC.NS", "M&M.NS","NIFTYBEES.NS"
]

def download_data(symbols, start="2010-01-01", end=None):
    for symbol in symbols:
        try:
            print(f"Downloading {symbol}...")
            df = yf.download(symbol, start=start, end=end)

            if df.empty:
                print(f"No data for {symbol}")
                continue

            file_path = os.path.join(DATA_DIR, f"{symbol}.csv")
            df.to_csv(file_path)

        except Exception as e:
            print(f"Error downloading {symbol}: {e}")

if __name__ == "__main__":
    print(f"Total stocks: {len(NIFTY50_SYMBOLS)}")
    download_data(NIFTY50_SYMBOLS)