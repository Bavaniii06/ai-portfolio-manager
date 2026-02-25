import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="NSE Demat Pro", page_icon="🏦", layout="wide")

st.markdown("# 🏦 **NSE Demat Portfolio Pro**")
st.markdown("**🔗 Simulated Zerodha/Groww • Live NSE • AI Rebalance • P&L Tracking**")

# SIMULATED DEMAT DATA (Real Zerodha API format)
@st.cache_data(ttl=300)  # Refresh every 5 min
def fetch_simulated_demat():
    """Simulate real Zerodha KiteConnect.holdings() API"""
    return pd.DataFrame({
        'tradingsymbol': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'],
        'exchange': ['NSE', 'NSE', 'NSE', 'NSE', 'NSE'],
        'quantity': [12, 8, 25, 15, 20],
        'average_price': [2850.50, 4150.25, 1625.80, 1820.10, 1185.75],
        'pnl': [2450.00, -125.50, 1875.20, 450.75, 320.25],
        'sector': ['Energy', 'IT', 'Banking', 'IT', 'Banking'],
        'last_price': [2925.60, 4185.20, 1650.40, 1850.90, 1195.50]
    })

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["🏦 Demat Sync", "📊 Portfolio", "🔍 Live NSE", "🎯 AI Rebalance"])

with tab1:
    st.subheader("**🔗 Connect Demat (Simulation)**")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("**🟢 SIMULATE ZERODHA**", type="primary"):
            st.session_state.demat_data = fetch_simulated_demat()
            st.success("✅ **Zerodha holdings synced!** (12 RELIANCE + 8 TCS + ...)")
    
    with col_btn2:
        if st.button("**🔵 SIMULATE GROWW**", type="secondary"):
            # Groww simulation
            st.session_state.demat_data = pd.DataFrame({
                'tradingsymbol': ['TCS.NS', 'RELIANCE.NS', 'SBIN.NS'],
                'quantity': [10, 15, 50],
                'average_price': [4100, 2800, 750],
                'pnl': [850, 3750, -1250]
            })
            st.success("✅ **Groww holdings synced!**")
    
    # DISPLAY SYNCHRONIZED HOLDINGS
    if 'demat_data' in st.session_state:
        demat = st.session_state.demat_data
        st.dataframe(demat[['tradingsymbol', 'quantity', 'average_price', 'pnl']], use_container_width=True)
        
        total_pnl = demat['pnl'].sum()
        col_p1, col_p2 = st.columns(2)
        col_p1.metric("💰 Total P&L", f"₹{total_pnl:,.0f}")
        col_p2.metric("📊 Holdings", len(demat))

