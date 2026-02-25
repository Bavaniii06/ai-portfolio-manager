import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="NSE Portfolio Pro", page_icon="📈", layout="wide")

st.markdown("# 📈 **NSE Portfolio Manager**")
st.markdown("**Perfect Holdings • Live NSE • Auto Rebalance**")

# TABS
tab1, tab2, tab3 = st.tabs(["📊 Portfolio", "🔍 Live NSE", "🎯 Rebalance"])

with tab1:
    st.subheader("**Enter Your Holdings**")
    
    # FIXED: SAFE DEFAULTS - No zero/negative values
    portfolio_data = []
    for i in range(6):
        col1, col2, col3 = st.columns([3,1.5,1.5])
        
        symbol = col1.text_input(f"Stock {i+1}", 
            value=["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","",""][i])
        
        qty = col2.number_input(f"Qty {i+1}", 
            value=[10.0,5.0,15.0,20.0,0.0,0.0][i], 
            min_value=0.0, step=1.0)
            
        price = col3.number_input(f"Price ₹{i+1}", 
            value=[2800.0,4200.0,1650.0,1850.0,100.0,100.0][i], 
            min_value=0.1, step=10.0)
        
        # Live value preview
        value = qty * price
        st.caption(f"**Value: ₹{value:,.0f}**")
        
        if symbol and qty > 0 and price > 0:
            portfolio_data.append({"Symbol": symbol, "Quantity": qty, "Avg_Price": price})

    # Build Portfolio Table
    if portfolio_data:
        df = pd.DataFrame(portfolio_data)
        df['Value'] = df['Quantity'] * df['Avg_Price']
        df = df.set_index('Symbol')
        
        total = df['Value'].sum()
        pct = df['Value']/total * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total", f"₹{total:,.0f}")
        col2.metric("📊 Stocks", len(df))
        col3.metric("🔴 Largest", f"{pct.max():.0f}%")
        
        st.dataframe(df[['Quantity','Avg_Price','Value']], use_container_width=True)
        
        fig = px.pie(values=pct, names=df.index, hole=0.4, title="Allocation")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("➕ **Add stocks above**")

with tab2:
    st.subheader("**Live NSE Prices** (25 Stocks + Gold/Silver)")
    
    NSE_STOCKS = [
        "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
        "KOTAKBANK.NS","BHARTIARTL.NS","ITC.NS","LT.NS","AXISBANK.NS",
        "GOLDBEES.NS","SILVERBEES.NS","NIFTYBEES.NS","BANKBEES.NS"
    ]
    
    if st.button("**SCAN LIVE NSE**"):
        with st.spinner("Loading..."):
            try:
                data = yf.download(NSE_STOCKS, period="1mo", progress=False)['Adj Close']
                returns = ((data.iloc[-1]/data.iloc[0]-1)*100).round(1)
                
                live_df = pd.DataFrame({
                    'Stock': NSE_STOCKS,
                    'Price': data.iloc[-1].round(0),
                    '1M %': [f"{r:+.1f}%" for r in returns]
                }).sort_values('1M %', key=lambda x: x.str.rstrip('%').astype(float), ascending=False)
                
                st.dataframe(live_df, use_container_width=True)
                st.success("✅ **LIVE NSE DATA**")
            except:
                st.info("🌐 **Use .NS tickers for live prices**")

with tab3:
    st.subheader("**Smart Rebalance**")
    
    if 'df' in locals() and not df.empty:
        st.info("🎯 **Drag sliders** to set target allocation")
        
        targets = {}
        for symbol in df.index:
            targets[symbol] = st.slider(symbol, 0, 100, 25)
        
        # Calculate rebalance
        current_pct = df['Value']/df['Value'].sum()
        rebalance_list = []
        
        for symbol in df.index:
            curr = current_pct[symbol]*100
            target = targets[symbol]/100
            gap = curr - targets[symbol]
            
            action = "🟢 BUY" if gap < -5 else "🔴 SELL" if gap > 5 else "🟡 HOLD"
            amount = abs((curr-targets[symbol])/100 * df['Value'].sum())
            
            rebalance_list.append({
                'Stock': symbol,
                'Current': f"{curr:.1f}%",
                'Target': f"{targets[symbol]}%",
                'Action': action,
                'Amount': f"₹{amount:,.0f}"
            })
        
        rebalance_df = pd.DataFrame(rebalance_list)
        st.dataframe(rebalance_df, use_container_width=True)
        
        buy_amounts = rebalance_df[rebalance_df['Action']=='🟢 BUY']['Amount'].str.replace('₹','').str.replace(',','').astype(float)
        st.success(f"💰 **Cash Needed: ₹{buy_amounts.sum():,.0f}**")
    else:
        st.warning("⚠️ **Enter portfolio first**")

st.markdown("---")
st.markdown("*⭐ **Perfect NSE Portfolio Manager 2026** - Quantity • Price • Live • Rebalance*")
