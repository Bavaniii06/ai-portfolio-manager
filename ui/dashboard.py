import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import os
import random

# ------------------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_icon="📈",
    page_title="Portfolio Pro | AI-Wealth Engine",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# SESSION STATE INITIALIZATION & MULTI-ASSET DUMMY DATA
# ------------------------------------------------------------------------------
DUMMY_PORTFOLIO = [
    {'Symbol': 'RELIANCE.NS', 'Quantity': 50, 'Avg_Price': 2450.0},
    {'Symbol': 'TCS.NS', 'Quantity': 20, 'Avg_Price': 3200.0},
    {'Symbol': 'GOLDBEES.NS', 'Quantity': 300, 'Avg_Price': 55.0},      # GOLD ETF
    {'Symbol': 'SILVERBEES.NS', 'Quantity': 200, 'Avg_Price': 70.0},     # SILVER ETF
    {'Symbol': 'HDFCBANK.NS', 'Quantity': 100, 'Avg_Price': 1500.0}
]

if 'invested_portfolio' not in st.session_state:
    st.session_state.invested_portfolio = pd.DataFrame(DUMMY_PORTFOLIO)

# ------------------------------------------------------------------------------
# PREMIUM PRO SAAS CSS (Restored Sidebar Toggle & Pastel Green)
# ------------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Hide Streamlit Header content but KEEP the container so the sidebar toggle arrow remains visible */
header {background: transparent !important;}
.stDeployButton {display:none;}
.viewerBadge_container__1QSob {display:none !important;}
/* Keep the sidebar expander button visible always */
[data-testid="collapsedControl"] { visibility: visible !important; color: #0f172a;}

/* Global Typography & Backgrounds */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif !important;
    background-color: #f8fafc;
}

/* Make block containers stretch perfectly */
div.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 95% !important;
}

