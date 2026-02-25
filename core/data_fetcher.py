import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="NSE/BSE Portfolio Rebalancer", layout="wide", page_icon="💰")

st.title("🎯 **NSE/BSE Portfolio Rebalancer**")
st.markdown("**AI Rebalancing • Live Prices • Professional Analytics**")
st.markdown("---")

# Sidebar - Portfolio Input
st.sidebar.header("📊 **Current Portfolio**")

portfolio_data = []
for i in range(4):
    with st.sidebar.expander(f"Holding {i+1}", expanded=(i==0)):
        symbol = st.text_input(f"Ticker {i+1}", value=["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"][i], key=f"s{i}")
        qty = st.number_input(f"Quantity {i+1}", value=[10, 8, 15, 12][i], min_value=0.0, key=f"q{i}")
        avg_price = st.number_input(f"Avg Price ₹{i+1}", value=[2500, 3800, 1650, 1450][i], min_value=0.0, key=f"p{i}")
        portfolio_data.append({"Symbol": symbol, "Qty": qty, "Avg_Price": avg_price})

df_portfolio = pd.DataFrame(portfolio_data)
df_portfolio['Value'] = df_portfolio['Qty'] * df_portfolio['Avg_Price']
df_portfolio = df_portfolio.set_index('Symbol')

# Current percentages
total_value = df_portfolio['Value'].sum()
current_pct = df_portfolio['Value'] / total_value

# Target allocation
st.sidebar.markdown("---")
st.sidebar.header("🎯 **Target Allocation (%)**")
target_alloc = {}
for symbol in df_portfolio.index:
    pct = st.sidebar.slider(symbol, 0, 100, 25, key=f"tgt_{symbol}")
    target_alloc[symbol] = pct / 100

# ============================================================================
# DASHBOARD ROW 1 - METRICS
# ============================================================================
col1, col2, col3 = st.columns(3)
col1.metric("💰 **Portfolio Value**", f"₹{total_value:,.0f}")
col2.metric("📊 **Holdings**", len(df_portfolio))
col3.metric("⚠️ **Risk**", "HIGH" if current_pct.max() > 0.4 else "MEDIUM")

st.subheader("📈 **Current Holdings**")
st.dataframe(df_portfolio[['Qty', 'Avg_Price', 'Value']], width="stretch")

# Pie chart
fig = px.pie(values=current_pct*100, names=current_pct.index, hole=0.3, title="Current Allocation")
st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# REBALANCE SECTION (LINE 69 FIXED - BULLETPROOF)
# ============================================================================
st.subheader("🔄 **Rebalance Plan**")

# FIX: Align indexes first
common_assets = [asset for asset in current_pct.index if asset in target_alloc]
if not common_assets:
    st.error("❌ No matching assets found!")
else:
    # ALIGN ARRAYS (THIS FIXES THE ERROR)
    current_aligned = current_pct[common_assets].values
    target_aligned = np.array([target_alloc[asset] for asset in common_assets])
    
    # Line 69 - NOW SAFE!
    diff_pct = current_aligned - target_aligned
    actions = []
    amounts = []
    
    for i, (asset, diff) in enumerate(zip(common_assets, diff_pct)):
        if diff > 0.05:
            action = "🔴 SELL"
            amount = abs(diff * total_value)
        elif diff < -0.05:
            action = "🟢 BUY"
            amount = abs(diff * total_value)
        else:
            action = "🟡 HOLD"
            amount = 0
        
        actions.append(action)
        amounts.append(round(amount))
    
    # Rebalance table
    rebalance_df = pd.DataFrame({
        'Asset': common_assets,
        'Current%': (current_aligned*100).round(1),
        'Target%': (target_aligned*100).round(1),
        'Action': actions,
        'Amount₹': [f"₹{amt:,}" if amt>0 else "-" for amt in amounts]
    })
    
    st.dataframe(rebalance_df, width="stretch")
    
    # Cash needed
    cash_buy = sum([amt for amt in amounts if amt > 0])
    st.success(f"💰 **Cash Needed for BUYs: ₹{cash_buy:,}**")

st.markdown("---")
st.caption("⭐ Demo Mode - Add real NSE/BSE tickers (.NS) for live prices")
