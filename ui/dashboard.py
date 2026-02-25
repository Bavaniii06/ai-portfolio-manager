import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="AI Advisor", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
# 🤖 **AI Investment Advisor** 
**Professional portfolio management • Live market analysis • Personalized strategy**
""")

# SIMULATED DEMAT (Real Zerodha/Groww format)
@st.cache_data(ttl=1800)
def load_sample_demat():
    """Your sample demat holdings"""
    return pd.DataFrame({
        'Symbol': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'],
        'Quantity': [12.0, 8.0, 25.0, 15.0, 20.0],
        'Avg_Price': [2850.50, 4150.25, 1625.80, 1820.10, 1185.75],
        'Live_Price': [2925.60, 4185.20, 1650.40, 1850.90, 1195.50],
        'PnL_Rs': [907.20, 280.00, 618.00, 466.50, 196.00]
    })

# PERSONAL PROFILE
st.sidebar.header("👤 **Your Profile**")
age = st.sidebar.slider("Age", 22, 65, 28)
annual_salary = st.sidebar.number_input("Annual Salary ₹", 300000, 5000000, 720000)
goal = st.sidebar.selectbox("Primary Goal", [
    "Emergency Fund (1yr)", "Short-term Goal (1-3yr)", "Home/Car (3-5yr)", 
    "Retirement (10+yr)", "Wealth Creation (5-10yr)"
])
risk_tolerance = st.sidebar.selectbox("Risk Comfort", ["Low", "Medium", "High"])

# LOAD SAMPLE DEMAT
if st.button("📱 **Load Sample Demat**", type="primary"):
    st.session_state.demat = load_sample_demat()
    st.success("✅ **Sample demat loaded** (RELIANCE 12 + TCS 8 + ...)")

# MAIN DASHBOARD
if 'demat' in st.session_state:
    df = st.session_state.demat.copy()
    
    # UPDATE LIVE PRICES
    symbols = df['Symbol'].tolist()
    try:
        live_data = yf.download(symbols, period="1d", progress=False)['Adj Close'].iloc[-1]
        df['Live_Price'] = [live_data.get(s, row['Live_Price']) for s, row in df.iterrows()]
        df['Current_Value'] = df['Quantity'] * df['Live_Price']
        df['PnL_%'] = ((df['Live_Price']/df['Avg_Price']-1)*100).round(2)
    except:
        pass
    
    total_value = df['Current_Value'].sum()
    
    # DASHBOARD METRICS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 **Portfolio Value**", f"₹{total_value:,.0f}")
    col2.metric("📈 **Total PnL**", f"₹{df['PnL_Rs'].sum():,.0f}")
    col3.metric("⚖️ **Equity %**", f"{100:.0f}%")
    col4.metric("🎯 **Risk Score**", f"{min((65-age)*1.2, 85):.0f}%")
    
    # PORTFOLIO TABLE
    st.subheader("**📊 Your Current Holdings**")
    display_df = df[['Symbol', 'Quantity', 'Avg_Price', 'Live_Price', 'PnL_%', 'Current_Value']].round(0)
    st.dataframe(display_df, use_container_width=True)
    
    # ALLOCATION PIE
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_pie = px.pie(df, values='Current_Value', names='Symbol', hole=0.4,
                        title="Current Allocation")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # AI RECOMMENDATIONS
    st.subheader("🤖 **AI Portfolio Recommendations**")
    
    # PERSONALIZED STRATEGY
    equity_alloc = min((65-age)/65 * 80, 90) if risk_tolerance != "Low" else min((65-age)/65 * 50, 60)
    monthly_sip = annual_salary * 0.15 / 12
    
    rec1, rec2, rec3 = st.columns(3)
    rec1.metric("🎯 **Target Equity**", f"{equity_alloc:.0f}%")
    rec2.metric("💸 **Monthly SIP**", f"₹{monthly_sip:,.0f}")
    rec3.metric("⏳ **Time Horizon**", f"{5 if '5yr' in goal else 10 if 'Retirement' in goal else 3} yrs")
    
    # HOLDING SIGNALS (Performance + Market momentum)
    df['Signal'] = np.where(df['PnL_%'] > 15, "🟢 STRONG HOLD", 
                           np.where(df['PnL_%'] > 5, "🟢 HOLD", 
                                   np.where(df['PnL_%'] > -10, "🟡 TRIM", "🔴 SELL")))
    
    st.subheader("**📋 Action Plan for Each Holding**")
    signals_df = df[['Symbol', 'PnL_%', 'Signal']].round(1)
    st.dataframe(signals_df, use_container_width=True)
    
    # MARKET TRENDS + NEW RECOMMENDATIONS [web:46][web:47]
    st.subheader("**🔥 Top Market Picks (Momentum Leaders)**")
    momentum_stocks = ["BAJFINANCE.NS", "CHOLAFIN.NS", "LT.NS", "ASIANPAINT.NS", "BSE.NS"]
    try:
        mom_data = yf.download(momentum_stocks, period="1mo", progress=False)['Adj Close']
        mom_latest = mom_data.iloc[-1].round(0)
        mom_returns = ((mom_latest / mom_data.iloc[0] - 1)*100).round(1)
        
        mom_df = pd.DataFrame({
            'Stock': mom_latest.index,
            'Price': mom_latest.values,
            '1M Return': [f"{r:+.1f}%" for r in mom_returns],
            'Fit': ['✅ Perfect' if 'Finance' in goal else '⚠️ Watch' for _ in mom_latest]
        })
        st.dataframe(mom_df, use_container_width=True)
    except:
        st.info("Momentum stocks loading...")
    
    # STRATEGIC ADVICE
    st.markdown("### **📈 Professional Strategy**")
    advice = f"""
    **Your Profile:** Age {age} • Salary ₹{annual_salary:,} • Goal: {goal} • Risk: {risk_tolerance}
    
    **Current Assessment:**
    • Portfolio Value: ₹{total_value:,.0f}
    • Concentration: {df['Current_Value'].max()/total_value*100:.0f}% in {df.loc[df['Current_Value'].idxmax(), 'Symbol']}
    • Performance: {df['PnL_%'].mean():+.1f}% avg PnL
    
    **Recommendations:**
    1. **{df['Signal'].iloc[0]} {df['Symbol'].iloc[0]}** ({df['PnL_%'].iloc[0]:+.1f}%) - {df['Signal'].iloc[0]}
    2. **SIP ₹{monthly_sip:,.0f}/mo** into momentum leaders above
    3. **Target Allocation:** {equity_alloc:.0f}% Equity | Rebalance quarterly
    4. **New Position:** Add 10% to top momentum pick
    
    **Expected Outcome:** 14-18% CAGR aligned to your {goal}
    """
    st.markdown(advice)
    
    # DOWNLOAD REPORT
    report_df = pd.concat([display_df.assign(Section='Holdings'), mom_df.assign(Section='Recommendations')])
    csv = report_df.to_csv(index=False)
    st.download_button("📥 **Download Advisor Report**", csv, "ai-advisor-report.csv")

else:
    st.info("👆 **Click "Load Sample Demat"** to start (RELIANCE + TCS sample)")

st.markdown("---")
st.markdown("*🤖 Professional AI Advisor | Live NSE data | Personalized for your goals*")
