import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="My Portfolio", page_icon="💰", layout="wide")

# PERSONAL BRANDING
st.markdown("""
# 💰 **My Real Portfolio Manager**
**Live Prices • Personal Risk Profile • YOUR Money Decisions**
""")

# STEP 1: USER PROFILE (Personalization)
st.sidebar.header("👤 **Your Profile**")
risk_profile = st.sidebar.selectbox("Risk Appetite", ["Conservative", "Balanced", "Growth", "Aggressive"])
investment_goal = st.sidebar.selectbox("Goal", ["Retirement", "House", "Education", "Wealth"])
monthly_sip = st.sidebar.number_input("Monthly SIP ₹", 5000, 100000, 15000)
total_portfolio = st.sidebar.number_input("Total Investment ₹", 10000, 5000000, 250000)

# MAIN PORTFOLIO SECTION
tab1, tab2, tab3, tab4 = st.tabs(["📊 My Holdings", "📈 Live Watchlist", "🎯 Personal Recs", "⚖️ Rebalance"])

with tab1:
    st.header("**1. My Current Holdings**")
    
    # EASY INPUT - Like Excel
    if 'my_holdings' not in st.session_state:
        st.session_state.my_holdings = pd.DataFrame()
    
    # Add/Edit Holdings
    with st.form("add_holding"):
        col1, col2, col3, col4 = st.columns([2,1,1,1])
        new_symbol = col1.text_input("Stock/ETF", "RELIANCE.NS")
        new_qty = col2.number_input("Quantity", 1, 1000, 10)
        new_price = col3.number_input("Avg Buy Price ₹", 10.0, 10000.0, 2500.0)
        add_stock = col4.form_submit_button("➕ Add")
        
        if add_stock:
            new_row = pd.DataFrame([{
                "Symbol": new_symbol,
                "Quantity": new_qty,
                "Avg_Price": new_price,
                "Added": datetime.now().strftime("%d/%m")
            }])
            st.session_state.my_holdings = pd.concat([st.session_state.my_holdings, new_row])
            st.success(f"✅ Added {new_symbol}")

    # SHOW MY HOLDINGS TABLE
    if not st.session_state.my_holdings.empty:
        st.subheader("**My Portfolio**")
        
        # LIVE PRICES
        symbols = st.session_state.my_holdings['Symbol'].tolist()
        try:
            live_data = yf.download(symbols, period="1d", progress=False)['Adj Close']
            latest_prices = live_data.iloc[-1]
            
            st.session_state.my_holdings['Live_Price'] = st.session_state.my_holdings['Symbol'].map(latest_prices)
            st.session_state.my_holdings['Market_Value'] = st.session_state.my_holdings['Quantity'] * st.session_state.my_holdings['Live_Price']
            st.session_state.my_holdings['P&L'] = st.session_state.my_holdings['Market_Value'] - (st.session_state.my_holdings['Quantity'] * st.session_state.my_holdings['Avg_Price'])
            st.session_state.my_holdings['P&L_%'] = (st.session_state.my_holdings['P&L'] / (st.session_state.my_holdings['Quantity'] * st.session_state.my_holdings['Avg_Price'])) * 100
            
        except:
            st.session_state.my_holdings['Live_Price'] = st.session_state.my_holdings['Avg_Price']
            st.session_state.my_holdings['Market_Value'] = st.session_state.my_holdings['Quantity'] * st.session_state.my_holdings['Live_Price']
            st.session_state.my_holdings['P&L'] = 0
            st.session_state.my_holdings['P&L_%'] = 0
        
        # KPI CARDS
        total_value = st.session_state.my_holdings['Market_Value'].sum()
        total_pnl = st.session_state.my_holdings['P&L'].sum()
        pnl_pct = (total_pnl / (total_value - total_pnl)) * 100 if total_value > total_pnl else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Total Value", f"₹{total_value:,.0f}")
        c2.metric("📈 P&L", f"₹{total_pnl:,.0f}", f"{pnl_pct:+.1f}%")
        c3.metric("📊 Stocks", len(st.session_state.my_holdings))
        c4.metric("🎯 Risk", risk_profile)
        
        # DETAILED TABLE
        st.dataframe(st.session_state.my_holdings[['Symbol', 'Quantity', 'Avg_Price', 'Live_Price', 'Market_Value', 'P&L', 'P&L_%']], 
                    use_container_width=True)
        
        # ALLOCATION CHART
        allocation = st.session_state.my_holdings.set_index('Symbol')['Market_Value'] / total_value * 100
        fig = px.pie(values=allocation, names=allocation.index, title="My Allocation", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("**2. Live Market Watch**")
    watchlist = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "GOLDBEES.NS", "NIFTYBEES.NS"]
    
    if st.button("🔄 Refresh Live Prices"):
        data = yf.download(watchlist, period="5d")['Adj Close']
        returns_5d = ((data.iloc[-1]/data.iloc[0]-1)*100).round(1)
        
        watch_df = pd.DataFrame({
            'Symbol': watchlist,
            'Price': data.iloc[-1].round(0),
            '5D Change': [f"{r:+.1f}%" for r in returns_5d]
        }).sort_values('5D Change', key=lambda x: x.str.rstrip('%').astype(float), ascending=False)
        
        st.dataframe(watch_df, use_container_width=True)

