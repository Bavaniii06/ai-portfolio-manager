import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO

st.set_page_config(layout="wide", page_title="Portfolio Rebalancer")
st.markdown('<h1 style="color:#1e293b;">🎯 AI Portfolio Rebalancer</h1>', unsafe_allow_html=True)
st.markdown("*Upload demat → Auto rebalance → Goal-based future buys*")

# === UPLOAD YOUR DEMAT ===
uploaded_file = st.file_uploader("📁 Upload CSV/Excel (Stock,Quantity)", type=['csv','xlsx'])
goal = st.selectbox("🎯 Rebalance Goal", 
                   ["Long-term (5+ yrs, 60/40 Equity/Debt)", 
                    "Growth (3 yrs, 75/25 Equity/Debt)", 
                    "Aggressive (1-2 yrs, 90/10 Equity/Debt)"])

if uploaded_file is not None and st.button("🚀 REBALANCE PORTFOLIO", type="primary"):
    # === PARSE UPLOAD ===
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Assume columns: Stock, Quantity (add Price simulation)
    df['Price'] = np.random.uniform(500, 5000, len(df))
    df['Current Value'] = df['Quantity'] * df['Price']
    total_value = df['Current Value'].sum()
    
    # === TARGET ALLOCATIONS BY GOAL ===
    targets = {
        "Long-term (5+ yrs, 60/40 Equity/Debt)": {'Equity': 0.60, 'Debt': 0.40},
        "Growth (3 yrs, 75/25 Equity/Debt)": {'Equity': 0.75, 'Debt': 0.25},
        "Aggressive (1-2 yrs, 90/10 Equity/Debt)": {'Equity': 0.90, 'Debt': 0.10}
    }
    
    target_alloc = targets[goal]
    equity_target = total_value * target_alloc['Equity']
    debt_target = total_value * target_alloc['Debt']
    
    # === CURRENT vs TARGET ===
    current_equity = df['Current Value'].sum() * 0.85  # Assume 85% equity now
    rebalance_needs = {
        'Equity Over/Under': f"{'+' if current_equity > equity_target else '-'}{(abs(current_equity-equity_target)/1000):,.0f}K",
        'Debt Over/Under': f"{'+' if current_equity < equity_target else '-'}{(abs(debt_target-(total_value-current_equity))/1000):,.0f}K"
    }
    
    # === DASHBOARD ===
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Current Value", f"₹{total_value:,.0f}")
    col2.metric("🎯 Target Equity", f"₹{equity_target:,.0f}")
    col3.metric("⚖️ Rebalance Needed", f"₹{(abs(current_equity-equity_target)/1000):,.0f}K")
    
    # === HOLDINGS ANALYSIS ===
    st.subheader("📊 Current Holdings")
    df_display = df[['Stock', 'Quantity', 'Price', 'Current Value']].round(0)
    st.dataframe(df_display, use_container_width=True)
    
    # === REBALANCING PLAN ===
    st.subheader("🎯 Rebalancing Plan")
    plan_df = pd.DataFrame({
        'Action': ['Reduce Equity Exposure', 'Increase Debt Allocation', 'Top 3 Buys', 'Avoid'],
        'Recommendation': [
            f"Sell ₹{(current_equity-equity_target)/1000:,.0f}K equity",
            f"Buy ₹{(debt_target-(total_value-current_equity))/1000:,.0f}K debt",
            "HDFCBANK.NS, LT.NS, NESTLEIND.NS",
            "High-risk penny stocks"
        ],
        'Goal Alignment': [goal, goal, f"For {goal}", "Not suitable"]
    })
    st.dataframe(plan_df, use_container_width=True)
    
    # === VISUALS ===
    col1, col2 = st.columns(2)
    with col1:
        # Current vs Target Pie
        fig_pie = px.pie(values=[current_equity, total_value-current_equity], 
                        names=['Equity (Current)', 'Debt (Current)'],
                        title="Current Allocation")
        st.plotly_chart(fig_pie)
    
    with col2:
        fig_target = px.pie(values=[equity_target, debt_target], 
                           names=['Equity (Target)', 'Debt (Target)'],
                           title=f"Target for {goal}")
        st.plotly_chart(fig_target)
    
    # === FUTURE ADDITIONS ===
    st.subheader("➕ Future Monthly Additions")
    future_df = pd.DataFrame({
        'Month': ['Apr 2026', 'May 2026', 'Jun 2026'],
        'Amount': ['₹25,000', '₹25,000', '₹25,000'],
        'Allocation': ['60% Equity / 40% Debt', '60% Equity / 40% Debt', '60% Equity / 40% Debt'],
        'Suggested Stocks': ['HDFCBANK.NS + GSec', 'LT.NS + Bonds', 'NESTLEIND.NS + FDs']
    })
    st.dataframe(future_df)
    
    # DOWNLOAD
    full_report = pd.concat([df_display, plan_df])
    st.download_button("📥 Download Rebalance Plan", full_report.to_csv(), "rebalance-plan.csv")

st.info("📁 Upload your demat CSV → Select goal → REBALANCE = Your personalized plan!")