/* Hero Section - Professional Platinum (Light & Positive SaaS Theme) */
.hero {
    background: linear-gradient(135deg, #f8fafc 0%, #f0fdf4 50%, #dcfce7 100%);
    color: #0f172a;
    padding: 2rem 3rem;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.1), 0 4px 6px -2px rgba(16, 185, 129, 0.05);
    border: 1px solid #e2e8f0;
}
.hero h1 { margin: 0; font-size: 2.8rem; font-weight: 800; line-height: 1.1; color: #064e3b; letter-spacing: -0.02em;}
.hero p { margin: 0.4rem 0 0 0; font-size: 1.1rem; color: #334155; font-weight: 500; opacity: 0.9; }
.hero-metric {
    background: #ffffff;
    border: 1px solid #bbf7d0;
    padding: 1.25rem 2.25rem;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

/* Professional Cards & Containers */
.pro-card {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin-bottom: 1rem;
    transition: box-shadow 0.2s ease;
}
.pro-card:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.stock-card {
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    border-left: 5px solid #4ade80; /* Pastel green */
    margin-bottom: 1rem;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
}

.advisor-box {
    background: #f0fdf4;
    border-left: 5px solid #10b981;
    padding: 1.25rem 1.5rem;
    border-radius: 0 12px 12px 0;
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    color: #064e3b;
}

.section-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.5rem;
}

/* Modern Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 15px;
    background-color: transparent;
    border-bottom: 2px solid #e2e8f0;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 0;
    gap: 1px;
    padding: 10px 15px;
    color: #64748b;
    font-weight: 600;
    border: none;
    border-bottom: 3px solid transparent;
}
.stTabs [aria-selected="true"] {
    background-color: transparent !important;
    color: #10b981 !important;
    border-bottom: 3px solid #10b981 !important;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# CORE LOGIC & YFINANCE HELPER FUNCTIONS
# ------------------------------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_live_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        if not history.empty:
            return round(history['Close'].iloc[-1], 2)
        return round(ticker.fast_info['lastPrice'], 2)
    except Exception:
         return None

@st.cache_data(ttl=86400)
def fetch_historical_data(symbol, period, interval='1d'):
    try:
         df = yf.download(symbol, period=period, interval=interval, progress=False)
         if not df.empty:
             df.index = df.index.tz_localize(None)
             if isinstance(df.columns, pd.MultiIndex):
                 new_cols = []
                 for c in df.columns: new_cols.append(c[0]) 
                 df.columns = new_cols
             df = df.dropna(subset=['Close'])
             return df
         return pd.DataFrame()
    except Exception:
         return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_stock_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        fast_info = ticker.fast_info
        
        name = info.get('longName', symbol)
        if "ETF" in name.upper() or "BEES" in symbol.upper():
             sector = "ETF / Commodity"
             industry = "Exchange Traded Fund"
        else:
             sector = info.get('sector', 'Unknown')
             industry = info.get('industry', 'Unknown')
             
        return {
            "name": name,
            "sector": sector,
            "industry": industry,
            "market_cap": fast_info.get('marketCap', 0),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "52_high": fast_info.get('yearHigh', 0),
            "52_low": fast_info.get('yearLow', 0)
        }
    except Exception:
        return {}

def format_inr(val):
    if val >= 10000000: return f"₹{val/10000000:.2f} Cr"
    elif val >= 100000: return f"₹{val/100000:.2f} L"
    return f"₹{val:,.0f}"
    
def resolve_ticker(query):
     q = query.strip().upper()
     # 1. Direct Mapping (Common shortcuts)
     mapping = {
         "GOLD": "GOLDBEES.NS",
         "SILVER": "SILVERBEES.NS",
         "NIFTY": "NIFTYBEES.NS",
         "NIFTY 50": "NIFTYBEES.NS",
         "NIFTY50": "NIFTYBEES.NS",
         "BANKNIFTY": "BANKBEES.NS",
         "IT": "ITBEES.NS",
         "TATA": "TATAMOTORS.NS",
         "RELIANCE": "RELIANCE.NS"
     }
     if q in mapping: return mapping[q]

     # 2. Database Lookup (Smart name matching for "Sun Pharma" etc.)
     db_path = "backend/screener_db.csv"
     if os.path.exists(db_path):
         try:
             df_lookup = pd.read_csv(db_path)
             # Fuzzy search in Name pillar
             match = df_lookup[df_lookup['Name'].str.upper().str.contains(q, na=False)]
             if not match.empty:
                 return match.iloc[0]['Symbol']
         except Exception: pass

     if not q.endswith(".NS") and not q.endswith(".BO"): return q + ".NS"
     return q

import random

# ------------------------------------------------------------------------------
# DYNAMIC RECOMMENDATION ENGINE (Offline DB + Hardcoded Fallback)
# ------------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_recommendations(horizon_str):
    db_path = "backend/screener_db.csv"
    if os.path.exists(db_path):
        try:
            df = pd.read_csv(db_path)
            # Map Horizon string to Risk filters inside the DB
            # We use the hardcoded pool logic for categories but expanded by the DB
            # Filter by horizon logic (Backend engine categorizes by Risk, we still need to map to Horizon)
            # For this version, we will trust the DB's Risk categorization and sample from the full DB
            return df
        except Exception:
            pass
    return None

# Fallback/Seed Universe for immediate use
NSE_RECOMMENDATIONS = {
    "Emergency (0-1Y)": [
        {"name": "Liquid Bees", "symbol": "LIQUIDBEES.NS", "target": 7.0, "risk": "Very Low", "category": "Debt"},
        {"name": "HDFC Liquid ETF", "symbol": "LIQUID.NS", "target": 6.8, "risk": "Very Low", "category": "Debt"},
        {"name": "Nippon India ETF Gilt", "symbol": "GILTBEES.NS", "target": 7.5, "risk": "Low", "category": "Govt Bonds"},
        {"name": "ICICI Pru Liquid ETF", "symbol": "ICICILIQ.NS", "target": 7.1, "risk": "Very Low", "category": "Debt"},
        {"name": "Gold ETF", "symbol": "GOLDBEES.NS", "target": 9.0, "risk": "Low", "category": "Commodity"},
        {"name": "SBI ETF Gold", "symbol": "SETFGOLD.NS", "target": 8.9, "risk": "Low", "category": "Commodity"}
    ],
    "Short Term (1-3Y)": [
        {"name": "Nifty 50 ETF", "symbol": "NIFTYBEES.NS", "target": 12.0, "risk": "Medium", "category": "Equity Index"},
        {"name": "Gold ETF", "symbol": "GOLDBEES.NS", "target": 9.0, "risk": "Low", "category": "Commodity"},
        {"name": "Silver ETF", "symbol": "SILVERBEES.NS", "target": 11.0, "risk": "Medium", "category": "Commodity"},
        {"name": "HDFC Bank", "symbol": "HDFCBANK.NS", "target": 12.5, "risk": "Low", "category": "Banking"},
        {"name": "TCS", "symbol": "TCS.NS", "target": 11.5, "risk": "Low", "category": "IT"},
        {"name": "ITC", "symbol": "ITC.NS", "target": 10.2, "risk": "Low", "category": "FMCG"},
        {"name": "HUL", "symbol": "HINDUNILVR.NS", "target": 10.5, "risk": "Low", "category": "FMCG"},
        {"name": "Nestle India", "symbol": "NESTLEIND.NS", "target": 11.0, "risk": "Low", "category": "FMCG"},
        {"name": "Kotak Bank", "symbol": "KOTAKBANK.NS", "target": 12.0, "risk": "Low", "category": "Banking"},
        {"name": "ICICI Bank", "symbol": "ICICIBANK.NS", "target": 13.5, "risk": "Low", "category": "Banking"},
        {"name": "Infosys", "symbol": "INFY.NS", "target": 11.8, "risk": "Low", "category": "IT"}
    ],
    "Medium (3-5Y)": [
        {"name": "Reliance", "symbol": "RELIANCE.NS", "target": 15.0, "risk": "Medium", "category": "Energy"},
        {"name": "Larsen & Toubro", "symbol": "LT.NS", "target": 18.5, "risk": "Medium", "category": "Infra"},
        {"name": "Bajaj Finance", "symbol": "BAJFINANCE.NS", "target": 22.0, "risk": "Medium", "category": "Financials"},
        {"name": "Maruti Suzuki", "symbol": "MARUTI.NS", "target": 16.0, "risk": "Medium", "category": "Auto"},
        {"name": "Mahindra & Mahindra", "symbol": "M&M.NS", "target": 17.5, "risk": "Medium", "category": "Auto"},
        {"name": "Titan", "symbol": "TITAN.NS", "target": 19.0, "risk": "Medium", "category": "Consumer"},
        {"name": "Midcap 150 ETF", "symbol": "MID150BEES.NS", "target": 16.5, "risk": "Medium", "category": "Equity Index"},
        {"name": "Sun Pharma", "symbol": "SUNPHARMA.NS", "target": 14.5, "risk": "Medium", "category": "Pharma"},
        {"name": "Tata Motors", "symbol": "TATAMOTORS.NS", "target": 20.0, "risk": "Medium", "category": "Auto"},
        {"name": "Bank Nifty ETF", "symbol": "BANKBEES.NS", "target": 15.5, "risk": "Medium", "category": "Equity Index"},
        {"name": "State Bank of India", "symbol": "SBIN.NS", "target": 14.0, "risk": "Medium", "category": "Banking"},
        {"name": "Bharti Airtel", "symbol": "BHARTIARTL.NS", "target": 16.8, "risk": "Medium", "category": "Telecom"},
        {"name": "NTPC", "symbol": "NTPC.NS", "target": 14.2, "risk": "Medium", "category": "Energy Utilities"}
    ],
    "Long Term (5+Y)": [
        {"name": "Nifty IT ETF", "symbol": "ITBEES.NS", "target": 16.0, "risk": "High", "category": "Equity Index"},
        {"name": "Zomato", "symbol": "ZOMATO.NS", "target": 35.0, "risk": "High", "category": "Tech"},
        {"name": "Jio Financial", "symbol": "JIOFIN.NS", "target": 28.0, "risk": "High", "category": "Financials"},
        {"name": "Trent", "symbol": "TRENT.NS", "target": 32.0, "risk": "High", "category": "Retail"},
        {"name": "RVNL", "symbol": "RVNL.NS", "target": 38.0, "risk": "High", "category": "Infra"},
        {"name": "IRFC", "symbol": "IRFC.NS", "target": 30.0, "risk": "High", "category": "Infra"},
        {"name": "Suzlon", "symbol": "SUZLON.NS", "target": 45.0, "risk": "Very High", "category": "Energy"},
        {"name": "HAL", "symbol": "HAL.NS", "target": 35.0, "risk": "High", "category": "Defense"},
        {"name": "Adani Power", "symbol": "ADANIPOWER.NS", "target": 40.0, "risk": "Very High", "category": "Energy"},
        {"name": "Tata Power", "symbol": "TATAPOWER.NS", "target": 28.0, "risk": "High", "category": "Energy Utilities"},
        {"name": "Dixon Tech", "symbol": "DIXON.NS", "target": 42.0, "risk": "High", "category": "Electronics"},
        {"name": "Smallcap 250 ETF", "symbol": "SML250BEES.NS", "target": 22.0, "risk": "High", "category": "Equity Index"},
        {"name": "Olectra Greentech", "symbol": "OLECTRA.NS", "target": 48.0, "risk": "Very High", "category": "EV Tech"}
    ]
}

# ------------------------------------------------------------------------------
# SIDEBAR: USER INPUTS
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135673.png", width=60)
    st.markdown("<h2 style='color:#0f172a; margin-bottom: 0;'>Financial Profile</h2>", unsafe_allow_html=True)
    st.markdown("Configure your inputs below to adjust the AI Recommendations.")
    
    age = st.slider("👤 Age", 18, 70, 28)
    gross_salary = st.number_input("💰 Gross Income /mo (₹)", 15000, 1000000, 50000, step=5000)
    risk_profile = st.selectbox("⚠️ Risk Appetite", ["Conservative", "Balanced", "Growth"], index=1)
    horizon = st.selectbox(
        "⏳ Investment Horizon", 
        ["Emergency (0-1Y)", "Short Term (1-3Y)", "Medium (3-5Y)", "Long Term (5+Y)"],
        index=3
    )
    st.markdown("---")
    st.info("🟢 Real-Time Linked")

# ------------------------------------------------------------------------------
# MATH PIPELINE
# ------------------------------------------------------------------------------
net_salary = gross_salary * 0.85
savings = net_salary * 0.30
risk_allocation = {"Conservative": 0.40, "Balanced": 0.60, "Growth": 0.80}
investment_amount = savings * risk_allocation[risk_profile]

# ------------------------------------------------------------------------------
# CONTINUOUS RISK ENGINE (Weighted Scoring)
# ------------------------------------------------------------------------------
def get_suggested_risk(u_age, u_horizon, u_appetite):
    # Mapping inputs to scores
    app_score = {"Conservative": 25, "Balanced": 55, "Growth": 85}[u_appetite]
    
    # Age Score (18-70): Young (+20) to Old (-20)
    age_score = 20 - (u_age - 18) * (40/52)
    
    # Horizon Score: Emergency (-30) to Long (+30)
    h_map = {"Emergency (0-1Y)": -35, "Short Term (1-3Y)": -15, "Medium (3-5Y)": 10, "Long Term (5+Y)": 30}
    h_score = h_map.get(u_horizon, 0)
    
    total = app_score + age_score + h_score
    if total < 40: return "Conservative"
    if total < 75: return "Balanced"
    return "Growth"

# Sidebar Horizon implies a set of numeric years for Sim
horizon_to_yrs = {"Emergency (0-1Y)": 1, "Short Term (1-3Y)": 2, "Medium (3-5Y)": 5, "Long Term (5+Y)": 10}

# Calculate Global Suggestion
global_suggested_risk = get_suggested_risk(age, horizon, risk_profile)

# Map Risk Category to Asset Risk levels in DB
risk_to_levels = {
    "Conservative": ["Very Low", "Low"],
    "Balanced": ["Low", "Medium"],
    "Growth": ["Medium", "High", "Very High"]
}
allowed_risks = risk_to_levels[global_suggested_risk]

# Override: If Horizon is Emergency, force Very Low regardless of calc
if horizon == "Emergency (0-1Y)":
    allowed_risks = ["Very Low", "Low"]
elif horizon == "Short Term (1-3Y)":
    allowed_risks = ["Low", "Medium"]
# Attempt to load from Offline Database first (Reactive)
db_results = load_recommendations(horizon)

if db_results is not None and not db_results.empty:
    # Phase 32: Purge ETFs/Mutual Funds from Market Picks (Stocks ONLY)
    stock_only_df = db_results[
        (~db_results['Sector'].str.contains("ETF|Commodity", case=False, na=False)) &
        (~db_results['Name'].str.contains("ETF|BeES|Nifty|Sensex", case=False, na=False))
    ]
    
    # Filter by Risk
    filtered_df = stock_only_df[stock_only_df['Risk'].isin(allowed_risks)]
    
    if not filtered_df.empty:
        # Phase 24: Profile-Anchoring
        # Phase 24: Profile-Anchoring for visual distinction
        # Force diversity: at least 2 from the "defining" risk tier for the profile
        if global_suggested_risk == "Balanced": # Anchor to Low
            defining = filtered_df[filtered_df['Risk'] == "Low"].sort_values(by='CAGR', ascending=False).head(2)
            others = filtered_df[~filtered_df['Symbol'].isin(defining['Symbol'])].sort_values(by='CAGR', ascending=False).head(2)
            sorted_tier_df = pd.concat([defining, others])
        elif global_suggested_risk == "Growth": # Anchor to High/Very High
            defining = filtered_df[filtered_df['Risk'].isin(["High", "Very High"])].sort_values(by='CAGR', ascending=False).head(2)
            others = filtered_df[~filtered_df['Symbol'].isin(defining['Symbol'])].sort_values(by='CAGR', ascending=False).head(2)
            sorted_tier_df = pd.concat([defining, others])
        else:
            sorted_tier_df = filtered_df.sort_values(by='CAGR', ascending=False).head(4)

        sample = sorted_tier_df.to_dict('records')
        
        recommended_stocks = []
        for i, s in enumerate(sample):
            action = '🔵 ACCUMULATE'
            if i == 0: action = '✨ AI TOP PICK'
            
            recommended_stocks.append({
                "name": s['Name'], 
                "symbol": s['Symbol'], 
                "target": s['CAGR'], 
                "risk": s['Risk'], 
                "category": s['Sector'],
                "Action": action
            })
    else:
        # Fallback to hardcoded
        filtered_universe = [s for s in NSE_RECOMMENDATIONS[horizon] if s["risk"] in allowed_risks]
        if len(filtered_universe) < 3: filtered_universe = NSE_RECOMMENDATIONS[horizon]
        sorted_fallback = sorted(filtered_universe, key=lambda x: x['target'], reverse=True)
        recommended_stocks = sorted_fallback[:4]
        for i, s in enumerate(recommended_stocks):
            s['Action'] = '✨ AI TOP PICK' if i == 0 else '🔵 ACCUMULATE'
else:
    # Use Hardcoded Universe (Phase 6 logic) with Sorting
    filtered_universe = [s for s in NSE_RECOMMENDATIONS[horizon] if s["risk"] in allowed_risks]
    if len(filtered_universe) < 3: filtered_universe = NSE_RECOMMENDATIONS[horizon]
    sorted_fallback = sorted(filtered_universe, key=lambda x: x['target'], reverse=True)
    recommended_stocks = sorted_fallback[:4]
    for i, s in enumerate(recommended_stocks):
        s['Action'] = '✨ AI TOP PICK' if i == 0 else '🔵 ACCUMULATE'

df_reco = pd.DataFrame(recommended_stocks)
if not df_reco.empty:
    df_reco['Allocation'] = investment_amount / len(df_reco)
    
    # Standardize column naming for live price lookup
    if 'symbol' not in df_reco.columns and 'Symbol' in df_reco.columns:
        df_reco['symbol'] = df_reco['Symbol']

    live_targets = []
    for sym in df_reco['symbol']:
        live_targets.append(fetch_live_price(sym) or 1.0)
    df_reco['live_price'] = live_targets

    df_reco['Quantity'] = (df_reco['Allocation'] / df_reco['live_price']).apply(lambda x: max(1, np.floor(x))).astype(int)
    df_reco['Total_Value'] = df_reco['Quantity'] * df_reco['live_price']
    
    if 'Action' not in df_reco.columns:
        df_reco['Action'] = ['🟢 STRONG BUY' if i == 0 else '🔵 ACCUMULATE' for i in range(len(df_reco))]
else:
    # Create empty DF with expected columns to avoid downstream errors
    df_reco = pd.DataFrame(columns=['name', 'symbol', 'Total_Value', 'Quantity', 'live_price', 'Action', 'category', 'risk', 'target'])

# ------------------------------------------------------------------------------
# MAIN APP PORTION - HERO
# ------------------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <div>
        <h1>Portfolio Pro</h1>
        <p>Market Intelligence • AI Advisory • Multi-Asset Tracking</p>
    </div>
    <div class="hero-metric">
        <div style='font-size: 2.2rem; font-weight: 800; line-height: 1; color: #064e3b;'>₹{:,}</div>
        <div style='font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; color: #64748b; font-weight: 700;'>Monthly Budget</div>
    </div>
</div>
""".format(int(investment_amount)), unsafe_allow_html=True)


# TABS STRUCTURE
tab1, tab2, tab3, tab4 = st.tabs([
    "💼 My Portfolio", 
    "🎯 Market Picks",
    "📈 Stock Scanner", 
    "🤖 SIP Planner"
])

# ==============================================================================
# TAB 1: INTERACTIVE INVESTED PORTFOLIO
# ==============================================================================
with tab1:
    st.markdown('<div class="section-header">Portfolio Overview</div>', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([1.5, 1])
    
    with col_t1:
        st.markdown('<div class="section-header">Live Multi-Asset Portfolio Tracker</div>', unsafe_allow_html=True)
        
        with st.expander("➕ Log New Transaction (Equities, Gold, Silver)", expanded=False):
            with st.form("add_stock_form"):
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1: new_symbol = st.text_input("Asset Ticker", placeholder="e.g., RELIANCE or GOLDBEES").upper()
                with col_f2: new_qty = st.number_input("Quantity", min_value=1, step=1, value=10)
                with col_f3: new_avg = st.number_input("Avg Price (₹)", min_value=1.0, value=100.0, step=10.0)
                
                if st.form_submit_button("Log Transaction", type="primary") and new_symbol:
                     sym = resolve_ticker(new_symbol)
                     if fetch_live_price(sym) is not None:
                         nr = pd.DataFrame([{'Symbol': sym, 'Quantity': int(new_qty), 'Avg_Price': float(new_avg)}])
                         st.session_state.invested_portfolio = pd.concat([st.session_state.invested_portfolio, nr], ignore_index=True)
                         st.success(f"Transaction Logged: {sym}")
                         st.rerun()
                     else:
                         st.error("Invalid ticker or data unavailable.")

        df_port = st.session_state.invested_portfolio.copy()
        if not df_port.empty:
            df_port['CMP (₹)'] = [fetch_live_price(s) or 0 for s in df_port['Symbol']]
            df_port['Invested Value'] = df_port['Quantity'] * df_port['Avg_Price']
            df_port['Current Value'] = df_port['Quantity'] * df_port['CMP (₹)']
            df_port['P&L (₹)'] = df_port['Current Value'] - df_port['Invested Value']
            df_port['P&L (%)'] = (df_port['P&L (₹)'] / df_port['Invested Value']) * 100
            
            # AI Signal Logic for Existing Portfolio
            signals = []
            for _, row in df_port.iterrows():
                pl_pct = row['P&L (%)']
                if pl_pct < -5.0: signals.append("🟢 BUY/AVRG") # Buying opportunity
                elif pl_pct > 20.0: signals.append("💎 SELL/PROFIT") # Profit booking
                else: signals.append("⚡ HOLD")
            df_port['AI Signal'] = signals

            tot_inv = df_port['Invested Value'].sum()
            tot_cur = df_port['Current Value'].sum()
            tot_pl = tot_cur - tot_inv
            pl_pct = (tot_pl / tot_inv * 100) if tot_inv > 0 else 0
            
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown(f'<div class="pro-card"> <div style="color:#64748b; font-size:0.85rem; font-weight:600; text-transform:uppercase;">Principal</div> <div style="font-size:1.8rem; font-weight:800; color:#0f172a;">{format_inr(tot_inv)}</div> </div>', unsafe_allow_html=True)
            with sc2:
                st.markdown(f'<div class="pro-card"> <div style="color:#64748b; font-size:0.85rem; font-weight:600; text-transform:uppercase;">Net Worth</div> <div style="font-size:1.8rem; font-weight:800; color:#10b981;">{format_inr(tot_cur)}</div> </div>', unsafe_allow_html=True)
            with sc3:
                c = "#10b981" if tot_pl >= 0 else "#ef4444"
                st.markdown(f'<div class="pro-card" style="border-right:4px solid {c}"> <div style="color:#64748b; font-size:0.85rem; font-weight:600; text-transform:uppercase;">Unrealized P&L</div> <div style="font-size:1.8rem; font-weight:800; color:{c};">{format_inr(tot_pl)} ({pl_pct:.2f}%)</div> </div>', unsafe_allow_html=True)
            
            st.dataframe(
                df_port.style.format({
                    'Avg_Price': '₹{:.2f}', 'CMP (₹)': '₹{:.2f}', 'Invested Value': '₹{:.0f}',
                    'Current Value': '₹{:.0f}', 'P&L (₹)': '₹{:.0f}', 'P&L (%)': '{:.2f}%'
                }).map(lambda v: f"color: {'#10b981' if v>0 else '#ef4444' if v<0 else 'grey'}; font-weight:700;", subset=['P&L (₹)', 'P&L (%)'])
                  .map(lambda v: f"background-color: {'#dcfce7' if 'BUY' in v else '#fef9c3' if 'HOLD' in v else '#fee2e2'}; border-radius: 4px; padding: 2px;", subset=['AI Signal']),
                use_container_width=True, hide_index=True
            )
            if st.button("🗑️ Reset Testing Portfolio"):
                st.session_state.invested_portfolio = pd.DataFrame(columns=['Symbol', 'Quantity', 'Avg_Price'])
                st.rerun()
            
    with col_t2:
        st.markdown('<div class="section-header">Asset Distribution</div>', unsafe_allow_html=True)
        if not df_port.empty:
            fig_pie = px.pie(df_port, values='Current Value', names='Symbol', hole=0.5,
                             color_discrete_sequence=['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#0f172a'])
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=True)
            fig_pie.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig_pie, use_container_width=True)

# ==============================================================================
# TAB 2: AI STOCK RECOMMENDATIONS (Restored & Improved)
# ==============================================================================
with tab2:
     st.markdown('<div class="section-header">Top Stock Recommendations</div>', unsafe_allow_html=True)
     st.markdown(f"AI suggested monthly allocation of **₹{investment_amount:,.0f}** for your **{horizon}** profile.")
     
     col_rec1, col_rec2 = st.columns([1, 1])
     
     with col_rec1:
         for i, row in df_reco.iterrows():
             reasoning = "Strong fundamentals and institutional backing." 
             if row['risk'] == "High": reasoning = f"High structural momentum in {row['category']} sector."
             elif row['risk'] == "Low": reasoning = "Bluechip stability, lower drawdowns in volatile markets."
                  
             action_color = "#10b981" if "TOP" in row['Action'] else "#34d399" 
             
             st.markdown(f"""
             <div class="stock-card" style="border-left-color: {action_color}; padding: 1.5rem; {'border: 2px solid #10b981;' if 'TOP' in row['Action'] else ''}">
                 <div style='display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;'>
                     <div style="flex: 1; min-width: 150px;">
                         <h3 style='margin: 0; color: #0f172a; font-size: 1.4rem;'>{row['name']}</h3>
                         <p style='margin: 0.2rem 0; color: #64748b; font-weight: 600; font-size: 0.9rem;'>{row['category']} • {row['risk']} Risk</p>
                     </div>
                     <div style='text-align: right; flex: 1; min-width: 150px;'>
                         <div style='font-size: 1.6rem; font-weight: 800; color: #0f172a;'>₹{int(row['Total_Value']):,}</div>
                         <div style='font-size: 1rem; color: #64748b;'>{int(row['Quantity'])} shares @ CMP ₹{row['live_price']}</div>
                         <div style='margin-top: 0.5rem; display: inline-block; padding: 0.3rem 0.6rem; background: {action_color}20; color: #064e3b; border-radius: 6px; font-weight: 700; font-size: 0.85rem;'>
                             {row['Action']}
                         </div>
                     </div>
                 </div>
                 <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; color: #475569; font-size: 0.9rem;'>
                     <strong>🤖 AI Logic:</strong> {reasoning}
                 </div>
             </div>
             """, unsafe_allow_html=True)
             
     with col_rec2:
         st.markdown("##### 🎯 Recommendation Universe Risk-Reward")
         fig_scatter = px.scatter(df_reco, x='risk', y='target', size='Total_Value', color='category',
                                 hover_name='name', size_max=60, height=400,
                                 color_discrete_sequence=['#10b981', '#0f172a', '#34d399', '#64748b', '#86efac'])
         fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff", font_color="#475569", xaxis_title="Risk Level", yaxis_title="Target Yield CAGR (%)", xaxis={'categoryorder':'array', 'categoryarray':['Very Low', 'Low', 'Medium', 'High']}, margin=dict(t=20, b=20, l=20, r=20))
         fig_scatter.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
         fig_scatter.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
         st.plotly_chart(fig_scatter, use_container_width=True)


# ==============================================================================
# TAB 3: PRO MARKET SCANNER (Candlesticks + Volume)
# ==============================================================================
with tab3:
    st.markdown('<div class="section-header">Stock Scanner</div>', unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
    with col_s1: 
        raw_sym = st.text_input("Analyze Asset", placeholder="e.g., RELIANCE or GOLDBEES", value="nifty").upper()
    with col_s2: 
        period = st.selectbox("Interval Span", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    with col_s3:
        chart_type = st.radio("Chart Type", ["Candle", "Line"], horizontal=True)
        
    calc_sym = resolve_ticker(raw_sym)
    
    with st.spinner(f"Loading Terminal Data for {calc_sym}..."):
        df_hist = fetch_historical_data(calc_sym, period, interval='1d')
        info = fetch_stock_info(calc_sym)
        lp = fetch_live_price(calc_sym)

    if not df_hist.empty and lp is not None:
        c_i1, c_i2, c_i3, c_i4 = st.columns(4)
        c_i1.metric("Live CMP", f"₹{lp:,.2f}")
        c_i2.metric("Sector", info.get("sector", "N/A"))
        c_i3.metric("52W High", f"₹{info.get('52_high', 0):,.2f}")
        c_i4.metric("52W Low", f"₹{info.get('52_low', 0):,.2f}")
        
        # PRO CHARTING
        df_hist['SMA_20'] = df_hist['Close'].rolling(window=20).mean()
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.75, 0.25])
        
        if chart_type == "Candle":
             fig.add_trace(go.Candlestick(x=df_hist.index, open=df_hist['Open'], high=df_hist['High'], low=df_hist['Low'], close=df_hist['Close'],
                                          increasing_line_color='#10b981', decreasing_line_color='#ef4444', name="Price"), row=1, col=1)
        else:
             fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist['Close'], mode='lines', line=dict(color='#0f172a', width=2), name="Price"), row=1, col=1)
             
        fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist['SMA_20'], mode='lines', line=dict(color='#f59e0b', width=1.5, dash='dot'), name="20 SMA"), row=1, col=1)
        
        if 'Volume' in df_hist.columns:
            colors = ['#10b981' if row['Close'] >= row['Open'] else '#ef4444' for i, row in df_hist.iterrows()]
            fig.add_trace(go.Bar(x=df_hist.index, y=df_hist['Volume'], marker_color=colors, name="Volume", opacity=0.7), row=2, col=1)
            
        fig.update_layout(
             height=600, margin=dict(t=20, b=20, r=20, l=20),
             paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff",
             xaxis_rangeslider_visible=False, showlegend=False, hovermode="x unified"
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', row=1, col=1)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', row=1, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Data unavailable for {calc_sym}.")

with tab4:
    st.markdown('<div class="section-header">Elite Multi-Asset SIP Planner</div>', unsafe_allow_html=True)
    
    with st.expander("💡 Understanding SIP: Mutual Funds vs ETFs", expanded=False):
        st.write("""
        **Mutual Funds vs ETFs**
        An ETF (Exchange Traded Fund) is simply a **Mutual Fund that trades on the stock exchange**. 
        - **Same Underlying Assets:** Both hold the same stocks (e.g. Nifty 50).
        - **Real-Time Simulation:** We use ETFs here because they allow for real-time price tracking and more accurate SIP simulations.
        - **Cost Effective:** Usually have lower expense ratios than traditional funds.
        
        This planner treats them as **Mutual Fund (ETF)** assets to give you the most professional and transparent investment experience.
        """)
    
    st.info(f"💡 Based on your age, the optimal equity exposure for your SIP is **{100-age}%**.")
    
    # 1. Main Inputs
    s_col1, s_col2 = st.columns([1,1])
    with s_col2:
        s_amt_final = st.number_input("Monthly Contribution (₹)", min_value=1000, value=10000, step=1000)
        s_yrs_final = st.slider("Horizon (Years)", 1, 25, value=5 if horizon == "Long Term (5+Y)" else horizon_to_yrs[horizon])
        
    with s_col1:
        sim_horizon = "Long Term (5+Y)"
        if s_yrs_final <= 1: sim_horizon = "Emergency (0-1Y)"
        elif s_yrs_final <= 3: sim_horizon = "Short Term (1-3Y)"
        elif s_yrs_final <= 5: sim_horizon = "Medium (3-5Y)"
        
        suggested_risk_cat = get_suggested_risk(age, sim_horizon, risk_profile)
        
        if 'sip_shuffle_seed' not in st.session_state:
             st.session_state.sip_shuffle_seed = 0
             
        # Phase 31: Dynamic Reactivity & Elite Naming
        # Move risk-profile calculation INSIDE the tab logic for slider reactivity
        local_risk_tier = get_suggested_risk(age, sim_horizon, risk_profile)
        local_allowed_risks = risk_to_levels[local_risk_tier]
        
        # Override if horizon is very short
        if s_yrs_final <= 1: local_allowed_risks = ["Very Low", "Low"]
        elif s_yrs_final <= 3: local_allowed_risks = ["Low", "Medium"]

        asset_count = len(db_results) if db_results is not None else 0
        st.caption(f"🧠 AI Brain actively monitoring {asset_count}+ assets | Risk Tier: {local_risk_tier}")

        # Phase 33: Reactive Seed for Intelligent Sampling
        reactive_seed = int(age) + int(s_amt_final) + int(s_yrs_final) + st.session_state.sip_shuffle_seed

        # Elite Name Cleaner Utility (Restored to Perfect State)
        def clean_elite_name(raw_name):
            clean = raw_name.replace(".NS", "").replace(".BO", "")
            # Only strip the most technical noise, keep descriptive branding for card-feel
            replacements = [" ETF", "ETF", " Mutual Fund", "Mutual Fund", " MUTUAL FUND"]
            for r in replacements:
                clean = clean.replace(r, "")
            # Cleanup common technical names for commodities
            if "GOLD" in clean.upper(): clean = "Gold"
            if "SILVER" in clean.upper(): clean = "Silver"
            return clean.strip()

        themed_grid = {"Stability": [], "Growth": [], "Elite Alpha": [], "Commodities & Defense": []}
        
        if db_results is not None and not db_results.empty:
            # Phase 33: Intelligent Reactive Sampling
            # Use reactive_seed to ensure diversity across slider changes
            import random
            rng = random.Random(reactive_seed)

            # 1. Stability (Large Cap) - Restored Variety
            l_cap_pool = db_results[
                ((db_results['Sector'].str.contains("ETF|Commodity", case=False, na=False)) |
                 (db_results['Name'].str.contains("ETF|BeES|Nifty|Sensex", case=False, na=False))) &
                (db_results['Name'].str.contains("50|Sensex|Bluechip", case=False, na=False)) &
                (db_results['Risk'].isin(local_allowed_risks))
            ].sort_values(by='CAGR', ascending=False)
            
            if not l_cap_pool.empty:
                candidates = l_cap_pool.head(6).index.tolist()
                chosen = rng.sample(candidates, min(len(candidates), 3))
                for idx in chosen:
                    r = l_cap_pool.loc[idx]
                    themed_grid["Stability"].append({"name": r['Name'], "raw": r['Name']})

            # 2. Growth (Mid/Small)
            g_mf_pool = db_results[
                ((db_results['Sector'].str.contains("ETF|Commodity", case=False, na=False)) |
                 (db_results['Name'].str.contains("ETF|BeES|Nifty|Sensex", case=False, na=False))) &
                (db_results['Name'].str.contains("Midcap|Smallcap|Next 50", case=False, na=False)) &
                (db_results['Risk'].isin(local_allowed_risks))
            ].sort_values(by='CAGR', ascending=False)

            if not g_mf_pool.empty:
                candidates = g_mf_pool.head(6).index.tolist()
                chosen = rng.sample(candidates, min(len(candidates), 3))
                for idx in chosen:
                    r = g_mf_pool.loc[idx]
                    themed_grid["Growth"].append({"name": r['Name'], "raw": r['Name']})

            # 3. Elite Alpha (Stocks)
            stock_pool = db_results[
                (~db_results['Sector'].str.contains("ETF|Commodity", case=False, na=False)) &
                (~db_results['Name'].str.contains("ETF|BeES|Nifty|Sensex", case=False, na=False)) &
                (db_results['Risk'].isin(local_allowed_risks))
            ].sort_values(by='CAGR', ascending=False)

            if not stock_pool.empty:
                candidates = stock_pool.head(10).index.tolist()
                chosen = rng.sample(candidates, min(len(candidates), 3))
                for idx in chosen:
                    r = stock_pool.loc[idx]
                    themed_grid["Elite Alpha"].append({"name": r['Name'], "raw": r['Name']})

            # 4. Commodities & Defense (Gold/Silver)
            comm_pool = db_results[
                (db_results['Name'].str.contains("GOLD|SILVER|SNETFGOLD|SILVERBEES", case=False, na=False))
            ].sort_values(by='CAGR', ascending=False)

            if not comm_pool.empty:
                candidates = comm_pool.head(5).index.tolist()
                chosen = rng.sample(candidates, min(len(candidates), 3))
                for idx in chosen:
                    r = comm_pool.loc[idx]
                    themed_grid["Commodities & Defense"].append({"name": r['Name'], "raw": r['Name']})

        # Fallback
        if not themed_grid["Stability"]:
            themed_grid["Stability"] = [{"name": "SBI Nifty 50", "raw": "SBI Nifty 50 ETF"}]
        if not themed_grid["Commodities & Defense"]:
            themed_grid["Commodities & Defense"] = [{"name": "Gold", "raw": "GOLDBEES.NS"}, {"name": "Silver", "raw": "SILVERBEES.NS"}]

        # UI Header with Shuffle (Matched to Screenshot)
        h_col1, h_col2 = st.columns([1.5, 1])
        with h_col1:
            st.markdown("### 🌌 Multi-Asset Discovery Hub")
        with h_col2:
            st.markdown('<div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px; text-align: center; background: white;">', unsafe_allow_html=True)
            if st.button("🔄 Shuffle Portfolio", key="sip_shuf_btn", use_container_width=True):
                st.session_state.sip_shuffle_seed += 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        for theme, assets in themed_grid.items():
            if assets and theme != "Commodities & Defense": # Row by row as per screenshot
                st.markdown(f"**{theme}**")
                cols = st.columns(3) 
                for i, asset in enumerate(assets):
                    if i < len(cols):
                        clean_name = clean_elite_name(asset['name'])
                        # Fixed height for card-feel if possible or just bold multi-line
                        if cols[i].button(f"**{clean_name}**", use_container_width=True, key=f"hub_{theme}_{asset['name']}"):
                            st.session_state.sip_search_key = asset['raw']
                            st.rerun()

        # Separated Commodities at the end for clean layout 
        if themed_grid["Commodities & Defense"]:
            st.markdown("**Commodities & Defense**")
            c_cols = st.columns(3)
            for i, asset in enumerate(themed_grid["Commodities & Defense"]):
                if i < 3:
                    clean_name = clean_elite_name(asset['name'])
                    if c_cols[i].button(f"**{clean_name}**", use_container_width=True, key=f"hub_comm_{asset['name']}"):
                        st.session_state.sip_search_key = asset['raw']
                        st.rerun()

        discover_mode = st.radio("Asset Discovery Mode", ["AI Suggestions", "Search All / Custom"], horizontal=True, label_visibility="collapsed")
        
        if discover_mode == "AI Suggestions":
            if 'sip_search_key' not in st.session_state:
                 st.session_state.sip_search_key = themed_grid["Stability"][0]['raw']

            all_options = sorted(db_results['Name'].unique().tolist()) if db_results is not None else ["Nifty 50 ETF"]
            # Phase 35: Professional selectbox mapping (Clean Label -> Raw Symbol)
            clean_to_raw = {clean_elite_name(opt): opt for opt in all_options}
            clean_options = list(clean_to_raw.keys())
            
            try:
                 # Search for the CURRENT key in clean names
                 current_raw = st.session_state.sip_search_key
                 current_clean = clean_elite_name(current_raw)
                 def_idx = clean_options.index(current_clean) if current_clean in clean_options else 0
            except:
                 def_idx = 0

            s_asset_clean = st.selectbox("🎯 Selected Target Asset", options=clean_options, index=def_idx)
            s_asset = clean_to_raw.get(s_asset_clean, s_asset_clean)
            s_sym = resolve_ticker(s_asset)
        else:
            st.markdown("#### 🔍 Full Market Search")
            st.info("💡 Enter any NSE Ticker to unlock 2000+ assets instantly.")
            c_col1, c_col2 = st.columns([3, 1])
            custom_sym = c_col1.text_input("📝 Enter Ticker Symbol", value="RELIANCE.NS").upper()
            if not custom_sym.endswith(".NS") and "." not in custom_sym: custom_sym += ".NS"
            s_sym = custom_sym
            s_asset = custom_sym 
            if c_col2.button("🚀 Fetch Data", use_container_width=True):
                 st.session_state.sip_search_key = custom_sym
                 st.rerun()

    st.markdown("---")

    # 2. Results (Hardened)
    if s_sym:
         monthly_hist = fetch_historical_data(s_sym, period="max", interval='1mo') 
         
         if not monthly_hist.empty and len(monthly_hist) > 1:
             max_months = len(monthly_hist)
             req_months = s_yrs_final * 12
             
             if req_months > max_months:
                 st.info(f"ℹ️ {s_asset} listed recently ({monthly_hist.index[0].strftime('%b %Y')}). Using max history ({max_months // 12}y {max_months % 12}m).")
                 c_closes = monthly_hist['Close']
             else:
                 c_closes = monthly_hist['Close'].tail(req_months)
                 
             months_actual = len(c_closes)
             
             # Defensive CAGR Calculation
             shares_bought = s_amt_final / c_closes
             cum_shares = shares_bought.cumsum()
             cum_invested = np.arange(1, months_actual + 1) * s_amt_final
             port_val = cum_shares * c_closes
             
             f_corpus = port_val.iloc[-1]
             t_inv = cum_invested[-1]
             
             if t_inv > 0 and months_actual > 0:
                 cagr = (f_corpus / t_inv) ** (1 / (months_actual/12)) - 1
             else:
                 cagr = 0.0
             
             sc1, sc2, sc3 = st.columns(3)
             with sc1: st.metric("Invested", format_inr(t_inv))
             with sc2: st.metric("Final Value", format_inr(f_corpus))
             with sc3: st.metric("Return (CAGR)", f"{(cagr*100):.1f}%")

             fig_area = go.Figure()
             fig_area.add_trace(go.Scatter(x=c_closes.index, y=cum_invested, fill='tozeroy', mode='lines', line=dict(color='#cbd5e1'), name='Principal'))
             fig_area.add_trace(go.Scatter(x=c_closes.index, y=port_val, fill='tonexty', mode='lines', line=dict(color='#10b981'), name='Market Value'))
             fig_area.update_layout(height=300, margin=dict(t=0,b=0,l=0,r=0), hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
             st.plotly_chart(fig_area, use_container_width=True)
         else:
              st.error("Insufficient historical data for this asset. Please try another ticker.")
    else:
        st.error("Please enter a valid asset ticker.")

# ------------------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------------------
st.markdown("<br><br><center style='color:#94a3b8; font-size:0.8rem;'>© 2026 Portfolio Pro • Multi-Asset Engine</center>", unsafe_allow_html=True)
