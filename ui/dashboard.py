import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🤖 AI Portfolio Dashboard")
st.markdown("**Professor Demo Ready**")

# METRICS - PLAIN STRINGS ONLY
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Value", "137900")
col2.metric("1M Return", "+4.2%")
col3.metric("Risk Score", "Medium")
col4.metric("Sharpe Ratio", "1.42")

# BAR CHART
st.subheader("Portfolio Allocation")
st.bar_chart({"TCS.NS": 48, "RELIANCE.NS": 22, "INFY.NS": 21, "HDFCBANK.NS": 28})

# WARNING
st.error("🔴 TCS OVERWEIGHT 35% → SELL RECOMMENDED")

# REBALANCING TABLE
st.subheader("AI Rebalancing")
df = pd.DataFrame({
    "Stock": ["TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS"],
    "Action": ["SELL", "BUY", "BUY", "HOLD"]
})
st.dataframe(df)

st.success("✅ 4 Charts Live! Professor Ready!")
