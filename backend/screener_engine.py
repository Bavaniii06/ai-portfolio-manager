import yfinance as yf
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
DB_PATH = "backend/screener_db.csv"
TICKER_LIMIT = 500  # Start with Top 500 to prove the engine
PAUSE_BETWEEN_STOCKS = 0.5  # Seconds to wait (prevents rate limiting)

# Top 100 Most Liquid NSE Tickers + Wide ETF Universe
NSE_TICKERS = [
    # --- BLUECHIP STOCKS ---
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LICI.NS", "KOTAKBANK.NS", "LT.NS",
    "AXISBANK.NS", "HCLTECH.NS", "BAJFINANCE.NS", "SUNPHARMA.NS", "MARUTI.NS", "ASIANPAINT.NS",
    "TITAN.NS", "ADANIENT.NS", "ULTRACEMCO.NS", "WIPRO.NS", "NTPC.NS", "M&M.NS",
    "JSWSTEEL.NS", "ONGC.NS", "POWERGRID.NS", "TATASTEEL.NS", "ADANIPORTS.NS", "GRASIM.NS",
    "HDFCLIFE.NS", "SBILIFE.NS", "BAJAJFINSV.NS", "LTIM.NS", "INDUSINDBK.NS",
    "HINDALCO.NS", "TATAMOTORS.NS", "BPCL.NS", "NESTLEIND.NS", "COALINDIA.NS", "BRITANNIA.NS",
    "EICHERMOT.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "DIVISLAB.NS",
    "TATACONSUM.NS", "BAJAJ-AUTO.NS", "TECHM.NS", "HEROMOTOCO.NS", "SBICARD.NS", "TATAPOWER.NS", 
    "VEDL.NS", "ZOMATO.NS", "TRENT.NS", "HAL.NS", "BEL.NS", "RVNL.NS", "IRFC.NS", "GAIL.NS", 
    "IOC.NS", "DLF.NS", "VBL.NS", "CHOLAFIN.NS", "SIEMENS.NS", "ABB.NS", "HAVELLS.NS",
    "PFC.NS", "RECLTD.NS", "BHEL.NS", "JIOFIN.NS", "NYKAA.NS", "PAYTM.NS", "SUZLON.NS",
    
    # --- WIDE MUTUAL FUND (ETF) UNIVERSE ---
    # Nifty 50 / Large Cap
    "NIFTYBEES.NS", "SETFNIF50.NS", "HDFCNIF50.NS", "ICICILIQ.NS", "ICICINIFTY.NS", "KOTAKNIFTY.NS", "UTINIFTETF.NS", "SBIETFNIFTY.NS", "ABSLNN50ET.NS",
    # Nifty Next 50
    "JUNIORBEES.NS", "HDFCNEXT50.NS", "ICICINX50.NS", "MOM30IETFS.NS",
    # Midcap
    "MID150BEES.NS", "MMLOWVOL.NS", "HDFCNIFIT.NS", "ICICIM150.NS", "AXISMIDETF.NS", "KOTAKMID50.NS", "MIRAEAM50.NS",
    # Smallcap
    "SMLCAPBEES.NS", "HDFCSML250.NS", "ICICISMC250.NS", "AXISSMALL.NS", "KOTAKSMALL.NS",
    # Sectoral / Thematic
    "BANKBEES.NS", "ITBEES.NS", "PHARMABEES.NS", "PSUBNKBEES.NS", "CPSEETF.NS", "INFRAEES.NS", "CONSUMBEES.NS",
    "AUTOBEES.NS", "FMCG拓O.NS", "HDFCBANKETF.NS", "ICICIBANKNIFTY.NS", "SBIETFIT.NS", "ICICIPRULI.NS", "KOTAKBKETF.NS",
    # Commodities
    "GOLDBEES.NS", "SILVERBEES.NS", "HDFCGOLD.NS", "ICICIGOLD.NS", "AXISGOLD.NS", "SETFGOLD.NS", "KOTAKGOLD.NS"
]

def calculate_metrics(df):
    """Calculate CAGR, Max Drawdown, and Volatility from historical data."""
    if df.empty or len(df) < 12:  # Need at least 1 year of months
        return None
    
    # CAGR
    start_val = df['Close'].iloc[0]
    end_val = df['Close'].iloc[-1]
    years = len(df) / 12
    cagr = (end_val / start_val) ** (1 / years) - 1
    
    # Max Drawdown
    peaks = df['Close'].cummax()
    drawdowns = (df['Close'] - peaks) / peaks
    max_drawdown = drawdowns.min()
    
    # Volatility
    vol = df['Close'].pct_change().std() * np.sqrt(12)
    
    # Risk Categorization
    if max_drawdown > -0.10: risk = "Low"
    elif max_drawdown > -0.25: risk = "Medium"
    else: risk = "High"
    
    if cagr > 0.40: risk = "Very High" # Speculative growth
    
    return {
        "CAGR": round(cagr * 100, 2),
        "Max_Drawdown": round(max_drawdown * 100, 2),
        "Volatility": round(vol * 100, 2),
        "Risk": risk
    }

def run_screener():
    results = []
    print(f"🚀 Starting NSE Full Market Scan ({len(NSE_TICKERS)} tickers)...")
    
    for i, symbol in enumerate(NSE_TICKERS):
        start_time = time.time()
        print(f"[{i+1}/{len(NSE_TICKERS)}] Analyzing {symbol}...", end="", flush=True)
        
        try:
            # Fetch 5 years of monthly data for steady metrics
            df = yf.download(symbol, period="5y", interval="1mo", progress=False)
            
            if df.empty:
                 print(" ❌ Fixed/Empty Data")
                 continue
                 
            # Handle Multi-Index columns if yfinance is being aggressive
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            
            metrics = calculate_metrics(df)
            if metrics:
                info = yf.Ticker(symbol).info
                results.append({
                    "Symbol": symbol,
                    "Name": info.get('longName', symbol),
                    "Sector": info.get('sector', 'ETF/Commodity'),
                    "CAGR": metrics['CAGR'],
                    "Max_Drawdown": metrics['Max_Drawdown'],
                    "Volatility": metrics['Volatility'],
                    "Risk": metrics['Risk'],
                    "Last_Updated": datetime.now().strftime("%Y-%m-%d")
                })
                print(f" ✅ {metrics['Risk']} Risk, {metrics['CAGR']}% CAGR")
            else:
                print(" ⚠️ Insufficient Data")
                
        except Exception as e:
            print(f" ❌ Error: {str(e)}")
            
        # Rate limit protection
        elapsed = time.time() - start_time
        if elapsed < PAUSE_BETWEEN_STOCKS:
            time.sleep(PAUSE_BETWEEN_STOCKS - elapsed)

    # Save to CSV
    if results:
        df_final = pd.DataFrame(results)
        df_final.to_csv(DB_PATH, index=False)
        print(f"\n✨ SUCCESS: Screener Database created with {len(results)} assets at {DB_PATH}")
    else:
        print("\n❌ FAILED: No data processed.")

if __name__ == "__main__":
    run_screener()
