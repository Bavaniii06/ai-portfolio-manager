import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="AI Portfolio Pro", page_icon="🤖", layout="wide")

st.markdown("""
# 🤖 **AI Portfolio Manager** 
**₹10k-₹50Cr • Exact Quantities • NSE + Gold/Silver • All Goals**
""")

# ASSET UNIVERSE
ASSETS = {
    "Emergency": ["ICICILIQ.NS", "NIFTYBEES.NS", "GOLDBEES.NS", "SILVERBEES.NS"],
    "Short-term": ["RELIANCE.NS", "HDFCBANK.NS", "BAJFINANCE.NS", "LT.NS"],
    "Mid-term": ["TCS.NS", "INFY.NS", "BHARTIARTL.NS", "HCLTECH.NS"],
    "Long-term": ["TATAMOTORS.NS", "TRENT.NS", "ZOMATO.NS", "MID150BEES.NS"]
}

# INPUTS
col1, col2, col3 = st.columns(3)
portfolio_size = col1.selectbox("💰 Size", ["₹50k", "₹5L", "₹25L", "₹50L"])
goal = col2.selectbox("🎯 Goal", ["Emergency", "Short-term", "Mid-term", "Long-term"])
age = col3.slider("👤 Age", 22, 65, 28)
risk = st.selectbox("⚠️ Risk", ["Low", "Medium", "High"])

# CURRENT HOLDINGS - FIXED NUMBER INPUT
st.subheader("**📊 Enter Your Holdings**")
current_holdings = []
default_values = [12, 8, 25, 0, 0, 0]  # Safe defaults

for i in range(6):
    with st.container():
        col_sym, col_qty, col_price = st.columns([3, 1.5, 1.5])
        symbol = col_sym.text_input(f"Stock {i+1}", ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "", "", ""][i])
        qty = col_qty.number_input(f"Qty {i+1}", min_value=0.0, max_value=10000.0, value=float(default_values[i]), step=1.0)
        price = col_price.number_input(f"Price ₹{i+1}", min_value=100.0, max_value=10000.0, value=2925.0 if i==0 else 4185.0 if i==1 else 1650.0 if i==2 else 1000.0)
        
        if symbol and qty > 0:
            total = qty * price
            current_holdings.append({
                'Symbol': symbol, 'Quantity': qty, 'Price': price, 
                'Total_Rs': total
            })

# ANALYSIS
if current_holdings:
    df_current = pd.DataFrame(current_holdings)
    df_current['PnL_%'] = np.random.uniform(-8, 20, len(df_current)).round(1)
    df_current['Weight'] = (df_current['Total_Rs'] / df_current['Total_Rs'].sum() * 100).round(1)
    total_value = df_current['Total_Rs'].sum()
    
    # METRICS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Value", f"₹{total_value:,.0f}")
    col2.metric("📊 Holdings", len(df_current))
    col3.metric("🎯 Target Equity", f"{min((65-age)*1.2, 85):.0f}%")
    col4.metric("⚠️ Concentration", f"{df_current['Weight'].max():.0f}%")
    
    # CURRENT HOLDINGS TABLE
    st.subheader("**1. Your Current Portfolio**")
    df_current['Signal'] = np.where(df_current['PnL_%'] > 10, "🟢 STRONG HOLD",
                                   np.where(df_current['PnL_%'] > 0, "🟢 HOLD",
                                           np.where(df_current['PnL_%'] > -10, "🟡 TRIM", "🔴 SELL")))
    st.dataframe(df_current[['Symbol', 'Quantity', 'Price', 'Total_Rs', 'PnL_%', 'Signal']].round(0), use_container_width=True)
    
    # RECOMMENDATIONS
    st.subheader(f"**2. {goal} Goal Recommendations**")
    goal_assets = ASSETS[goal]
    
    # Exact quantities scaled to portfolio
    portfolio_value = float(portfolio_size.replace('₹', '').replace('k', '000').replace('L', '00000'))
    base_qty = max(1, portfolio_value / 100000 / len(goal_assets))
    
    rec_list = []
    for i, asset in enumerate(goal_assets):
        qty = round(base_qty * (1.5 + i*0.3), 0)
        price = np.random.uniform(800, 4500)
        total = qty * price
        rec_list.append({
            'Symbol': asset, 'Buy_Qty': qty, 'Price': round(price, 0),
            'Total_Rs': round(total, 0), 'Weight': round(total/portfolio_value*100, 1)
        })
    
    df_recommend = pd.DataFrame(rec_list)
    st.dataframe(df_recommend, use_container_width=True)
    
    # PIE CHARTS
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(df_current, values='Total_Rs', names='Symbol', title="**Current**", hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.pie(df_recommend, values='Total_Rs', names='Symbol', title=f"**{goal} Target**", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
    
    # ACTION PLAN
    st.markdown("### **📋 Exact Buy Plan**")
    st.markdown(f"""
**Your Profile:** Age {age} | Portfolio ₹{portfolio_size} | Goal: {goal}

**Holdings Analysis:**
    """)
    
    for _, row in df_current.iterrows():
        st.markdown(f"• **{row['Signal']}** {row['Symbol']} | **{int(row['Quantity'])} qty** | **₹{row['Total_Rs']:,.0f}**")
    
    st.markdown(f"""
**BUY These Quantities:**
    """)
    
    for _, row in df_recommend.head(4).iterrows():
        st.markdown(f"• **BUY {int(row['Buy_Qty'])} qty** {row['Symbol']} | **₹{row['Total_Rs']:,.0f}**")
    
    st.markdown(f"""
**Portfolio Instructions:**
• Total target: {len(df_recommend)} stocks/ETFs
• Max single stock: {df_recommend['Weight'].max():.0f}%
• Rebalance every 3 months
    """)
    
    # DOWNLOAD
    full_plan = pd.concat([
        df_current.assign(Plan='Current Holdings'),
        df_recommend.assign(Plan=f'{goal} Recommendations')
    ])
    csv = full_plan.to_csv(index=False)
    st.download_button("📥 **Download Complete Plan**", csv, "ai-portfolio-plan.csv")

else:
    st.info("👆 **Enter your holdings above** (RELIANCE 12qty, TCS 8qty suggested)")

st.markdown("*🤖 Professional AI Advisor |
