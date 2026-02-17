import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("AI Portfolio Dashboard")
st.markdown("Professional 5-chart demo")

# 1. METRICS - STRINGS ONLY
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Value", "137900")
col2.metric("1M Return", "+4.2%")
col3.metric("Risk Score", "Medium")
col4.metric("Sharpe Ratio", "1.42")

# 2. BAR CHART
st.subheader("Portfolio Allocation")
data = {
    'TCS': 48000, 
    'RELIANCE': 22800, 
    'INFY': 21600, 
    'HDFC': 28500
}
st.bar_chart(data)

# 3. WARNING
st.error("TCS OVERWEIGHT 35% - SELL RECOMMENDED")

# 4. REBALANCING TABLE
st.subheader("AI Rebalancing")
table = pd.DataFrame({
    'Stock': ['TCS', 'RELIANCE', 'INFY', 'HDFC'],
    'Current': ['35%', '17%', '16%', '21%'],
    'Target': ['25%', '25%', '25%', '25%'],
    'Action': ['SELL', 'BUY', 'BUY', 'HOLD']
})
st.dataframe(table)

# 5. RISK METRICS
st.subheader("Risk Analysis")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Sharpe", "1.42")
r2.metric("Beta", "0.95")
r3.metric("Drawdown", "-8.2%")
r4.metric("Volatility", "12.4%")

st.success("5 charts working!")
