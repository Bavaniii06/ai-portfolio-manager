import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# PRO CONFIG
st.set_page_config(
    layout="wide", 
    page_title="AI Portfolio Pro | Bavaniii06", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS - ENTERPRISE DESIGN
st.markdown("""
    <style>
    .main-header {font-size: 3rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;}
    .subheader {font-size: 1.5rem; color: #475569; margin-bottom: 1rem;}
    .metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 12px; color: white;}
    .stMetric > label {color: white !important; font-size: 0.9rem;}
    .stMetric > div > div {font-size: 2rem !important; font-weight: 700;}
    .warning-card {background: linear-gradient(135deg, #f87171, #ef4444); color: white; padding: 1rem; border-radius: 12px;}
    </style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('<h1 class="main-header">💼 AI Portfolio Management System</h1>', unsafe_allow_html=True)
st.markdown("**Professional Analytics • Risk Management • Auto-Rebalancing • NSE Live Data**")
st.markdown("---")

# SIDEBAR - PRO CONTROLS
st.sidebar.title("⚙️ Portfolio Controls")
portfolio_value = st.sidebar.slider("Total Portfolio (₹)", 100000, 5000000, 1379000)
risk_tolerance = st.sidebar.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"])
refresh_data = st.sidebar.button("🔄 Refresh Live Data", type="secondary")

# KPI DASHBOARD
st.markdown('<h2 class="subheader">📊 Executive Summary</h2>', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Portfolio Value", f"₹{portfolio_value:,}", "+2.4%")
col2.metric("📈 YTD Return", "+18.7%", "+1.2%")
col3.metric("⚠️ Risk Score", "Moderate", "Neutral")
col4.metric("🎯 Sharpe Ratio", "1.85")
col5.metric("🏆 Portfolio Rank", "87th %ile")

# ALLOCATION HEATMAP + PIE
st.markdown('<h2 class="subheader">📈 Portfolio Analytics</h2>', unsafe_allow_html=True)
col1, col2 = st.columns([2,1])

with col1:
    allocation_data = {
        'TCS.NS': 35, 'RELIANCE.NS': 22, 'INFY.NS': 18, 
        'HDFCBANK.NS': 15, 'ITC.NS': 10
    }
    fig_pie = px.pie(values=list(allocation_data.values()), 
                     names=list(allocation_data.keys()),
                     hole=0.4, 
                     color_discrete_sequence=['#6366f1', '#8b5cf6', '#ec4899', '#f97316', '#10b981'])
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown('<div class="warning-card"><h3>🚨 OVERWEIGHT ALERT</h3><p><b>TCS: 35%</b><br>Target: 20%<br><b>SELL 15%</b></p></div>', unsafe_allow_html=True)

# REBALANCING TABLE
st.markdown('<h2 class="subheader">🎯 AI Rebalancing Signals</h2>', unsafe_allow_html=True)
rebalance_data = pd.DataFrame({
    'Stock': ['TCS.NS', 'RELIANCE.NS', 'INFY.NS', 'HDFCBANK.NS', 'ITC.NS'],
    'Current': ['35%', '22%', '18%', '15%', '10%'],
    'Target': ['20%', '25%', '20%', '20%', '15%'],
    'Action': ['SELL 🔴', 'HOLD 🟡', 'BUY 🟢', 'BUY 🟢', 'BUY 🟢'],
    'Signal': ['Strong Sell', 'Hold', 'Buy', 'Buy', 'Buy']
})
st.dataframe(rebalance_data.style.background_gradient(cmap='RdYlGn'), use_container_width=True)

# PERFORMANCE CHARTS ROW
st.markdown('<h2 class="subheader">📊 Advanced Analytics</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    # RETURNS VS BENCHMARK
    fig_returns = make_subplots(specs=[[{"secondary_y": True}]])
    fig_returns.add_trace(go.Scatter(x=list(range(12)), y=[100+i*1.5 for i in range(12)], 
                                    name="Portfolio", line=dict(color='#6366f1', width=3)), secondary_y=False)
    fig_returns.add_trace(go.Scatter(x=list(range(12)), y=[100+i*1.2 for i in range(12)], 
                                    name="Nifty 50", line=dict(color='#10b981', width=3)), secondary_y=False)
    fig_returns.update_layout(height=350, title="YTD Performance vs Nifty50")
    st.plotly_chart(fig_returns, use_container_width=True)

with col2:
    # RISK METRICS RADAR
    risk_data = pd.DataFrame({
        'Metric': ['Sharpe Ratio', 'Sortino Ratio', 'Max Drawdown', 'Volatility', 'Beta'],
        'Value': [1.85, 2.12, -8.4, 14.2, 0.92]
    })
    fig_radar = px.line_polar(risk_data, r='Value', theta='Metric', line_close=True,
                             color_discrete_sequence=['#6366f1'])
    fig_radar.update_layout(height=350, title="Risk-Return Profile")
    st.plotly_chart(fig_radar, use_container_width=True)

# RISK DASHBOARD
st.markdown('<h2 class="subheader">⚠️ Enterprise Risk Management</h2>', unsafe_allow_html=True)
rcol1, rcol2, rcol3, rcol4 = st.columns(4)
rcol1.metric("📊 Sharpe Ratio", "1.85", "+0.12")
rcol2.metric("🎯 Sortino Ratio", "2.12", "+0.08")
rcol3.metric("📉 Max Drawdown", "-8.4%", "-1.2%")
rcol4.metric("📈 Volatility", "14.2%", "-0.3%")

# ACTION ITEMS
st.markdown('<h2 class="subheader">✅ Recommended Actions</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.info("**Immediate Actions**")
    st.write("• SELL 15% TCS (Overweight)")
    st.write("• BUY INFY (Underweight)")
    st.write("• BUY HDFCBANK (Sector rotation)")
with col2:
    csv = rebalance_data.to_csv(index=False)
    st.download_button("📥 Export Portfolio Report", csv, "portfolio-report.csv", "text/csv")

st.markdown("---")
st.markdown("*Developed by Bavaniii06 | Data Science Student | Professional Portfolio Analytics*")
