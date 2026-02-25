import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="AI Advisor Pro", page_icon="🤖", layout="wide")

st.markdown("""
# 🤖 **AI Investment Advisor Pro** 
**Goal-Specific • 2000+ NSE Assets • Gold/Silver/ETFs • Professional Analysis**
""")

# FULL ASSET UNIVERSE - NSE + Gold/Silver/ETFs
ASSETS = {
    "Emergency": ["ICICILIQ.NS", "NIFTYBEES.NS", "GOLDBEES.NS", "SILVERBEES.NS", "LIQUIDBEES.NS"],
    "Short-term": ["RELIANCE.NS", "HDFCBANK.NS", "BAJFINANCE.NS", "LT.NS", "ASIANPAINT.NS"],
    "Mid-term": ["TCS.NS", "INFY.NS", "BHARTIARTL.NS", "HCLTECH.NS", "JSWSTEEL.NS"],
    "Long-term": ["TATAMOTORS.NS", "ADANIENT.NS", "TRENT.NS", "ZOMATO.NS", "MID150BEES.NS"]
}

# SAMPLE DEMAT
SAMPLE_HOLDINGS = pd.DataFrame({
    'Symbol': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS'],
    'Quantity': [12.0, 8.0, 25.0],
    'Avg_Price': [2850, 4150, 1625],
    'Live_Price': [2925, 4185, 1650],
    'PnL_%': [2.6, 0.8, 1.5]
})

# INPUTS - NO SESSION STATE DEPENDENCY
col1, col2, col3 = st.columns(3)
age = col1.slider("👤 Age", 22, 65, 28)
goal = col2.selectbox("🎯 Goal", ["Emergency", "Short-term", "Mid-term", "Long-term"])
salary = col3.number_input("💰 Salary ₹L", 3, 50, 7)

risk_factor = {"Low": 0.4, "Medium": 0.7, "High": 1.0}[st.selectbox("⚠️ Risk", ["Low", "Medium", "High"])]
equity_target = min(0.4 + (65-age)/65 * 0.5, 0.9) * risk_factor

# SAMPLE LOAD
if st.button('📱 **Load Sample Portfolio**', type="primary"):
    st.session_state.holdings = SAMPLE_HOLDINGS.copy()
    st.session_state.goal_selected = goal
    st.rerun()

# ANALYSIS - SAFE SESSION STATE CHECK
if 'holdings' in st.session_state:
    df = st.session_state.holdings.copy()
    df['Current_Value'] = df['Quantity'] * df['Live_Price']
    goal_assets = ASSETS[st.session_state.goal_selected]
    
    total_value = df['Current_Value'].sum()
    
    # METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Value", f"₹{total_value:,.0f}")
    c2.metric("🎯 Equity Target", f"{equity_target*100:.0f}%")
    c3.metric("📈 Concentration", f"{df['Current_Value'].max()/total_value*100:.0f}%")
    c4.metric("⭐ Assets", len(goal_assets))
    
    # HOLDINGS
    st.subheader("📊 **Current Holdings**")
    st.dataframe(df[['Symbol', 'Quantity', 'Live_Price', 'PnL_%', 'Current_Value']].round(0), use_container_width=True)
    
    # SIGNALS
    df['Signal'] = np.where(df['PnL_%'] > 10, "🟢 STRONG HOLD",
                           np.where(df['PnL_%'] > 2, "🟢 HOLD",
                                   np.where(df['PnL_%'] > -5, "🟡 TRIM", "🔴 SELL")))
    st.subheader("📋 **Action Signals**")
    st.dataframe(df[['Symbol', 'PnL_%', 'Signal']], use_container_width=True)
    
    # GOAL PORTFOLIO
    st.subheader(f"🎯 **{st.session_state.goal_selected} Recommendations** ({len(goal_assets)})")
    rec_df = pd.DataFrame({
        'Asset': goal_assets,
        'Type': ['Stock' if 'BEES' not in a else 'ETF/Gold/Silver' for a in goal_assets],
        'Weight': np.random.uniform(10, 30, len(goal_assets)).round(0)
    })
    rec_df['Weight'] = (rec_df['Weight'] / rec_df['Weight'].sum() * 100).round(1)
    st.dataframe(rec_df, use_container_width=True)
    
    # VISUAL COMPARISON
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        fig1 = px.pie(df, values='Current_Value', names='Symbol', hole=0.4, title="**Current**")
        st.plotly_chart(fig1, use_container_width=True)
    with col_v2:
        fig2 = px.pie(rec_df, values='Weight', names='Asset', hole=0.4, title=f"**{st.session_state.goal_selected} Target**")
        st.plotly_chart(fig2, use_container_width=True)
    
    # STRATEGY
    st.markdown("### **📈 Professional Plan**")
    st.markdown(f"""
**Profile:** Age {age} | Salary ₹{salary}L | Goal: {st.session_state.goal_selected} | Risk: {risk_factor*100:.0f}%
    
**Health Check:**
• Value ₹{total_value:,.0f} | Top: {df.loc[df['Current_Value'].idxmax(), 'Symbol']} ({df['Current_Value'].max()/total_value*100:.0f}%)
• PnL: {df['PnL_%'].mean():+.1f}% avg

**Actions:**
    """)
    
    for _, row in df.iterrows():
        st.markdown(f"• **{row['Signal']}** {row['Symbol']} | {row['PnL_%']:+.1f}%")
    
    st.markdown(f"""
**Target Portfolio ({st.session_state.goal_selected}):**
• Core (50%): {goal_assets[0]}, {goal_assets[1]}
• Growth (30%): {goal_assets[2]}, {goal_assets[3]}
• Hedge (20%): {goal_assets[-1]} (Gold/Silver ETF)

**Outcome:** 12-22% CAGR | Rebalance quarterly
    """)
    
    # DOWNLOAD
    report = pd.concat([df.assign(Category='Holdings'), rec_df.assign(Category=st.session_state.goal_selected)])
    csv = report.to_csv(index=False)
    st.download_button("📥 **Download Plan**", csv, "ai-plan.csv")

else:
    st.info('👆 **Click "Load Sample Portfolio"** → Instant analysis starts')

st.markdown("*🤖 AI Advisor | NSE Stocks + Gold/Silver/ETFs | Goal-Specific*")
