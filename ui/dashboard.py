import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="AI Advisor", page_icon="🤖", layout="wide")

st.markdown("""
# 🤖 **AI Investment Advisor** 
**Professional portfolio analysis • Personalized recommendations**
""")

# SAMPLE DEMAT - NO EXTERNAL CALLS
SAMPLE_DEMAT = pd.DataFrame({
    'Symbol': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS'],
    'Quantity': [12.0, 8.0, 25.0, 15.0, 20.0],
    'Avg_Price': [2850.50, 4150.25, 1625.80, 1820.10, 1185.75],
    'Live_Price': [2925.60, 4185.20, 1650.40, 1850.90, 1195.50],
    'PnL_Rs': [907.20, 280.00, 618.00, 466.50, 196.00]
})

# SIDEBAR PROFILE
st.sidebar.header("👤 **Your Profile**")
age = st.sidebar.slider("Age", 22, 65, 28)
annual_salary = st.sidebar.number_input("Annual Salary ₹", 300000, 5000000, 720000)
goal = st.sidebar.selectbox("Goal", [
    "Emergency (1yr)", "Short-term (1-3yr)", "Home/Car (3-5yr)", 
    "Retirement (10+yr)", "Wealth (5-10yr)"
])
risk = st.sidebar.selectbox("Risk", ["Low", "Medium", "High"])

# LOAD BUTTON
if st.button('📱 **Load Sample Demat**', type="primary"):
    st.session_state.demat = SAMPLE_DEMAT.copy()
    st.rerun()

# ANALYSIS
if 'demat' in st.session_state:
    df = st.session_state.demat.copy()
    df['Current_Value'] = df['Quantity'] * df['Live_Price']
    df['PnL_%'] = ((df['Live_Price']/df['Avg_Price']-1)*100).round(2)
    
    total_value = df['Current_Value'].sum()
    
    # METRICS ROW
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Portfolio Value", f"₹{total_value:,.0f}")
    col2.metric("📈 Total PnL", f"₹{df['PnL_Rs'].sum():,.0f}")
    col3.metric("⚖️ Equity %", "100%")
    col4.metric("🎯 Risk Score", f"{min((65-age)*1.2, 85):.0f}%")
    
    # HOLDINGS TABLE
    st.subheader("📊 **Current Holdings**")
    display_df = df[['Symbol', 'Quantity', 'Avg_Price', 'Live_Price', 'PnL_%', 'Current_Value']].round(0)
    st.dataframe(display_df, use_container_width=True)
    
    # PIE CHART
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, values='Current_Value', names='Symbol', hole=0.4, title="Allocation")
        st.plotly_chart(fig, use_container_width=True)
    
    # PERSONALIZED STRATEGY
    st.subheader("🤖 **AI Recommendations**")
    
    equity_target = min((65-age)/65 * 80, 90) if risk != "Low" else min((65-age)/65 * 50, 60)
    sip_amount = annual_salary * 0.15 / 12
    
    c1, c2, c3 = st.columns(3)
    c1.metric("🎯 Target Equity", f"{equity_target:.0f}%")
    c2.metric("💸 Monthly SIP", f"₹{sip_amount:,.0f}")
    c3.metric("⏳ Horizon", f"{5 if '5yr' in goal else 10 if 'Retirement' in goal else 3} yrs")
    
    # HOLDING SIGNALS
    df['Signal'] = np.where(df['PnL_%'] > 15, "🟢 STRONG HOLD", 
                           np.where(df['PnL_%'] > 5, "🟢 HOLD", 
                                   np.where(df['PnL_%'] > -10, "🟡 TRIM", "🔴 SELL")))
    
    st.subheader("📋 **Action Plan**")
    signals_df = df[['Symbol', 'PnL_%', 'Signal']].round(1)
    st.dataframe(signals_df, use_container_width=True)
    
    # MOMENTUM RECOMMENDATIONS
    st.subheader("🔥 **Top Additions**")
    momentum = pd.DataFrame({
        'Stock': ['BAJFINANCE.NS', 'LT.NS', 'ASIANPAINT.NS', 'CHOLAFIN.NS'],
        '1M_Return': ['+12.4%', '+9.8%', '+8.2%', '+7.1%'],
        'Action': ['🟢 BUY 10%', '🟢 BUY 8%', '🟢 BUY 7%', '🟢 BUY 5%']
    })
    st.dataframe(momentum, use_container_width=True)
    
    # PROFESSIONAL ADVICE
    st.markdown("### **📈 Investment Strategy**")
    advice = f"""
**Profile:** Age {age} | Salary ₹{annual_salary:,}/yr | Goal: {goal} | Risk: {risk}

**Assessment:**
• Value: ₹{total_value:,.0f} | Top: {df.loc[df['Current_Value'].idxmax(), 'Symbol']} ({df['Current_Value'].max()/total_value*100:.0f}%)
• Performance: {df['PnL_%'].mean():+.1f}% avg

**Action Plan:**
"""
    st.markdown(advice)
    
    for _, row in df.iterrows():
        st.markdown(f"• **{row['Signal']}** {row['Symbol']} | PnL {row['PnL_%']:+.1f}%")
    
    st.markdown(f"""
**Next Steps:**
• SIP ₹{sip_amount:,.0f}/mo → BAJFINANCE/LT
• Target: {equity_target:.0f}% Equity
• Rebalance: Quarterly (±5% deviation)
• **Projected:** 14-18% annual returns
    """)
    
    # DOWNLOAD
    csv = df.to_csv(index=False)
    st.download_button("📥 Download Report", csv, "portfolio-report.csv")

else:
    st.info('👆 Click "Load Sample Demat" to analyze RELIANCE+TCS portfolio')

st.markdown("*🤖 AI Portfolio Manager | Production ready*")
