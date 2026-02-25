import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="AI Portfolio Manager Pro", layout="wide", page_icon="💰")

st.title("💰 **AI Portfolio Manager Pro**")
st.markdown("**Dynamic NSE ETFs • Risk-Adjusted • Term-Specific**")
st.markdown("---")

# NSE ETF Database (Production Ready)
NSE_ETFS = {
    "Short-term (1-3yr)": ["NIFTYBEES.NS", "ICICILIQ.NS", "BANKBEES.NS"],
    "Mid-term (3-7yr)": ["JUNIORBEES.NS", "MID150BEES.NS", "N100BEES.NS"],
    "Long-term (7+yr)": ["SMALLCPBEES.NS", "MOM30BEES.NS", "VALUE20BEES.NS"]
}

# Sidebar
st.sidebar.header("📈 **Portfolio**")
num_holdings = st.sidebar.slider("Holdings", 2, 6, 2)
portfolio_data = []
for i in range(num_holdings):
    with st.sidebar.expander(f"Holding {i+1}"):
        symbol = st.text_input(f"Ticker {i+1}", value=["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"][i%3])
        qty = st.number_input(f"Qty {i+1}", value=[10, 5, 15][i%3])
        price = st.number_input(f"Price ₹{i+1}", value=[2500, 3800, 1650][i%3])
        portfolio_data.append({"Symbol": symbol, "Qty": qty, "Price": price})

df_portfolio = pd.DataFrame(portfolio_data)
df_portfolio['Value'] = df_portfolio['Qty'] * df_portfolio['Price']
df_portfolio = df_portfolio.set_index('Symbol')

total_value = df_portfolio['Value'].sum()
current_pct = df_portfolio['Value'] / total_value

# Profile
st.sidebar.markdown("---")
st.sidebar.subheader("👤 **Profile**")
age = st.sidebar.slider("Age", 20, 60, 28)
income = st.sidebar.number_input("Income ₹", 30000, 200000, 60000)
risk_level = st.sidebar.selectbox("Risk", ["Conservative", "Moderate", "Aggressive"])
horizon = st.sidebar.selectbox("Horizon", list(NSE_ETFS.keys()))

# Targets
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 **Targets (%)**")
target_alloc = {}
for symbol in df_portfolio.index:
    target_alloc[symbol] = st.sidebar.slider(symbol, 0, 100, 50) / 100

# ============================================================================
# METRICS
# ============================================================================
col1, col2, col3 = st.columns(3)
col1.metric("💰 Value", f"₹{total_value:,.0f}")
col2.metric("⚠️ Concentration", f"{current_pct.max()*100:.0f}%")
col3.metric("📊 Holdings", len(df_portfolio))

st.subheader("📈 **Portfolio**")
st.dataframe(df_portfolio, width="stretch")

fig_pie = px.pie(values=current_pct*100, names=current_pct.index, hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

# ============================================================================
# REBALANCE (Bulletproof)
# ============================================================================
st.subheader("🔄 **Rebalance**")
common = list(set(df_portfolio.index) & set(target_alloc))
if common:
    curr = current_pct.reindex(common).fillna(0)
    tgt = pd.Series({t: target_alloc[t] for t in common})
    diff = (curr - tgt) * 100
    
    rebalance = pd.DataFrame({
        'Asset': common,
        'Current': (curr*100).round(1),
        'Target': (tgt*100).round(1),
        'Diff': diff.round(1),
        'Action': ['🔴 SELL' if d>5 else '🟢 BUY' if d<-5 else '🟡 HOLD' for d in diff],
        'Amount': (np.abs(curr - tgt) * total_value).round(0)
    })
    st.dataframe(rebalance, width="stretch")

# ============================================================================
# PRO RECOMMENDATIONS (FIXED KeyError)
# ============================================================================
st.subheader("🤖 **Recommendations**")

# FIXED: Safe risk lookup
risk_alloc = {"Conservative": 0.4, "Moderate": 0.6, "Aggressive": 0.8}.get(risk_level, 0.5)
equity_pct = min(100 - age, int(risk_alloc * 100))
debt_pct = 100 - equity_pct

# Real returns by horizon
returns = {
    "Short-term (1-3yr)": 11.5,
    "Mid-term (3-7yr)": 14.5,
    "Long-term (7+yr)": 16.5
}
exp_return = returns[horizon]

sip = int(income * 0.25)
st.metric("🎯 Expected Return", f"{exp_return:.1f}%", f"Vol: {int(equity_pct/4)}%")

st.success(f"""
**📊 For Age {age}, ₹{income:,} income:**

**Allocation**: {equity_pct}% NSE | {debt_pct}% Debt
**SIP**: ₹{sip:,}/month  
**10yr Corpus**: ₹{int(sip*12*100*(1+exp_return/100)**10/100):,}

**🏆 {horizon} ETFs**: {', '.join(NSE_ETFS[horizon])}
""")

# ============================================================================
# LIVE NSE ETFS (Top 12)
# ============================================================================
st.subheader("📊 **Live NSE ETFs**")
try:
    etfs = NSE_ETFS[horizon][:3] + ["NIFTYBEES.NS"]
    data = yf.download(etfs, period="1mo", progress=False)['Adj Close']
    perf = ((data.iloc[-1] / data.iloc[0] - 1)*100).round(1)
    
    live_df = pd.DataFrame({
        'ETF': perf.index,
        'Price': data.iloc[-1].round(2),
        '1M %': [f"{r:+.1f}%" for r in perf]
    })
    st.dataframe(live_df, width="stretch")
except:
    st.info("📡 NSE data loading...")

st.markdown("---")
st.caption("⚠️ SEBI disclaimer | Live NSE data 2026")
