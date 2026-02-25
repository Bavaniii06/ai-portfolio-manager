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

# SIMULATED DEMAT
@st.cache_data(ttl=1800)
def load_sample_demat():
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

# LOAD SAMPLE
if st.button('📱 **Load Sample Demat**', type="primary"):
    st.session_state.demat = load_sample_demat()
    st.success('✅ **Sample demat loaded** (RELIANCE 12 + TCS 8 + ...)')

# MAIN ANALYSIS
if 'demat' in st.session_state:
    df = st.session_state.demat.copy()
    
    # LIVE PRICES
    symbols = df['Symbol'].tolist()
    try:
        live_data = yf.download(symbols, period="1d", progress=False)['Adj Close'].iloc[-1]
        df['Live_Price'] = [live_data.get(s, row['Live_Price']) for s, row in df.iterrows()]
        df['Current_Value'] = df['Quantity'] * df['Live_Price']
        df['PnL_%'] = ((df['Live_Price']/df['Avg_Price']-1)*100).round(2)
    except:
        pass
    
    total_value = df['Current_Value'].sum()
    
    # METRICS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 **Portfolio Value**", f"₹{total_value:,.0f}")
    col2.metric("📈 **Total PnL**", f"₹{df['PnL_Rs'].sum():,.0f}")
    col3.metric("⚖️ **Equity %**", f"{100:.0f}%")
    col4.metric("🎯 **Risk Score**", f"{min((65-age)*1.2, 85):.0f}%")
    
    # HOLDINGS TABLE
    st.subheader("**📊 Your Current Holdings**")
    display_df = df[['Symbol', 'Quantity', 'Avg_Price', 'Live_Price', 'PnL_%', 'Current_Value']].round(0)
    st.dataframe(display_df, use_container_width=True)
    
    # ALLOCATION PIE
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_pie = px.pie(df, values='Current_Value', names='Symbol', hole=0.4, title="Current Allocation")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # AI RECOMMENDATIONS
    st.subheader("🤖 **AI Portfolio Recommendations**")
    
    equity_alloc = min((65-age)/65 * 80, 90) if risk_tolerance != "Low" else min((65-age)/65 * 50, 60)
    monthly_sip = annual_salary * 0.15 / 12
    
    rec1, rec2, rec3 = st.columns(3)
    rec1.metric("🎯 **Target Equity**", f"{equity_alloc:.0f}%")
    rec2.metric("💸 **Monthly SIP**", f"₹{monthly_sip:,.0f}")
    rec3.metric("⏳ **Time Horizon**", f"{5 if '5yr' in goal else 10 if 'Retirement' in goal else 3} yrs")
    
    # SIGNALS
    df['Signal'] = np.where(df['PnL_%'] > 15, "🟢 STRONG HOLD", 
                           np.where(df['PnL_%'] > 5, "🟢 HOLD", 
                                   np.where(df['PnL_%'] > -10, "🟡 TRIM", "🔴 SELL")))
    
    st.subheader("**📋 Action Plan**")
    signals_df = df[['Symbol', 'PnL_%', 'Signal']].round(1)
    st.dataframe(signals_df, use_container_width=True)
    
    # MOMENTUM PICKS
    st.subheader("**🔥 Top Market Picks**")
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
    
    # STRATEGY ADVICE
    st.markdown("### **📈 Professional Strategy**")
    advice = f"""
    **Your Profile:** Age {age} • Salary ₹{annual_salary:,}/yr • Goal: {goal} • Risk: {risk_tolerance}
    
    **Portfolio Health:**
    • Value: ₹{total_value:,.0f} | Concentration: {df['Current_Value'].max()/total_value*100:.0f}%
    • Performance: {df['PnL_%'].mean():+.1f}% avg PnL
    
    **Immediate Actions:**
    """
    st.markdown(advice)
    
    for _, row in df.iterrows():
        st.markdown(f"• **{row['Signal']}** {row['Symbol']} ({row['PnL_%']:+.1f}%)")
    
    st.markdown(f"""
    **Next Steps:**
    1. SIP ₹{monthly_sip:,.0f}/month in top momentum picks
    2. Target: {equity_alloc:.0f}% Equity allocation
    3. Rebalance quarterly when >5% deviation
    4. **Expected:** 14-18% CAGR for your {goal}
    """)
    
    # DOWNLOAD
    report_df = pd.concat([display_df.assign(Section='Holdings'), mom_df.assign(Section='Recommendations') if 'mom_df' in locals() else pd.DataFrame()])
    csv = report_df.to_csv(index=False)
    st.download_button("📥 **Download Report**", csv, "ai-advisor-report.csv")

else:
    st.info('👆 **Click "Load Sample Demat"** to start (RELIANCE + TCS sample)')

st.markdown("---")
st.markdown("*🤖 Professional AI Advisor | Live NSE | Goal-based portfolio management*")
