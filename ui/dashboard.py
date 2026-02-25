import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="NSE Advisor Pro", page_icon="🧠", layout="wide")

st.markdown("## 🧠 **Personalized NSE Portfolio Advisor**")
st.markdown("*AI matches your Age • Salary • Goal to NSE stocks/ETFs*")

# PERSONAL PROFILE - AGE GOAL SALARY
col_age, col_goal, col_salary = st.columns(3)
age = col_age.slider("👤 **Age**", 20, 65, 28)  # Your age from profile
goal = col_goal.selectbox("🎯 **Goal**", 
                         ["Emergency Fund (1yr)", "Short-term (1-3yr)", "Mid-term (3-7yr)", "Retirement (7+yr)"])
monthly_salary = col_salary.number_input("💰 **Monthly Salary** ₹", 25000, 200000, 60000)

# RISK PROFILE BY AGE + GOAL
risk_score = min((65-age)/65 * 100, 80)  # 100-age rule
if goal == "Emergency Fund": risk_score = 20
elif goal == "Short-term": risk_score = 40
equity_pct = risk_score / 100 * 0.8  # Conservative adjustment

st.markdown("---")

# AI RECOMMENDATIONS ENGINE
st.subheader("🤖 **Your Personalized NSE Portfolio**")

# NSE STOCKS DATABASE - Age/Goal matched
nse_database = {
    # Conservative/Low Risk (Age 50+ or Emergency)
    "Conservative": ["NIFTYBEES.NS", "ICICILIQ.NS", "BANKBEES.NS", "GOLDBEES.NS"],
    # Balanced (Age 30-50 Mid-term) 
    "Balanced": ["RELIANCE.NS", "HDFCBANK.NS", "TCS.NS", "NIFTYBEES.NS", "JUNIORBEES.NS"],
    # Growth (Age 25-40 Short/Mid-term)
    "Growth": ["INFY.NS", "BHARTIARTL.NS", "LT.NS", "ASIANPAINT.NS", "N100BEES.NS"],
    # Aggressive (Age <30 Long-term)
    "Aggressive": ["TATAMOTORS.NS", "JSWSTEEL.NS", "ADANIENT.NS", "MID150BEES.NS"]
}

# MATCH TO YOUR PROFILE
if risk_score < 40: profile = "Conservative"
elif risk_score < 60: profile = "Balanced" 
elif risk_score < 80: profile = "Growth"
else: profile = "Aggressive"

recommended_stocks = nse_database[profile][:5]  # Top 5 for you

# LIVE PRICES + PERFORMANCE
if st.button("📡 **FETCH LIVE NSE DATA**", type="primary"):
    with st.spinner("Analyzing NSE for your profile..."):
        try:
            data = yf.download(recommended_stocks, period="3mo", progress=False)['Adj Close']
            latest = data.iloc[-1].round(0)
            returns_1m = ((data.iloc[-1]/data.iloc[-21]-1)*100).round(2) if len(data)>21 else pd.Series(0, index=latest.index)
            
            portfolio_df = pd.DataFrame({
                'Stock': latest.index,
                'Live ₹': latest.values,
                '1M %': [f"{r:+.1f}%" for r in returns_1m],
                'Risk Fit': profile,
                'For You': ['✅ Yes' if i<3 else '⚠️ Watch' for i in range(len(latest))]
            })
            
            st.session_state.portfolio = portfolio_df
            st.success("✅ **Live NSE portfolio ready!**")
        except:
            st.info("🌐 Live data loading...")

# DISPLAY YOUR PORTFOLIO
if 'portfolio' in st.session_state:
    df = st.session_state.portfolio
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 **Recommended Stocks**", len(df))
    col2.metric("📈 **Avg 1M Return**", f"{df['1M %'].str.rstrip('%').astype(float).mean():+.1f}%")
    col3.metric("💰 **Monthly SIP**", f"₹{int(monthly_salary*0.2):,}")
    
    st.dataframe(df, use_container_width=True)
    
    # ALLOCATION PIE
    fig_pie = px.pie(names=df['Stock'], values=[25000]*len(df), hole=0.4,
                    title=f"**{profile} Portfolio** - {equity_pct*100:.0f}% Equity")
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # WHY THIS PORTFOLIO
    st.markdown("### **📋 Why These Stocks For You?**")
    reasons = {
        "Conservative": "Nifty ETFs + Gold = Capital protection",
        "Balanced": "RELIANCE+HDFC bluechips + JuniorBees growth", 
        "Growth": "IT+Infra leaders + N100 midcaps",
        "Aggressive": "High-beta industrials + Mid150 growth"
    }
    st.info(f"**{profile} Profile** → {reasons[profile]}\n"
            f"**Age {age}** → {equity_pct*100:.0f}% NSE Equity\n"
            f"**Salary ₹{monthly_salary:,}** → SIP ₹{int(monthly_salary*0.2):,}/mo\n"
            f"**Goal {goal}** → {risk_score:.0f}% Risk")

# TRADING SIGNALS
st.subheader("🎯 **Monthly Action Plan**")
signals = pd.DataFrame({
    'Action': ['BUY Top 3', 'HOLD Core', 'SIP Monthly', 'Rebalance Qrtly'],
    'Stocks': [', '.join(recommended_stocks[:3]), recommended_stocks[3], 'NIFTYBEES.NS', 'All'],
    'Amount': [f"₹{int(monthly_salary*0.1):,}", '-', f"₹{int(monthly_salary*0.2):,}", '5% deviation'],
    'Why': [f"{profile} winners", 'Stable base', f"20% salary rule", 'Risk control']
})
st.dataframe(signals, use_container_width=True)

# RISK METRICS
col_r1, col_r2, col_r3 = st.columns(3)
col_r1.metric("📊 **Expected Return**", f"{12 + risk_score/10:.1f}% p.a.")
col_r2.metric("📉 **Max Drawdown**", f"{15 + risk_score/2:.0f}%")
col_r3.metric("⏱️ **Recommended Horizon**", f"{3 if risk_score<50 else 5 if risk_score<70 else 7}+ years")

# DOWNLOAD
csv = df.to_csv(index=False) if 'portfolio' in st.session_state else ""
st.download_button("📥 **Download My NSE Portfolio**", csv, "my-nse-portfolio.csv")

st.markdown("---")
st.markdown("*🧠 AI Advisor for Bavani | Data Science Student | NSE-focused*")
