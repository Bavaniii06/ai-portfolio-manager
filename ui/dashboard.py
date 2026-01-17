import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher import StockData
from core.risk_engine import RiskAnalyzer
from core.portfolio import PortfolioAnalyzer
from core.rebalancer import Rebalancer

st.set_page_config(page_title="AI Portfolio Manager", layout="wide")

def main():
    st.title("🚀 AI Portfolio Management System")
    st.markdown("---")
    
    # Sidebar inputs
    st.sidebar.header("📈 Portfolio Settings")
    tickers = st.sidebar.text_input("Stocks (comma sep)", "RELIANCE.NS,TCS.NS,AAPL").split(',')
    shares = {
        tickers[0]: st.sidebar.number_input("Shares "+tickers[0], 0, 1000, 10),
        tickers[1]: st.sidebar.number_input("Shares "+tickers[1], 0, 1000, 15),
        tickers[2]: st.sidebar.number_input("Shares "+tickers[2], 0, 1000, 5)
    }
    
    if st.button("🔥 ANALYZE PORTFOLIO", type="primary"):
        with st.spinner("AI Analysis in progress..."):
            # Get live data
            portfolio = StockData(tickers)
            prices, returns = portfolio.fetch_live()
            
            # Risk analysis
            risk_analyzer = RiskAnalyzer(prices, returns)
            risk_table = risk_analyzer.calculate_metrics()
            
            # Portfolio analysis  
            port_analyzer = PortfolioAnalyzer()
            port_analyzer.shares = shares  # Dynamic shares
            summary, total_value, over, under = port_analyzer.analyze()
            
            # Rebalancing
            rebalancer = Rebalancer()
            rebalancer.portfolio.shares = shares
            _, current_alloc = rebalancer.analyze_allocation()
            signals = rebalancer.generate_signals(current_alloc)
     
     # Add to dashboard.py (after ANALYZE button)
    if st.button("🔄 REFRESH LIVE DATA"):
        st.cache_data.clear()  # Force fresh NSE data
        st.rerun()  # Reload dashboard with new prices

        # Dashboard Layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("💰 Total Value", f"₹{total_value:,.2f}")
            st.metric("⚠️ Over-allocated", len(over))
            st.metric("📈 Under-allocated", len(under))
            st.metric("🔄 Trades Needed", len(signals[signals['Action'] != '🟡 HOLD']))
        
        with col2:
            fig_pie = px.pie(summary, values='Value', names=summary.index, 
                           title="Current Allocation")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Risk Heatmap
        st.subheader("📊 Risk Analysis")
        fig_risk = px.bar(risk_table, x=risk_table.index, y='Volatility (%)',
                         color='Risk Level', title="Risk Profile")
        st.plotly_chart(fig_risk, use_container_width=True)
        
        # Rebalancing Signals
        st.subheader("⚖️ Rebalancing Recommendations")
        st.dataframe(signals.style.highlight_max(axis=0), use_container_width=True)
        
        # Live Price Chart
        st.subheader("📈 Live Prices (5-min)")
        fig_price = go.Figure()
        for ticker in tickers:
            fig_price.add_trace(go.Scatter(x=[pd.Timestamp.now()], y=[prices[ticker]],
                                         mode='markers+text', name=ticker,
                                         text=[f"₹{prices[ticker]:.2f}"]))
        st.plotly_chart(fig_price, use_container_width=True)

if __name__ == "__main__":
    main()