with tab2:
    st.subheader("**📊 Real-Time Portfolio**")
    
    if 'demat_data' in st.session_state:
        demat = st.session_state.demat_data.copy()
        
        # LIVE PRICES UPDATE
        symbols = demat['tradingsymbol'].tolist()
        try:
            live_prices = yf.download(symbols, period="1d", progress=False)['Adj Close'].iloc[-1]
            demat['live_price'] = [live_prices.get(s, row['average_price']) for s, row in demat.iterrows()]
        except:
            demat['live_price'] = demat['average_price']
        
        # CALCULATIONS
        demat['current_value'] = demat['quantity'] * demat['live_price']
        demat['pnl_pct'] = ((demat['live_price']/demat['average_price']-1)*100).round(2)
        total_value = demat['current_value'].sum()
        
        # METRICS
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Portfolio Value", f"₹{total_value:,.0f}")
        col2.metric("📈 Total P&L", f"₹{demat['pnl'].sum():,.0f}")
        col3.metric("🎯 Best Stock", f"{demat.loc[demat['pnl_pct'].idxmax(), 'tradingsymbol']} +{demat['pnl_pct'].max():.1f}%")
        col4.metric("⚠️ Worst Stock", f"{demat.loc[demat['pnl_pct'].idxmin(), 'tradingsymbol']} {demat['pnl_pct'].min():.1f}%")
        
        # PORTFOLIO TABLE
        portfolio_display = demat[['tradingsymbol', 'quantity', 'average_price', 'live_price', 
                                  'current_value', 'pnl', 'pnl_pct']].round(0)
        portfolio_display.columns = ['Stock', 'Qty', 'Avg ₹', 'Live ₹', 'Value ₹', 'P&L ₹', 'P&L %']
        st.dataframe(portfolio_display, use_container_width=True)
        
        # ALLOCATION PIE
        fig_pie = px.pie(values=demat['current_value'], names=demat['tradingsymbol'], 
                        title="Portfolio Allocation", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # SECTOR BREAKDOWN
        sector_pnl = demat.groupby('sector')['pnl'].sum()
        fig_sector = px.bar(x=sector_pnl.index, y=sector_pnl.values, 
                          title="Sector P&L", color=sector_pnl.values)
        st.plotly_chart(fig_sector, use_container_width=True)

with tab3:
    st.subheader("**🔴 LIVE NSE Market Scanner**")
    
    NSE_LIVE = [
        "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS",
        "INFY.NS","ITC.NS","LT.NS","AXISBANK.NS","KOTAKBANK.NS"
    ]
    
    col_period, col_sort = st.columns(2)
    with col_period:
        period = st.selectbox("Timeframe", ["1d", "5d", "1mo"])
    with col_sort:
        sort_by = st.selectbox("Sort", ["Price", "1M %", "Volume"])
    
    if st.button("**📡 SCAN LIVE NSE**", type="primary"):
        with st.spinner("Live NSE data..."):
            try:
                data = yf.download(NSE_LIVE, period=period, progress=False)['Adj Close']
                latest_prices = data.iloc[-1].dropna()
                change_pct = ((latest_prices / data.iloc[0] - 1) * 100).round(2)
                
                live_table = pd.DataFrame({
                    'Price': latest_prices.round(0),
                    f'{period.upper()} %': [f"{p:+.2f}%" for p in change_pct]
                }).sort_values(f'{period.upper()} %', ascending=False, key=lambda x: x.str.rstrip('%').astype(float))
                
                st.dataframe(live_table, use_container_width=True)
                st.success(f"✅ **LIVE NSE** | {datetime.now().strftime('%H:%M IST')}")
            except Exception as e:
                st.error(f"⚠️ {e}")

with tab4:
    st.subheader("**🤖 AI Rebalance + Risk Engine**")
    
    if 'demat_data' in st.session_state:
        df = st.session_state.demat_data.copy()
        df['current_value'] = df['quantity'] * df['last_price']
        current_alloc = df['current_value'] / df['current_value'].sum() * 100
        
        # TARGET ALLOCATION SLIDERS
        st.info("🎯 **Set target weights**")
        target_weights = {}
        for symbol in df['tradingsymbol'][:4]:  # Top 4
            target_weights[symbol] = st.slider(
                f"{symbol}", 0, 60, int(current_alloc[df['tradingsymbol']==symbol].iloc[0]), 1
            )
        
        if st.button("**⚖️ CALCULATE REBALANCE**"):
            rebalance_plan = []
            portfolio_value = df['current_value'].sum()
            
            for symbol in df['tradingsymbol']:
                curr_wt = current_alloc[df['tradingsymbol']==symbol].iloc[0]
                tgt_wt = target_weights.get(symbol, 25)
                gap = curr_wt - tgt_wt
                
                if abs(gap) > 3:
                    action = "🟢 BUY" if gap < 0 else "🔴 SELL"
                    trade_value = abs(gap/100 * portfolio_value)
                else:
                    action = "🟡 HOLD"
                    trade_value = 0
                
                rebalance_plan.append({
                    'Stock': symbol,
                    'Current': f"{curr_wt:.1f}%",
                    'Target': f"{tgt_wt}%",
                    'Action': action,
                    'Trade ₹': f"₹{trade_value:,.0f}"
                })
            
            rebalance_df = pd.DataFrame(rebalance_plan)
            st.dataframe(rebalance_df, use_container_width=True)
            
            buy_trades = rebalance_df[rebalance_df['Action']=='🟢 BUY']['Trade ₹'].str.replace('₹','').str.replace(',','').astype(float)
            st.metric("💰 Cash Required", f"₹{buy_trades.sum():,.0f}")

# GLOBAL EXPORT
st.markdown("---")
if 'demat_data' in st.session_state:
    csv_data = st.session_state.demat_data.to_csv(index=False)
    st.download_button("📊 Export Demat CSV", csv_data, "demat-portfolio.csv", "text/csv")
st.caption("*🏦 Simulated Zerodha/Groww API | Production ready for real API keys*")
