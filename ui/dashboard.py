import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("💼 AI Portfolio Management System")
st.markdown("**Professional Analytics • Risk Management • Auto-Rebalancing**")

# 1. EXECUTIVE METRICS
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Portfolio Value", "₹1,37,900")
col2.metric("📈 1M Return", "+4.2%")
col3.metric("⚠️ Risk Score", "Moderate")
col4.metric("🎯 Sharpe Ratio", "1.42")

# 2. ALLOCATION CHART 
st.subheader("📊 Portfolio Allocation")
st.bar_chart({"TCS.NS": 48, "RELIANCE.NS": 22, "INFY.NS": 21, "HDFCBANK.NS": 28})

# 3. OVERWEIGHT WARNING
st.error("🔴 **TCS OVERWEIGHT 35%** → **SELL RECOMMENDED**")

# 4. REBALANCING TABLE
st.subheader("🎯 AI Trading Signals")
df = pd.DataFrame({
    "Stock": ["TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS"],
    "Current %": ["35%", "17%", "16%", "21%"],
    "Target %": ["25%", "25%", "25%", "25%"],
    "Action": ["SELL 🔴", "BUY 🟢", "BUY 🟢", "HOLD 🟡"]
})
st.dataframe(df, use_container_width=True)

# 5. RISK DASHBOARD
st.subheader("⚠️ Risk Analytics")
rcol1, rcol2, rcol3, rcol4 = st.columns(4)
rcol1.metric("📊 Sharpe Ratio", "1.42")
rcol2.metric("🎯 Beta vs Nifty", "0.95")
rcol3.metric("📉 Max Drawdown", "-8.2%")
rcol4.metric("📈 Volatility", "12.4%")

# DOWNLOAD BUTTON ONLY
csv = df.to_csv(index=False)
st.download_button("📊 Export Report", csv, "portfolio-analysis.csv", "text/csv")
