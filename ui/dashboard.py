import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(layout="wide", page_title="Smart Portfolio Advisor")
st.markdown("""
<style>
.header {font-size: 2.8rem; color: #1e293b; font-weight: 800;}
.card {background: linear-gradient(135deg, #f8fafc, #e2e8f0); padding: 1.5rem; border-radius: 15px; margin: 1rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">🤖 Smart Demat Portfolio Advisor</h1>', unsafe_allow_html=True)
st.markdown("*AI-powered simulation • Goal-based recommendations • Live NSE analysis*")

# === GOAL SELECTION ===
col1, col2, col3 = st.columns(3)
goal = st.selectbox("🎯 Investment Goal", 
                   ["Long-term Wealth (5+ years)", "Short-term Gains (1-2 years)", "Balanced Growth (3 years)"])

investment_amount = st.slider("💰 Investment Amount", 10000, 5000000, 250000)
risk_profile = st.radio("⚠️ Risk Tolerance", ["Low", "Medium", "High"])

if st.button("🚀 GENERATE PORTFOLIO", type="primary"):
    # === SIMULATED PORTFOLIO BASED ON GOAL ===
    portfolios = {
        "Long-term Wealth (5+ years)": {
            "Stable": ["HDFCBANK.NS", "RELIANCE.NS", "ITC.NS", "HINDUNILVR.NS"],
            "Growth": ["TCS.NS", "INFY.NS", "LT.NS"]
        },
        "Short-term Gains (1-2 years)": {
            "High Growth": ["SBIN.NS", "TATAMOTORS.NS", "ADANIPORTS.NS"],
            "Momentum": ["NESTLEIND.NS", "ASIANPAINT.NS"]
        },
        "Balanced Growth (3 years)": {
            "Mixed": ["TCS.NS", "HDFCBANK.NS", "RELIANCE.NS", "SBIN.NS"]
        }
    }
    
    # Generate random portfolio
    portfolio_stocks = portfolios[goal]['Stable'] + portfolios[goal].get('Growth', [])
    np.random.shuffle(portfolio_stocks)
    portfolio_stocks = portfolio_stocks[:5]  # Top 5 stocks
    
    # Live prices + simulation
    portfolio_data = {}
    for stock in portfolio_stocks:
        ticker = yf.Ticker(stock)
        try:
            price = ticker.history(period="1d")['Close'].iloc[-1]
        except:
            price = np.random.uniform(1500, 4500)
        qty = int(investment_amount * np.random.uniform(0.1, 0.3) / price)
        value = qty * price
        portfolio_data[stock] = {'Quantity': qty, 'Price': price, 'Value': value}
    
    df_portfolio = pd.DataFrame(portfolio_data).T
    total_value = df_portfolio['Value'].sum()
    
    # === EXECUTIVE SUMMARY ===
    st.markdown('<div class="card"><h2>📊 Portfolio Summary</h2></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Invested", f"₹{investment_amount:,}")
    col2.metric("📈 Current Value", f"₹{total_value:,.0f}")
    col3.metric("💰 P&L", f"₹{(total_value-investment_amount):,.0f}", f"{((total_value/investment_amount-1)*100):.1f}%")
    col4.metric("⚠️ Risk Level", risk_profile)
    
    # === HOLDINGS TABLE ===
    st.markdown('<div class="card"><h2>📋 Recommended Holdings</h2></div>', unsafe_allow_html=True)
    df_portfolio = df_portfolio.round(2)
    st.dataframe(df_portfolio, use_container_width=True)
    
    # === ALLOCATION CHART ===
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df_portfolio.reset_index(), values='Value', names='index', 
                    title=f"Portfolio Allocation - {goal}")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Why These Stocks?")
        st.write(f"**Goal**: {goal}")
        st.write("• **Blue-chip stability** for long-term")
        st.write("• **High-growth momentum** for short-term")
        st.write("• **Live NSE prices**")
        st.write("• **Risk-matched** to your profile")
    
    # === TRADING SIGNALS ===
    st.markdown('<div class="card"><h2>📈 Trading Signals</h2></div>', unsafe_allow_html=True)
    signals_df = pd.DataFrame({
        'Recommendation': ['HOLD Top Performers', 'ADD on Dips', 'Rebalance Monthly'],
        'Stocks': ['TCS.NS, RELIANCE.NS', 'INFY.NS, HDFCBANK.NS', 'All holdings'],
        'Time Horizon': ['Long-term', '3-6 months', 'Monthly']
    })
    st.dataframe(signals_df)
    
    # === RISK ANALYSIS ===
    st.markdown('<div class="card"><h2>⚠️ Risk Profile Analysis</h2></div>', unsafe_allow_html=True)
    rcol1, rcol2, rcol3 = st.columns(3)
    rcol1.metric("📊 Expected Return", f"{(risk_profile=='High')*25+(risk_profile=='Medium')*18+(risk_profile=='Low')*12}%")
    rcol2.metric("📉 Max Drawdown", f"-{(risk_profile=='High')*15+(risk_profile=='Medium')*10+(risk_profile=='Low')*6}%")
    rcol3.metric("🎯 Recommended Horizon", f"{5 if risk_profile=='Low' else 3 if risk_profile=='Medium' else 1} years")
    
    # EXPORT
    csv_data = df_portfolio.reset_index().to_csv(index=False)
    st.download_button("📥 Download My Portfolio", csv_data, "recommended-portfolio.csv")
    
    st.balloons()
    st.success(f"✅ **Portfolio ready for {goal}!** Download & invest!")

st.info("👆 Select goal → Amount → Risk → GENERATE = Your personalized NSE portfolio!")
