import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher import StockData
from core.risk_engine import RiskAnalyzer

class PortfolioAnalyzer:
    def __init__(self):
        self.shares = {'RELIANCE.NS': 10, 'TCS.NS': 15, 'AAPL': 5}  # Your holdings
        self.prices = None
        self.risk_data = None
    
    def analyze(self):
        """Complete portfolio health check"""
        # Get live data
        portfolio = StockData(['RELIANCE.NS', 'TCS.NS', 'AAPL'])
        prices, returns = portfolio.fetch_live()
        self.prices = prices
        
        # Risk analysis
        analyzer = RiskAnalyzer(prices, returns)
        self.risk_data = analyzer.calculate_metrics()
        
        # Portfolio calculations
        values = pd.Series(self.shares) * prices
        total_value = values.sum()
        allocation = (values / total_value * 100).round(2)
        
        # Health check
        over_allocated = allocation[allocation > 30]
        under_allocated = allocation[allocation < 10]
        
        summary = pd.DataFrame({
            'Shares': pd.Series(self.shares),
            'Price': prices.round(2),
            'Value': values.round(2),
            'Allocation %': allocation,
            'Risk': self.risk_data['Risk Level']
        })
        
        return summary, total_value, over_allocated, under_allocated
    
    def health_report(self, summary, total_value, over, under):
        print(f"\n💰 TOTAL PORTFOLIO VALUE: ₹{total_value:,.2f}")
        print(f"\n📋 PORTFOLIO SUMMARY:")
        print("=" * 60)
        print(summary)
        print(f"\n⚠️  OVER-ALLOCATED (>30%): {len(over)} stocks")
        if len(over) > 0:
            print(over)
        print(f"📈 UNDER-ALLOCATED (<10%): {len(under)} stocks") 
        if len(under) > 0:
            print(under)

# TEST DAY 3
if __name__ == "__main__":
    print("💼 PORTFOLIO ANALYSIS DAY 3\n")
    analyzer = PortfolioAnalyzer()
    summary, total, over, under = analyzer.analyze()
    analyzer.health_report(summary, total, over, under)