with tab3:
    st.header("**3. Personal Investment Advice**")
    
    # PERSONALIZED RECOMMENDATIONS
    recommendations = {
        "Conservative": ["GOLDBEES.NS (15%)", "NIFTYBEES.NS (40%)", "BANKBEES.NS (25%)", "LIQUIDBEES.NS (20%)"],
        "Balanced": ["HDFCBANK.NS (20%)", "RELIANCE.NS (15%)", "ITC.NS (15%)", "NIFTYBEES.NS (30%)", "GOLDBEES.NS (20%)"],
        "Growth": ["TCS.NS (25%)", "INFY.NS (20%)", "BHARTIARTL.NS (15%)", "NIFTYBEES.NS (25%)", "JUNIORBEES.NS (15%)"],
        "Aggressive": ["TATAMOTORS.NS (25%)", "ADANIPORTS.NS (20%)", "JINDALSTEL.NS (20%)", "JUNIORBEES.NS (20%)", "SMALLCPSE.NS (15%)"]
    }
    
    recs = recommendations[risk_profile]
    st.markdown(f"**Based on your {risk_profile} profile + ₹{monthly_sip:,} SIP:**")
    
    for i, rec in enumerate(recs, 1):
        st.markdown(f"**{i}.** {rec}")

with tab4:
    st.header("**4. Smart Rebalance**")
    if not st.session_state.my_holdings.empty:
        st.info("🎯 Set your target allocation")
        
        targets = {}
        for symbol in st.session_state.my_holdings['Symbol']:
            targets[symbol] = st.slider(symbol, 0, 100, 20)
        
        current_alloc = st.session_state.my_holdings.set_index('Symbol')['Market_Value'] / total_value * 100
        rebalance_actions = []
        
        for symbol in st.session_state.my_holdings['Symbol']:
            curr_pct = current_alloc[symbol]
            target_pct = targets[symbol]
            diff = curr_pct - target_pct
            
            action = "🟢 BUY" if diff < -5 else "🔴 SELL" if diff > 5 else "➡️ HOLD"
            amount = abs(diff/100 * total_value)
            
            rebalance_actions.append({
                'Stock': symbol,
                'Current %': f"{curr_pct:.1f}%",
                'Target %': f"{target_pct}%",
                'Action': action,
                '₹ Move': f"₹{amount:,.0f}"
            })
        
        rebalance_df = pd.DataFrame(rebalance_actions)
        st.dataframe(rebalance_df)
        
        cash_need = rebalance_df[rebalance_df['Action']=='🟢 BUY']['₹ Move'].str.replace('₹','').str.replace(',','').astype(float).sum()
        st.success(f"💰 **Cash Required: ₹{cash_need:,.0f}**")

st.markdown("---")
st.markdown("**⭐ Built for REAL investors | Live tracking | Personal suggestions | Tiruppur 2026**")
