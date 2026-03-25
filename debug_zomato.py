import yfinance as yf
import pandas as pd

def test_zomato():
    symbol = "ZOMATO.NS"
    print(f"Testing {symbol}...")
    
    # Test 1: Live Price
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="1d")
    lp = None
    if not history.empty:
        lp = round(history['Close'].iloc[-1], 2)
    else:
        lp = round(ticker.fast_info['lastPrice'], 2)
    print(f"Live Price: {lp}")

    # Test 2: Historical Data
    df = yf.download(symbol, period="1y", interval='1d', progress=False)
    print(f"Historical Data Shape: {df.shape}")
    if not df.empty:
        print("Columns:", df.columns)
        # Check for multi-index
        if isinstance(df.columns, pd.MultiIndex):
            print("Multi-index detected")
            new_cols = []
            for c in df.columns: new_cols.append(c[0]) 
            df.columns = new_cols
        print("Final Columns:", df.columns)
        print("First few rows:")
        print(df.head())
    
    if lp is not None and not df.empty:
        print("SUCCESS: Data is available.")
    else:
        print("FAILURE: One or more checks failed.")

if __name__ == "__main__":
    test_zomato()
