import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="AI Portfolio Manager", layout="wide", page_icon="💰")

# Title
st.title("💰 AI Portfolio Manager")
st.markdown("---")

# Sidebar
st.sidebar.header("📈 Portfolio Settings")

# Portfolio input
st.sidebar.subheader("1. Enter Your Holdings")
col1, col2, col3 = st.sidebar.columns(3)
with col1: symbol1 = st.text_input("Symbol 1", value="RELIANCE.NS")
with col2: qty1 = st.number_input("Qty 1", value=10.0)
with col3: price1 = st.number_input("Price ₹ 1", value=2500.0)

with col1: symbol2 = st.text_input("Symbol 2", value="TCS.NS") 
with col2: qty2 = st.number_input("Qty 2", value=5.0)
with col3: price2 = st.number_input("Price ₹ 2", value=3800.0)

# Target allocation
st.sidebar.subheader("2. Target Allocation (%)")
target_alloc = {}
tickers = [symbol1, symbol2]
for i, ticker in enumerate(tickers):
    alloc = st.sidebar.slider(f"{ticker}", 0, 100, 50, key=f"alloc_{i}")
    target_alloc[ticker] = alloc / 100

# Create portfolio dataframe
portfolio_data = {
    'Symbol': [symbol1, symbol2],
    'Quantity': [qty1, qty2],
    'Price': [price1, price2],
    'Value': [qty1*price1, qty2*price2]
}
df_portfolio = pd.DataFrame(portfolio_data)
df_portfolio = df_portfolio.set_index('Symbol')

# Current allocation
total_value = df_portfolio['Value'].sum()
current_pct = df_portfolio['Value'] / total_value

# ============================================================================
# 1. PORTFOLIO SUMMARY 
# ============================================================================
st.subheader("📊 Portfolio Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Value", f"₹{total_value:,.0f}")
col2.metric("Largest Holding", f"{current_pct.idxmax()} ({current_pct.max()*100:.1f}%)")
col3.metric("Holdings", len(df_portfolio))
col4.metric("Avg Price", f"₹{df_portfolio['Price'].mean():.0f}")

st.dataframe(df_portfolio, width="stretch")

# Pie chart
fig_pie = px.pie(df_portfolio, values='Value', names=df_portfolio.index, 
                 title="Current Allocation", hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

# ============================================================================
# 2. TARGET ALLOCATION VISUALIZATION
# ============================================================================
st.subheader("🎯 Target vs Current Allocation")

# Target series (convert dict to Series)
target_series = pd.Series(target_alloc)
target_df = pd.DataFrame({
    'Current': current_pct.reindex(target_series.index, fill_value=0),
    'Target': target_series
}).fillna(0)

fig_compare = go.Figure()
fig_compare.add_trace(go.Bar(name='Current', x=target_df.index, y=target_df['Current']*100))
fig_compare.add_trace(go.Bar(name='Target', x=target_df.index, y=target_df['Target']*100))
fig_compare.update_layout(barmode='group', title="Allocation Comparison")
st.plotly_chart(fig_compare, use_container_width=True)

# ============================================================================
# 3. REBALANCE PLAN (CRASH-PROOF - THE COMPLETE FIX)
# ============================================================================
st.subheader("🔄 **Rebalance Plan**")
st.markdown("---")

# CRITICAL FIX: Align arrays by common assets ONLY
portfolio_assets = df_portfolio.index.values
target_assets = target_series.index.values
common_assets = np.intersect1d(portfolio_assets, target_assets)

if len(common_assets) == 0:
    st.error("❌ **No matching assets!** Add same tickers to both portfolio and targets.")
else:
    # ALIGN ARRAYS (THIS SOLVES THE ERROR)
    mask = np.isin(portfolio_assets, common_assets)
    current_aligned = current_pct[mask]
    target_aligned = target_series.loc[common_assets].values
    
    # Rebalance calculations
    pct_diff = current_aligned - target_aligned
    total_value = df_portfolio['Value'].sum()
    actions = []
    amounts = []
    
    for i, (asset, curr, tgt, diff) in enumerate(zip(common_assets, current_aligned, target_aligned, pct_diff)):
        if diff > 0.05:
            actions.append("🔴 **SELL**")
            amounts.append(abs(diff * total_value))
        elif diff < -0.05:
            actions.append("🟢 **BUY**")
            amounts.append(abs(diff * total_value))
        else:
            actions.append("🟡 **HOLD**")
            amounts.append(0)
    
    # Create rebalance table
    rebalance_df = pd.DataFrame({
        'Asset': common_assets,
        'Current %': [f"{p*100:.1f}%" for p in current_aligned],
        'Target %': [f"{t*100:.1f}%" for t in target_aligned],
        'Action': actions,
        'Amount ₹': [f"₹{int(a):,}" if a > 0 else "-" for a in amounts]
    })
    
    st.dataframe(rebalance_df, width="stretch")
    
    # Cash summary
    cash_needed = sum([a for a in amounts if a > 0])
    st.success(f"💰 **Total Cash Needed: ₹{int(cash_needed):,}**")

# Footer
st.markdown("---")
st.markdown("⭐ **Built with Streamlit | Deployed on Streamlit Cloud**")
